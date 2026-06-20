import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import cv2

from app.config import CAPTURES_DIR, JSONL_LOG_PATH, ensure_directories


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def center_point(box: List[int]) -> tuple[int, int]:
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def point_inside_box(point: tuple[int, int], box: List[int]) -> bool:
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def point_in_upper_person_area(point: tuple[int, int], person_box: List[int]) -> bool:
    x, y = point
    x1, y1, x2, y2 = person_box
    upper_limit = y1 + int((y2 - y1) * 0.35)
    return x1 <= x <= x2 and y1 <= y <= upper_limit


def box_center_in_person_head_area(box: List[int], person_box: List[int]) -> bool:
    x, y = center_point(box)
    x1, y1, x2, y2 = person_box
    person_width = x2 - x1
    person_height = y2 - y1
    if person_width <= 0 or person_height <= 0:
        return False

    head_bottom = y1 + int(person_height * 0.24)
    horizontal_margin = int(person_width * 0.18)
    return (x1 - horizontal_margin) <= x <= (x2 + horizontal_margin) and y1 <= y <= head_bottom


def box_center_in_person_torso_area(box: List[int], person_box: List[int]) -> bool:
    x, y = center_point(box)
    x1, y1, x2, y2 = person_box
    person_height = y2 - y1
    if person_height <= 0:
        return False

    torso_top = y1 + int(person_height * 0.18)
    torso_bottom = y1 + int(person_height * 0.72)
    return x1 <= x <= x2 and torso_top <= y <= torso_bottom


def normalize_class_name(name: str) -> str:
    return name.strip().lower().replace("_", " ").replace("-", " ")


def save_violation_screenshot(frame, prefix: str = "violation") -> str:
    ensure_directories()
    filename = f"{prefix}_{timestamp_for_filename()}.jpg"
    path = CAPTURES_DIR / filename
    cv2.imwrite(str(path), frame)
    return str(Path("captures") / filename)


def append_jsonl(payload: Dict[str, Any]) -> None:
    ensure_directories()
    with JSONL_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def flatten_violations(detections: Iterable[Dict[str, Any]]) -> List[str]:
    violations: List[str] = []
    for detection in detections:
        violations.extend(detection.get("violations", []))
    return violations
