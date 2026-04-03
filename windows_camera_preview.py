#!/usr/bin/env python3
"""Live webcam preview on Windows host.

Run this file with Windows Python, not WSL Python.
"""

from __future__ import annotations

import argparse
import time

import cv2


def _candidate_backends() -> list[tuple[str, int]]:
    backends: list[tuple[str, int]] = []

    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(("DSHOW", cv2.CAP_DSHOW))
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(("MSMF", cv2.CAP_MSMF))

    backends.append(("ANY", cv2.CAP_ANY))
    return backends


def open_camera(index: int, width: int, height: int, fps: int) -> tuple[cv2.VideoCapture, str]:
    attempts: list[str] = []

    for backend_name, backend in _candidate_backends():
        cap = cv2.VideoCapture(index, backend)
        if not cap.isOpened():
            attempts.append(f"backend={backend_name}: open failed")
            cap.release()
            continue

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))
        cap.set(cv2.CAP_PROP_FPS, float(max(1, fps)))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1.0)

        ok, frame = cap.read()
        if ok and frame is not None:
            return cap, backend_name

        attempts.append(f"backend={backend_name}: first frame failed")
        cap.release()

    attempt_text = " | ".join(attempts) if attempts else "no backend attempts"
    raise RuntimeError(f"Cannot open camera index {index}. Attempts: {attempt_text}")


def scan_camera_indices(max_index: int = 10) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []

    print("[scan] Probing camera indices...")
    for index in range(max_index):
        opened_backends: list[str] = []
        for backend_name, backend in _candidate_backends():
            cap = cv2.VideoCapture(index, backend)
            opened = cap.isOpened()
            if opened:
                ok, frame = cap.read()
                if ok and frame is not None:
                    opened_backends.append(backend_name)
            cap.release()

        if opened_backends:
            uniq = sorted(set(opened_backends))
            print(f"[scan] index={index}: OK via {', '.join(uniq)}")
            found.append((index, uniq[0]))

    if not found:
        print("[scan] No available camera index detected.")

    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows webcam live preview")
    parser.add_argument("--index", type=int, default=0, help="camera index (default: 0)")
    parser.add_argument("--width", type=int, default=1280, help="capture width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, help="capture height (default: 720)")
    parser.add_argument("--fps", type=int, default=30, help="target FPS (default: 30)")
    parser.add_argument("--scan", action="store_true", help="scan available camera indices and exit")
    parser.add_argument("--max-index", type=int, default=10, help="max index to probe in scan mode")
    args = parser.parse_args()

    if args.scan:
        found = scan_camera_indices(max_index=max(1, args.max_index))
        return 0 if found else 1

    try:
        cap, backend_name = open_camera(
            index=args.index,
            width=args.width,
            height=args.height,
            fps=args.fps,
        )
    except RuntimeError as exc:
        print(f"[camera][error] {exc}")
        print("[hint] If camera was attached to WSL before, run: usbipd detach --busid <BUSID>")
        print("[hint] Check Windows camera privacy settings for desktop apps.")
        print("[hint] Try scan mode: python windows_camera_preview.py --scan")
        return 1

    window_name = "Windows Camera Preview (press q to quit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    last_time = time.perf_counter()
    smoothed_fps = 0.0

    print(f"[camera] Opened camera index={args.index} backend={backend_name}")
    print("[camera] Press q in the window to exit")

    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            # Keep trying; transient failures are common.
            continue

        now = time.perf_counter()
        dt = max(now - last_time, 1e-6)
        last_time = now
        instant_fps = 1.0 / dt
        smoothed_fps = instant_fps if smoothed_fps == 0.0 else (0.9 * smoothed_fps + 0.1 * instant_fps)

        h, w = frame.shape[:2]
        cv2.putText(
            frame,
            f"{w}x{h}  FPS:{smoothed_fps:5.1f}  Backend:{backend_name}",
            (20, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q")):
            break

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
