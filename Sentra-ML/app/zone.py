from typing import Dict, List, Tuple

import cv2
import numpy as np

from app.config import DANGER_ZONE


Box = List[int]
Point = Tuple[int, int]


def get_default_zone() -> Dict[str, int]:
    return DANGER_ZONE.copy()


def foot_point(box: Box) -> Point:
    x1, _, x2, y2 = box
    return int((x1 + x2) / 2), int(y2)


def is_point_in_zone(point: Point, zone: Dict[str, int] | None = None) -> bool:
    active_zone = zone or get_default_zone()
    x, y = point
    return active_zone["x1"] <= x <= active_zone["x2"] and active_zone["y1"] <= y <= active_zone["y2"]


def draw_danger_zone(frame: np.ndarray, zone: Dict[str, int] | None = None) -> np.ndarray:
    active_zone = zone or get_default_zone()
    overlay = frame.copy()
    pt1 = (active_zone["x1"], active_zone["y1"])
    pt2 = (active_zone["x2"], active_zone["y2"])
    cv2.rectangle(overlay, pt1, pt2, (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)
    cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 2)
    cv2.putText(
        frame,
        "DANGER ZONE",
        (active_zone["x1"], max(25, active_zone["y1"] - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )
    return frame
