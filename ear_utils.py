"""
ear_utils.py — Eye Aspect Ratio (EAR) helpers
----------------------------------------------
EAR formula (Soukupová & Čech, 2016):

         ‖p2−p6‖ + ‖p3−p5‖
EAR =  ─────────────────────
             2 · ‖p1−p4‖

Where p1..p6 are the six eye-contour landmarks (clockwise from outer corner).
EAR ≈ 0.3  → eye fully open
EAR < 0.25 → eye closed / blinking
"""

import math
from typing import List, Tuple

# MediaPipe FaceMesh landmark indices for left and right eyes
# Order: [outer, top-outer, top-inner, inner, bot-inner, bot-outer]
LEFT_EYE_IDX  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33,  160, 158, 133, 153, 144]


def _dist(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Euclidean distance between two 2-D points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def calculate_ear(eye_pts: List[Tuple[int, int]]) -> float:
    """
    Compute Eye Aspect Ratio from 6 eye-contour points.

    Args:
        eye_pts: List of 6 (x, y) pixel coordinates in the order
                 [p1, p2, p3, p4, p5, p6] described above.

    Returns:
        EAR as a float. Values below ~0.25 indicate a closed eye.
    """
    if len(eye_pts) != 6:
        raise ValueError(f"Expected 6 eye points, got {len(eye_pts)}")

    p1, p2, p3, p4, p5, p6 = eye_pts

    vertical_1 = _dist(p2, p6)   # top-outer  ↔ bot-outer
    vertical_2 = _dist(p3, p5)   # top-inner  ↔ bot-inner
    horizontal = _dist(p1, p4)   # outer corner ↔ inner corner

    if horizontal < 1e-6:        # guard against division by zero
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def get_eye_landmarks(
    landmarks,
    frame_w: int,
    frame_h: int,
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Extract pixel coordinates for both eyes from a MediaPipe landmark list.

    Args:
        landmarks : face_mesh result .landmark list (normalised 0-1 coords)
        frame_w   : frame width  in pixels
        frame_h   : frame height in pixels

    Returns:
        (left_eye_pts, right_eye_pts) — each a list of 6 (x, y) int tuples.
    """
    def _to_px(idx: int) -> Tuple[int, int]:
        lm = landmarks[idx]
        return (int(lm.x * frame_w), int(lm.y * frame_h))

    left_eye  = [_to_px(i) for i in LEFT_EYE_IDX]
    right_eye = [_to_px(i) for i in RIGHT_EYE_IDX]
    return left_eye, right_eye