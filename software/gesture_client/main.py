#!/usr/bin/env python3
"""
Egocentric hand-gesture recognition client (Raspberry Pi / host).

Captures camera frames, runs MediaPipe Hands, classifies gestures, and sends
robust UDP commands to the ESP32 robotic-arm controller.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import cv2
import mediapipe as mp
import yaml

from gestures import COMMAND_DESCRIPTIONS, classify_hand
from udp_client import RobustUdpClient


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time egocentric HGR → UDP robotic teleoperation client",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("config.yaml"),
        help="Path to YAML config (default: config.yaml next to this script)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Override ESP32 host IP",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override UDP port",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Override camera index",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    example = Path(__file__).with_name("config.example.yaml")
    config_path = args.config if args.config.exists() else example
    if not config_path.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 1

    cfg = load_config(config_path)
    host = args.host or cfg["robot"]["host"]
    port = args.port or int(cfg["robot"]["port"])
    cam_index = args.camera if args.camera is not None else int(cfg["camera"]["index"])
    width = int(cfg["camera"]["width"])
    height = int(cfg["camera"]["height"])
    confirm = int(cfg["gesture"]["confirm_frames"])
    suffix = str(cfg["gesture"].get("payload_suffix", "100,0,0,0"))
    window = str(cfg["display"].get("window_name", "Hand Tracking"))
    mirror = bool(cfg["display"].get("mirror", True))

    client = RobustUdpClient((host, port), confirm_frames=confirm, payload_suffix=suffix)
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    drawer = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, width, height)

    print(f"UDP target: {host}:{port}")
    print(f"Confirm frames: {confirm}")
    print("Commands:", ", ".join(f"{k}={v}" for k, v in COMMAND_DESCRIPTIONS.items()))
    print("Press 'q' to quit.")

    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            if mirror:
                frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            h, w = frame.shape[:2]
            command = "I"

            if results.multi_hand_landmarks and results.multi_handedness:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    drawer.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp.solutions.hands.HAND_CONNECTIONS,
                    )
                    label = results.multi_handedness[idx].classification[0].label
                    mapped = classify_hand(hand_landmarks, label, w, h)
                    if mapped is not None:
                        command = mapped
                        cv2.putText(
                            frame,
                            f"{label}: {mapped}",
                            (10, 30 + 30 * idx),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )

            sent = client.observe(command)
            status = f"cmd={command}" + (" SENT" if sent else " (confirming)")
            cv2.putText(
                frame,
                status,
                (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
            if sent:
                print(f"Sending command: {command},{suffix}")

            cv2.imshow(window, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        hands.close()
        client.close()
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
