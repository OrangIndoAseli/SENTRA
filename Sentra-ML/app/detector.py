from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

os.environ.setdefault("YOLO_CONFIG_DIR", str(Path(__file__).resolve().parent.parent / ".ultralytics"))

from ultralytics import YOLO

from app.config import (
    CLASS_ALIASES,
    DEFAULT_CAMERA_CODE,
    DEFAULT_CONFIDENCE,
    FALLBACK_MODEL_NAME,
    PPE_WORN_CONFIDENCE,
    get_helmet_model_path,
    get_sh17_assist_model_path,
    get_vest_model_path,
)
from app.risk_engine import calculate_risk, highest_risk_level
from app.utils import box_center_in_person_head_area, box_center_in_person_torso_area, center_point
from app.zone import draw_danger_zone, foot_point, is_point_in_zone


@dataclass
class DetectionBox:
    box: List[int]
    class_name: str
    confidence: float


class SentraDetector:
    def __init__(
        self,
        confidence: float = DEFAULT_CONFIDENCE,
        helmet_model_path: Optional[str] = None,
        vest_model_path: Optional[str] = None,
        sh17_assist_model_path: Optional[str] = None,
    ):
        self.helmet_model_path = helmet_model_path or get_helmet_model_path()
        self.vest_model_path = vest_model_path or get_vest_model_path()
        self.sh17_assist_model_path = sh17_assist_model_path if sh17_assist_model_path is not None else get_sh17_assist_model_path()
        self.confidence = confidence
        self.assist_confidence = max(confidence, 0.55)
        self.helmet_worn_confidence = max(confidence, PPE_WORN_CONFIDENCE)
        self.vest_worn_confidence = max(confidence, PPE_WORN_CONFIDENCE)
        self.helmet_model = YOLO(self.helmet_model_path)
        self.vest_model = YOLO(self.vest_model_path)
        self.sh17_assist_model = YOLO(self.sh17_assist_model_path) if self.sh17_assist_model_path else None
        self.names: Dict[int, str] = {}
        self.helmet_names = self.helmet_model.names
        self.vest_names = self.vest_model.names
        self.sh17_assist_names = self.sh17_assist_model.names if self.sh17_assist_model is not None else {}
        model_paths = {self.helmet_model_path, self.vest_model_path, self.sh17_assist_model_path}
        self.person_fallback_model = YOLO(FALLBACK_MODEL_NAME) if FALLBACK_MODEL_NAME not in model_paths else None
        self.supports_helmet = self._has_class_group("helmet", self.helmet_names) or self._has_class_group("no_helmet", self.helmet_names)
        self.supports_vest = self._has_class_group("vest", self.vest_names) or self._has_class_group("no_vest", self.vest_names)
        self.tracks: Dict[str, List[Dict[str, Any]]] = {}
        self.next_track_id = 1
        self._warn_if_ppe_unavailable()

    @staticmethod
    def _iou(first: List[int], second: List[int]) -> float:
        left, top = max(first[0], second[0]), max(first[1], second[1])
        right, bottom = min(first[2], second[2]), min(first[3], second[3])
        intersection = max(0, right - left) * max(0, bottom - top)
        if not intersection:
            return 0.0
        first_area = max(0, first[2] - first[0]) * max(0, first[3] - first[1])
        second_area = max(0, second[2] - second[0]) * max(0, second[3] - second[1])
        return intersection / max(1, first_area + second_area - intersection)

    def _worker_ids(self, camera_code: str, people: List[DetectionBox]) -> List[str]:
        now = time.monotonic()
        tracks = [track for track in self.tracks.get(camera_code, []) if now - track["seen_at"] < 10]
        assigned: List[str] = []
        used_ids = set()
        for person in people:
            candidates = [track for track in tracks if track["id"] not in used_ids]
            best = max(candidates, key=lambda track: self._iou(person.box, track["box"]), default=None)
            if best and self._iou(person.box, best["box"]) >= 0.25:
                best["box"], best["seen_at"] = person.box, now
                worker_id = best["id"]
            else:
                worker_id = f"W-{self.next_track_id:03d}"
                self.next_track_id += 1
                tracks.append({"id": worker_id, "box": person.box, "seen_at": now})
            used_ids.add(worker_id)
            assigned.append(worker_id)
        self.tracks[camera_code] = tracks
        return assigned

    def _warn_if_ppe_unavailable(self) -> None:
        available_names = list(self.helmet_names.values()) + list(self.vest_names.values())
        available = {str(name).strip().lower().replace("_", " ").replace("-", " ") for name in available_names}
        has_ppe_class = any(
            alias.replace("_", " ").replace("-", " ").lower() in available
            for aliases in [CLASS_ALIASES["helmet"], CLASS_ALIASES["vest"], CLASS_ALIASES["no_helmet"], CLASS_ALIASES["no_vest"]]
            for alias in aliases
        )
        if not has_ppe_class:
            print(
                "[SENTRA] Warning: model aktif belum memiliki class PPE. "
                "Helmet dan safety vest akan dianggap tidak terdeteksi sampai models/best.pt diganti model custom PPE."
            )

    def _has_class_group(self, group: str, names: Optional[Dict[int, str]] = None) -> bool:
        names = names or self.names
        available = {str(name).strip().lower().replace("_", " ").replace("-", " ") for name in names.values()}
        aliases = [alias.replace("_", " ").replace("-", " ").lower() for alias in CLASS_ALIASES[group]]
        return any(alias in available for alias in aliases)

    @staticmethod
    def _is_alias(class_name: str, group: str) -> bool:
        normalized = class_name.strip().lower().replace("_", " ").replace("-", " ")
        aliases = [alias.replace("_", " ").replace("-", " ").lower() for alias in CLASS_ALIASES[group]]
        return normalized in aliases

    def _parse_results(
        self,
        results: Any,
        names: Optional[Dict[int, str]] = None,
        min_confidence: Optional[float] = None,
    ) -> Dict[str, List[DetectionBox]]:
        names = names or self.names
        min_confidence = self.confidence if min_confidence is None else min_confidence
        grouped: Dict[str, List[DetectionBox]] = {
            "persons": [],
            "helmets": [],
            "vests": [],
            "no_helmets": [],
            "no_vests": [],
            "others": [],
        }

        if not results:
            return grouped

        result = results[0]
        for raw_box in result.boxes:
            confidence = float(raw_box.conf[0])
            if confidence < min_confidence:
                continue

            cls_id = int(raw_box.cls[0])
            class_name = str(names.get(cls_id, cls_id))
            x1, y1, x2, y2 = [int(value) for value in raw_box.xyxy[0].tolist()]
            detection = DetectionBox(box=[x1, y1, x2, y2], class_name=class_name, confidence=confidence)

            if self._is_alias(class_name, "person"):
                grouped["persons"].append(detection)
            elif self._is_alias(class_name, "helmet"):
                grouped["helmets"].append(detection)
            elif self._is_alias(class_name, "vest"):
                grouped["vests"].append(detection)
            elif self._is_alias(class_name, "no_helmet"):
                grouped["no_helmets"].append(detection)
            elif self._is_alias(class_name, "no_vest"):
                grouped["no_vests"].append(detection)
            else:
                grouped["others"].append(detection)

        return grouped

    def _matched_helmet(self, person_box: List[int], helmets: List[DetectionBox], no_helmets: List[DetectionBox]) -> Optional[DetectionBox]:
        for no_helmet in no_helmets:
            if box_center_in_person_head_area(no_helmet.box, person_box):
                return None
        candidates = [
            helmet for helmet in helmets
            if helmet.confidence >= self.helmet_worn_confidence and box_center_in_person_head_area(helmet.box, person_box)
        ]
        return max(candidates, key=lambda helmet: helmet.confidence, default=None)

    def _matched_vest(self, person_box: List[int], vests: List[DetectionBox], no_vests: List[DetectionBox]) -> Optional[DetectionBox]:
        for no_vest in no_vests:
            if box_center_in_person_torso_area(no_vest.box, person_box):
                return None
        candidates = [
            vest for vest in vests
            if vest.confidence >= self.vest_worn_confidence and box_center_in_person_torso_area(vest.box, person_box)
        ]
        return max(candidates, key=lambda vest: vest.confidence, default=None)

    def detect(
        self,
        frame: np.ndarray,
        camera_code: str = DEFAULT_CAMERA_CODE,
        draw: bool = True,
        danger_zone: Optional[Dict[str, int]] = None,
    ) -> Tuple[Dict[str, Any], np.ndarray]:
        annotated = frame.copy()
        if draw and danger_zone is not None:
            draw_danger_zone(annotated, danger_zone)

        grouped: Dict[str, List[DetectionBox]] = {
            "persons": [],
            "helmets": [],
            "vests": [],
            "no_helmets": [],
            "no_vests": [],
            "others": [],
        }
        helmet_results = self.helmet_model(frame, verbose=False)
        vest_results = self.vest_model(frame, verbose=False)
        helmet_grouped = self._parse_results(helmet_results, self.helmet_names)
        vest_grouped = self._parse_results(vest_results, self.vest_names)
        grouped["persons"].extend(helmet_grouped["persons"])
        grouped["helmets"] = helmet_grouped["helmets"]
        grouped["no_helmets"] = helmet_grouped["no_helmets"]
        grouped["vests"] = vest_grouped["vests"]
        grouped["no_vests"] = vest_grouped["no_vests"]
        if self.sh17_assist_model is not None:
            assist_results = self.sh17_assist_model(frame, verbose=False)
            assist_grouped = self._parse_results(assist_results, self.sh17_assist_names, self.assist_confidence)
            grouped["helmets"].extend(assist_grouped["helmets"])
            grouped["vests"].extend(assist_grouped["vests"])
        if not grouped["persons"] and self.person_fallback_model is not None:
            fallback_results = self.person_fallback_model(frame, verbose=False)
            grouped["persons"] = self._parse_results(fallback_results, self.person_fallback_model.names)["persons"]
        detections: List[Dict[str, Any]] = []

        worker_ids = self._worker_ids(camera_code, grouped["persons"])
        for person, worker_id in zip(grouped["persons"], worker_ids):
            person_box = person.box
            helmet_detection = self._matched_helmet(person_box, grouped["helmets"], grouped["no_helmets"]) if self.supports_helmet else None
            vest_detection = self._matched_vest(person_box, grouped["vests"], grouped["no_vests"]) if self.supports_vest else None
            has_helmet = bool(helmet_detection) if self.supports_helmet else True
            has_vest = bool(vest_detection) if self.supports_vest else True
            in_danger_zone = danger_zone is not None and is_point_in_zone(foot_point(person_box), danger_zone)

            violations: List[str] = []
            if self.supports_helmet and not has_helmet:
                violations.append("NO_HELMET")
            if self.supports_vest and not has_vest:
                violations.append("NO_VEST")
            if in_danger_zone:
                violations.append("DANGER_ZONE_ENTRY")

            risk_score, risk_level = calculate_risk(violations)
            worker = {
                "worker_id": worker_id,
                "helmet": has_helmet,
                "vest": has_vest,
                "in_danger_zone": in_danger_zone,
                "violations": violations,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "box": person_box,
                "helmet_box": helmet_detection.box if helmet_detection else None,
                "vest_box": vest_detection.box if vest_detection else None,
                "evidence_score": round(person.confidence * ((person_box[2] - person_box[0]) * (person_box[3] - person_box[1])) / max(1, frame.shape[0] * frame.shape[1]), 6),
            }
            detections.append(worker)

            if draw:
                self._draw_worker(annotated, worker)

        risk_levels = [worker["risk_level"] for worker in detections]
        total_violation = sum(len(worker["violations"]) for worker in detections)
        payload = {
            "camera_code": camera_code,
            "worker_count": len(detections),
            "detections": detections,
            "summary": {
                "total_violation": total_violation,
                "highest_risk": highest_risk_level(risk_levels),
                "screenshot_saved": False,
                "screenshot_path": None,
                "sh17_assist_enabled": self.sh17_assist_model is not None,
            },
        }

        if draw and total_violation:
            cv2.putText(
                annotated,
                f"ALERT: {total_violation} VIOLATION(S)",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3,
                cv2.LINE_AA,
            )

        return payload, annotated

    @staticmethod
    def _draw_worker(frame: np.ndarray, worker: Dict[str, Any]) -> None:
        if worker["violations"]:
            x1, y1, x2, y2 = worker["box"]
            label = ",".join(worker["violations"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        for name, box, color in [
            ("HELMET", worker.get("helmet_box"), (0, 220, 0)),
            ("VEST", worker.get("vest_box"), (0, 220, 0)),
        ]:
            if not box:
                continue
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, name, (x1, max(20, y1 - 7)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
