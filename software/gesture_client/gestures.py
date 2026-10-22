"""
Hand-landmark → teleoperation command mapping.

Commands A–I match the ESP32 firmware ``controlServos`` table from the MEng dissertation.
Landmark indices follow MediaPipe Hands (21 landmarks).
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

# MediaPipe landmark indices
WRIST = 0
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 2
INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP = 12, 10, 9
RING_TIP, RING_PIP, RING_MCP = 16, 14, 13
PINKY_TIP, PINKY_PIP, PINKY_MCP = 20, 18, 17

Point = Tuple[float, float]


def _pixel_landmarks(
    landmarks,
    image_width: int,
    image_height: int,
) -> List[Point]:
    """Convert normalized landmarks to pixel (x, y). y increases downward."""
    pts: List[Point] = []
    for lm in landmarks.landmark:
        pts.append((lm.x * image_width, lm.y * image_height))
    return pts


def _finger_extended(tip: Point, pip: Point) -> bool:
    """True if fingertip is above PIP joint in image space (smaller y)."""
    return tip[1] < pip[1]


def _thumb_extended_right(pts: Sequence[Point]) -> bool:
    """Heuristic for right hand: thumb tip left of IP (mirrored selfie view)."""
    return pts[THUMB_TIP][0] < pts[THUMB_IP][0]


def _thumb_extended_left(pts: Sequence[Point]) -> bool:
    """Heuristic for left hand: thumb tip right of IP (mirrored selfie view)."""
    return pts[THUMB_TIP][0] > pts[THUMB_IP][0]


def classify_hand(
    landmarks,
    handedness_label: str,
    image_width: int,
    image_height: int,
) -> Optional[str]:
    """
    Classify a single hand into a command letter, or None if no gesture matched.

    Right hand (thesis mapping):
      - index extended          → B  (servo 2)
      - middle extended         → F  (servo 6 open)
      - pinky extended          → H  (multi-servo pose)
      - open palm (I+M+P)       → H

    Left hand (thesis mapping):
      - thumb / pinky region tip check → C  (kept for compatibility; uses tip/mcp y)
      - index extended          → D
      - ring extended           → E  (thesis used landmark 16 as "pinky" check)
      - middle extended         → G  (servo 6 close)

    Prefer specific single-finger gestures; open-palm checked last for right hand.
    """
    pts = _pixel_landmarks(landmarks, image_width, image_height)
    index_up = _finger_extended(pts[INDEX_TIP], pts[INDEX_PIP])
    middle_up = _finger_extended(pts[MIDDLE_TIP], pts[MIDDLE_PIP])
    ring_up = _finger_extended(pts[RING_TIP], pts[RING_PIP])
    pinky_up = _finger_extended(pts[PINKY_TIP], pts[PINKY_PIP])

    label = handedness_label.strip().title()

    if label == "Right":
        # Open palm takes precedence when multiple fingers are clearly extended.
        if index_up and middle_up and pinky_up:
            return "H"
        if index_up and not middle_up and not pinky_up:
            return "B"
        if pinky_up and not index_up and not middle_up:
            return "H"
        if middle_up and not index_up and not pinky_up:
            return "F"
        return None

    if label == "Left":
        # Thesis used landmark 20 vs 19 for a left-hand "thumb" check (pinky tip/mcp).
        # Keep that behavior for fidelity, and also allow true thumb extension.
        left_special = pts[PINKY_TIP][1] < pts[PINKY_MCP][1]
        if left_special and not index_up and not middle_up:
            return "C"
        if _thumb_extended_left(pts) and not index_up and not middle_up and not ring_up:
            return "C"
        if index_up and not middle_up and not ring_up:
            return "D"
        if ring_up and not index_up and not middle_up:
            return "E"
        if middle_up and not index_up:
            return "G"
        return None

    return None


COMMAND_DESCRIPTIONS = {
    "A": "Servo 1 → 180°",
    "B": "Servo 2 → 180° (right index)",
    "C": "Servo 3 → 180° (left special / thumb)",
    "D": "Servo 4 → 180° (left index)",
    "E": "Servo 5 → 180° (left ring)",
    "F": "Servo 6 → 180° (right middle / open gripper)",
    "G": "Servo 6 → 0° (left middle / close gripper)",
    "H": "Multi-servo pose (right open palm / pinky)",
    "I": "Idle / stop motion (no hand detected)",
}
