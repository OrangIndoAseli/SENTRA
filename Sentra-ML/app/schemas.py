from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class WorkerDetection(BaseModel):
    worker_id: str
    helmet: bool
    vest: bool
    in_danger_zone: bool
    violations: List[str]
    risk_score: int
    risk_level: str
    box: List[int]
    helmet_box: Optional[List[int]] = None
    vest_box: Optional[List[int]] = None
    evidence_score: float = 0


class DetectionSummary(BaseModel):
    total_violation: int
    highest_risk: str
    screenshot_saved: bool
    screenshot_path: Optional[str] = None


class DetectionResponse(BaseModel):
    camera_code: str
    worker_count: int
    detections: List[WorkerDetection]
    summary: DetectionSummary
    annotated_image_base64: Optional[str] = None


class LaravelPayload(BaseModel):
    url: Optional[str] = None
    payload: Dict[str, Any]
