#!/usr/bin/env python3
"""ROS 2 node that displays camera images and overlays PointStamped data."""

from __future__ import annotations

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from ros_image_codec import image_msg_to_bgr8
from sensor_msgs.msg import Image


class CameraPointCvSubscriber(Node):
    def __init__(self) -> None:
        super().__init__("camera_point_cv_subscriber")

        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("point_topic", "/camera/object_point")
        self.declare_parameter("show_point_overlay", True)
        self.declare_parameter("enable_click_scan", True)
        self.declare_parameter("scale_px_per_meter", 80.0)
        self.declare_parameter("processing_mode", "none")
        self.declare_parameter("canny_low", 80)
        self.declare_parameter("canny_high", 160)
        self.declare_parameter("min_target_area", 350.0)
        self.declare_parameter("auto_publish_detected_point", False)
        self.declare_parameter("auto_publish_hz", 8.0)
        self.declare_parameter("render_hz", 60.0)

        self.image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        self.point_topic = self.get_parameter("point_topic").get_parameter_value().string_value
        self.show_point_overlay = (
            self.get_parameter("show_point_overlay").get_parameter_value().bool_value
        )
        self.enable_click_scan = (
            self.get_parameter("enable_click_scan").get_parameter_value().bool_value
        )
        self.processing_mode = (
            self.get_parameter("processing_mode").get_parameter_value().string_value.lower().strip()
        )
        self.canny_low = self.get_parameter("canny_low").get_parameter_value().integer_value
        self.canny_high = self.get_parameter("canny_high").get_parameter_value().integer_value
        self.min_target_area = (
            self.get_parameter("min_target_area").get_parameter_value().double_value
        )
        self.auto_publish_detected_point = (
            self.get_parameter("auto_publish_detected_point").get_parameter_value().bool_value
        )
        self.auto_publish_hz = (
            self.get_parameter("auto_publish_hz").get_parameter_value().double_value
        )
        self.render_hz = self.get_parameter("render_hz").get_parameter_value().double_value

        self.window_name = "Camera Viewer (press q to quit)"
        self.width = 960
        self.height = 720
        self.scale_px_per_meter = (
            self.get_parameter("scale_px_per_meter").get_parameter_value().double_value
        )
        if self.scale_px_per_meter <= 0.0:
            self.scale_px_per_meter = 80.0
        if self.canny_low < 0:
            self.canny_low = 0
        if self.canny_high <= self.canny_low:
            self.canny_high = self.canny_low + 1
        if self.min_target_area <= 0.0:
            self.min_target_area = 350.0
        if self.auto_publish_hz <= 0.0:
            self.auto_publish_hz = 8.0
        if self.render_hz <= 0.0:
            self.render_hz = 60.0

        self.latest_image: np.ndarray | None = None
        self.latest_image_msg: Image | None = None
        self.latest_point_msg: PointStamped | None = None
        self.last_clicked_pixel: tuple[int, int] | None = None
        self.last_detected_pixel: tuple[int, int] | None = None
        self.last_detected_area: float = 0.0
        self.processing_mode_warned = False
        self.last_auto_publish_time = self.get_clock().now()
        self.last_log_time = self.get_clock().now()

        image_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
        )
        self.image_subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            image_qos,
        )
        self.point_subscription = self.create_subscription(
            PointStamped,
            self.point_topic,
            self.point_callback,
            10,
        )
        self.point_publisher = self.create_publisher(PointStamped, self.point_topic, 10)
        self.timer = self.create_timer(1.0 / self.render_hz, self.render_frame)

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        if self.enable_click_scan:
            cv2.setMouseCallback(self.window_name, self.on_mouse_event)

        self.get_logger().info(f"Subscribed image topic: {self.image_topic}")
        self.get_logger().info(f"Subscribed point topic: {self.point_topic}")
        self.get_logger().info(f"Render refresh rate: {self.render_hz:.2f} Hz")
        self.get_logger().info(f"Processing mode: {self.processing_mode}")
        if self.enable_click_scan:
            self.get_logger().info(
                "Click-scan enabled: left-click image to publish /camera/object_point."
            )
        if self.auto_publish_detected_point:
            self.get_logger().info(
                f"Auto point publish enabled at <= {self.auto_publish_hz:.2f} Hz"
            )
        self.get_logger().info("Press 'q' in OpenCV window to quit.")

    def image_callback(self, msg: Image) -> None:
        try:
            raw_frame = image_msg_to_bgr8(msg)
            processed_frame = self._process_frame(raw_frame)
            self.latest_image = processed_frame
            self.latest_image_msg = msg
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warning(f"Failed to convert image message: {exc}")

    def point_callback(self, msg: PointStamped) -> None:
        self.latest_point_msg = msg

        now = self.get_clock().now()
        if (now - self.last_log_time).nanoseconds > 1_000_000_000:
            self.last_log_time = now
            self.get_logger().info(
                f"Latest point in {msg.header.frame_id or 'unknown'}: "
                f"x={msg.point.x:.3f}, y={msg.point.y:.3f}, z={msg.point.z:.3f}"
            )

    def on_mouse_event(self, event: int, x: int, y: int, flags: int, param: object) -> None:
        del flags, param

        if not self.enable_click_scan or event != cv2.EVENT_LBUTTONDOWN:
            return

        if self.latest_image is None:
            return

        self.last_clicked_pixel = (int(x), int(y))
        self._publish_point_from_pixel(int(x), int(y), source="click")

    def _point_from_pixel(self, x: int, y: int) -> PointStamped:
        h, w = self.latest_image.shape[:2]
        x_m = (float(x) - (w / 2.0)) / self.scale_px_per_meter
        y_m = ((h / 2.0) - float(y)) / self.scale_px_per_meter

        frame_id = "camera_frame"
        if self.latest_image_msg is not None and self.latest_image_msg.header.frame_id:
            frame_id = self.latest_image_msg.header.frame_id

        point_msg = PointStamped()
        point_msg.header.stamp = self.get_clock().now().to_msg()
        point_msg.header.frame_id = frame_id
        point_msg.point.x = float(x_m)
        point_msg.point.y = float(y_m)
        point_msg.point.z = 0.0
        return point_msg

    def _publish_point_from_pixel(self, x: int, y: int, source: str) -> None:
        if self.latest_image is None:
            return

        if source == "auto":
            dt_ns = (self.get_clock().now() - self.last_auto_publish_time).nanoseconds
            min_interval_ns = int((1.0 / self.auto_publish_hz) * 1e9)
            if dt_ns < min_interval_ns:
                return

        point_msg = self._point_from_pixel(x, y)
        self.point_publisher.publish(point_msg)
        self.latest_point_msg = point_msg

        if source == "auto":
            self.last_auto_publish_time = self.get_clock().now()
            return

        self.get_logger().info(
            f"Clicked pixel=({x},{y}) -> point x={point_msg.point.x:+.3f}m "
            f"y={point_msg.point.y:+.3f}m z={point_msg.point.z:+.3f}m"
        )

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        mode = self.processing_mode

        if mode in ("", "none"):
            self.last_detected_pixel = None
            self.last_detected_area = 0.0
            return frame

        if mode == "gray":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.last_detected_pixel = None
            self.last_detected_area = 0.0
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        if mode == "canny":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, int(self.canny_low), int(self.canny_high))
            self.last_detected_pixel = None
            self.last_detected_area = 0.0
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        if mode in ("red-target", "red_track", "red"):
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_red_1 = np.array([0, 100, 80], dtype=np.uint8)
            upper_red_1 = np.array([10, 255, 255], dtype=np.uint8)
            lower_red_2 = np.array([170, 100, 80], dtype=np.uint8)
            upper_red_2 = np.array([180, 255, 255], dtype=np.uint8)

            mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
            mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
            mask = cv2.bitwise_or(mask_1, mask_2)

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.last_detected_pixel = None
            self.last_detected_area = 0.0

            if contours:
                contour = max(contours, key=cv2.contourArea)
                area = float(cv2.contourArea(contour))
                if area >= self.min_target_area:
                    moments = cv2.moments(contour)
                    if moments["m00"] > 0:
                        cx = int(moments["m10"] / moments["m00"])
                        cy = int(moments["m01"] / moments["m00"])
                        self.last_detected_pixel = (cx, cy)
                        self.last_detected_area = area

                        cv2.drawContours(frame, [contour], -1, (0, 255, 255), 2)
                        cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
                        cv2.putText(
                            frame,
                            f"target area={area:.0f}",
                            (max(12, cx - 80), max(20, cy - 16)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (0, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        if self.auto_publish_detected_point:
                            self._publish_point_from_pixel(cx, cy, source="auto")

            return frame

        if not self.processing_mode_warned:
            self.processing_mode_warned = True
            self.get_logger().warning(
                f"Unknown processing_mode='{self.processing_mode}'. Falling back to raw image."
            )

        self.last_detected_pixel = None
        self.last_detected_area = 0.0
        return frame

    def _draw_waiting_canvas(self) -> np.ndarray:
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        canvas[:] = (20, 20, 20)

        cv2.putText(
            canvas,
            "Waiting for camera image...",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (220, 220, 220),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            f"image topic: {self.image_topic}",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (190, 190, 190),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            f"point topic: {self.point_topic}",
            (30, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (190, 190, 190),
            2,
            cv2.LINE_AA,
        )

        return canvas

    def _draw_point_overlay(self, frame: np.ndarray) -> None:
        if not self.show_point_overlay:
            return

        h, w = frame.shape[:2]
        inset_w = min(300, max(220, w // 3))
        inset_h = min(240, max(180, h // 3))
        margin = 16

        x1 = w - inset_w - margin
        y1 = margin
        x2 = x1 + inset_w
        y2 = y1 + inset_h

        if x1 < 0 or y2 > h:
            return

        # Draw a semi-transparent inset for top-down XY visualization.
        roi = frame[y1:y2, x1:x2]
        overlay = roi.copy()
        overlay[:] = (30, 30, 30)
        cv2.addWeighted(overlay, 0.6, roi, 0.4, 0, roi)

        cx = x1 + inset_w // 2
        cy = y1 + inset_h // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (120, 120, 120), 1)
        cv2.line(frame, (x1, cy), (x2, cy), (80, 80, 80), 1)
        cv2.line(frame, (cx, y1), (cx, y2), (80, 80, 80), 1)
        cv2.putText(
            frame,
            "XY (top view)",
            (x1 + 10, y1 + 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (220, 220, 220),
            2,
            cv2.LINE_AA,
        )

        if self.latest_point_msg is None:
            cv2.putText(
                frame,
                "No PointStamped",
                (x1 + 10, y1 + inset_h - 16),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (180, 180, 180),
                1,
                cv2.LINE_AA,
            )
            return

        p = self.latest_point_msg.point
        px = int(cx + p.x * self.scale_px_per_meter)
        py = int(cy - p.y * self.scale_px_per_meter)
        in_bounds = x1 <= px < x2 and y1 <= py < y2
        color = (0, 220, 0) if in_bounds else (0, 180, 255)

        draw_x = min(max(px, x1), x2 - 1)
        draw_y = min(max(py, y1), y2 - 1)
        cv2.circle(frame, (draw_x, draw_y), 6, color, -1)
        cv2.circle(frame, (draw_x, draw_y), 14, color, 2)

        point_info = (
            f"x={p.x:+.3f}m y={p.y:+.3f}m z={p.z:+.3f}m"
        )
        cv2.putText(
            frame,
            point_info,
            (x1 + 10, y2 - 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (235, 235, 235),
            1,
            cv2.LINE_AA,
        )

    def _draw_header_overlay(self, frame: np.ndarray) -> None:
        lines = [
            f"image topic: {self.image_topic}",
            f"point topic: {self.point_topic}",
            f"processing: {self.processing_mode}",
            "Press q to exit",
        ]

        if self.enable_click_scan:
            lines.append("Left-click: publish object point")

        if self.latest_image_msg is not None:
            stamp = self.latest_image_msg.header.stamp
            stamp_sec = stamp.sec + stamp.nanosec / 1e9
            frame_id = self.latest_image_msg.header.frame_id or "unknown"
            lines.insert(2, f"image frame_id: {frame_id}  stamp: {stamp_sec:.6f}s")

        for idx, line in enumerate(lines):
            y = 28 + idx * 24
            cv2.putText(
                frame,
                line,
                (12, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

    def _draw_click_marker(self, frame: np.ndarray) -> None:
        if self.last_clicked_pixel is None:
            return

        x, y = self.last_clicked_pixel
        h, w = frame.shape[:2]
        if x < 0 or y < 0 or x >= w or y >= h:
            return

        color = (0, 220, 255)
        cv2.circle(frame, (x, y), 8, color, 2)
        cv2.line(frame, (x - 12, y), (x + 12, y), color, 1)
        cv2.line(frame, (x, y - 12), (x, y + 12), color, 1)

        label = f"px=({x},{y})"
        cv2.putText(
            frame,
            label,
            (x + 10, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

    def _draw_detected_marker(self, frame: np.ndarray) -> None:
        if self.last_detected_pixel is None:
            return

        x, y = self.last_detected_pixel
        h, w = frame.shape[:2]
        if x < 0 or y < 0 or x >= w or y >= h:
            return

        color = (0, 0, 255)
        cv2.circle(frame, (x, y), 12, color, 2)
        cv2.putText(
            frame,
            f"detected px=({x},{y})",
            (x + 10, min(h - 8, y + 22)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

    def render_frame(self) -> None:
        if self.latest_image is None:
            frame = self._draw_waiting_canvas()
        else:
            frame = self.latest_image.copy()

        self._draw_header_overlay(frame)
        self._draw_point_overlay(frame)
        self._draw_click_marker(frame)
        self._draw_detected_marker(frame)

        cv2.imshow(self.window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            self.get_logger().info("Quit requested from OpenCV window.")
            rclpy.shutdown()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = CameraPointCvSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutdown requested by keyboard interrupt.")
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
