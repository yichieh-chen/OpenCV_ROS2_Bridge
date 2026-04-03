#!/usr/bin/env python3

"""ROS 2 範例節點：訂閱 camera PoseStamped，轉換後發佈 JointState。"""

import sys
from typing import List

import geometry_msgs.msg
import rclpy
import sensor_msgs.msg
import std_msgs.msg
import tf2_geometry_msgs
import tf2_ros
from rclpy.node import Node


class CameraToArmNode(Node):
    def __init__(self):
        super().__init__("camera_to_arm_interface")

        self.camera_topic = "/camera/object_pose"
        self.joint_topic = "/arm/joint_command"
        self.base_frame = "arm_base_link"
        self.joint_names = ["joint1", "joint2", "joint3", "joint4"]

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.pose_subscriber = self.create_subscription(
            geometry_msgs.msg.PoseStamped,
            self.camera_topic,
            self.pose_callback,
            10,
        )

        self.joint_publisher = self.create_publisher(
            sensor_msgs.msg.JointState,
            self.joint_topic,
            10,
        )

        self.get_logger().info(f"Subscribed to {self.camera_topic}")
        self.get_logger().info(f"Publishing joint commands to {self.joint_topic}")

    def pose_callback(self, msg: geometry_msgs.msg.PoseStamped) -> None:
        self.get_logger().info(
            f"Received object pose from frame={msg.header.frame_id} at time={msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d}"
        )

        pose_in_base = self.transform_pose_to_base(msg)
        if pose_in_base is None:
            self.get_logger().warning("Unable to transform object pose to arm base frame.")
            return

        joint_angles = self.compute_joint_angles_from_pose(pose_in_base)
        if joint_angles is None:
            self.get_logger().warning("Failed to compute joint angles.")
            return

        self.publish_joint_command(joint_angles)

    def transform_pose_to_base(
        self, pose_stamped: geometry_msgs.msg.PoseStamped
    ) -> geometry_msgs.msg.PoseStamped | None:
        if pose_stamped.header.frame_id == self.base_frame:
            return pose_stamped

        try:
            transform = self.tf_buffer.lookup_transform(
                self.base_frame,
                pose_stamped.header.frame_id,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=1.0),
            )
            transformed_pose = tf2_geometry_msgs.do_transform_pose(pose_stamped, transform)
            return transformed_pose
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as exc:
            self.get_logger().error(f"TF transform failed: {exc}")
            return None

    def compute_joint_angles_from_pose(
        self, pose_stamped: geometry_msgs.msg.PoseStamped
    ) -> List[float] | None:
        # TODO: 在這裡實作從物體位置到四軸機械手臂關節角度的逆向運動學。
        # 這裡示範一個固定姿態的暫時回傳，請依照機構與 kinematics 改寫。
        self.get_logger().info(
            f"Object in base frame: x={pose_stamped.pose.position.x:.3f}, y={pose_stamped.pose.position.y:.3f}, z={pose_stamped.pose.position.z:.3f}"
        )

        # Example placeholder: 假設目標角度都是 0
        return [0.0, 0.0, 0.0, 0.0]

    def publish_joint_command(self, joint_angles: List[float]) -> None:
        joint_state = sensor_msgs.msg.JointState()
        joint_state.header = std_msgs.msg.Header()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = self.joint_names
        joint_state.position = joint_angles

        self.joint_publisher.publish(joint_state)
        self.get_logger().info(f"Published JointState: {joint_state.position}")


def main(args=None):
    rclpy.init(args=args)

    node = CameraToArmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutdown requested by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
