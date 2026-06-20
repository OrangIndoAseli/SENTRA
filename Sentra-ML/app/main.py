import base64
import time
from typing import Any, Dict

import cv2
import numpy as np
import requests
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, DEFAULT_CAMERA_CODE, LARAVEL_ENDPOINT_URL, ensure_directories
from app.database import get_logs, get_stats, init_db, insert_detection_log
from app.detector import SentraDetector
from app.schemas import DetectionResponse, LaravelPayload
from app.utils import append_jsonl, save_violation_screenshot


ensure_directories()
init_db()

app = FastAPI(title="SENTRA-ML API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
detector = SentraDetector()


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "SENTRA-ML API running", "project": "Safety Enforcement, Notification, Tracking & Risk Analytics"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/logs")
def logs(limit: int = 100) -> Dict[str, Any]:
    return {"data": get_logs(limit=limit)}


@app.get("/stats")
def stats() -> Dict[str, Any]:
    return get_stats()


def encode_annotated_image(frame: np.ndarray) -> str:
    encoded, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
    return base64.b64encode(buffer).decode("ascii") if encoded else ""


def violation_signature(payload: Dict[str, Any]) -> str:
    violations = []
    for worker in payload.get("detections", []):
        codes = sorted(worker.get("violations", []))
        if codes:
            violations.append(f'{worker["worker_id"]}:{"|".join(codes)}')
    return ";".join(sorted(violations))


@app.post("/detect-image", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    camera_code: str = DEFAULT_CAMERA_CODE,
    zone_x1: int | None = None,
    zone_y1: int | None = None,
    zone_x2: int | None = None,
    zone_y2: int | None = None,
) -> Dict[str, Any]:
    content = await file.read()
    image_array = np.frombuffer(content, np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="File upload bukan image yang valid.")

    values = [zone_x1, zone_y1, zone_x2, zone_y2]
    danger_zone = dict(zip(["x1", "y1", "x2", "y2"], values)) if all(v is not None for v in values) else None
    payload, annotated = detector.detect(frame, camera_code=camera_code, draw=True, danger_zone=danger_zone)
    if payload["summary"]["total_violation"] > 0:
        screenshot_path = save_violation_screenshot(annotated)
        payload["summary"]["screenshot_saved"] = True
        payload["summary"]["screenshot_path"] = screenshot_path
        insert_detection_log(payload, screenshot_path=screenshot_path)
        append_jsonl(payload)

    payload["annotated_image_base64"] = encode_annotated_image(annotated)
    return payload


@app.websocket("/ws/detect")
async def detect_websocket(websocket: WebSocket) -> None:
    """Continuous browser-camera inference; only confirmed incidents are persisted."""
    await websocket.accept()
    camera_code = websocket.query_params.get("camera_code", DEFAULT_CAMERA_CODE)
    active_workers: Dict[str, Dict[str, float]] = {}

    try:
        while True:
            content = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"error": "Frame video tidak valid."})
                continue

            payload, annotated = detector.detect(frame, camera_code=camera_code, draw=True)
            now = time.monotonic()
            resolved_workers = [worker_id for worker_id, state in active_workers.items() if now - state["seen_at"] >= 15]
            active_workers = {worker_id: state for worker_id, state in active_workers.items() if now - state["seen_at"] < 15}
            if resolved_workers:
                try:
                    requests.post(
                        f"{LARAVEL_ENDPOINT_URL.rsplit('/', 1)[0]}/resolve",
                        json={"camera_code": camera_code, "worker_ids": resolved_workers},
                        timeout=10,
                    )
                except requests.RequestException:
                    pass
            violating_workers = [worker for worker in payload["detections"] if worker["violations"]]
            new_workers = [worker for worker in violating_workers if worker["worker_id"] not in active_workers]
            for worker in violating_workers:
                if worker["worker_id"] in active_workers:
                    state = active_workers[worker["worker_id"]]
                    state["seen_at"] = now
                    score = float(worker.get("evidence_score", 0))
                    if score >= state["best_score"] * 1.15 and now - state["last_evidence_at"] >= 3:
                        try:
                            response = requests.post(
                                f"{LARAVEL_ENDPOINT_URL.rsplit('/', 1)[0]}/evidence",
                                json={
                                    "camera_code": camera_code,
                                    "worker_id": worker["worker_id"],
                                    "evidence_score": score,
                                    "annotated_image_base64": encode_annotated_image(annotated),
                                },
                                timeout=10,
                            )
                            if response.ok:
                                state["best_score"] = score
                                state["last_evidence_at"] = now
                        except requests.RequestException:
                            pass
            event_saved = False

            if new_workers:
                try:
                    event_payload = {
                        **payload,
                        "worker_count": len(new_workers),
                        "detections": new_workers,
                        "summary": {
                            **payload["summary"],
                            "total_violation": sum(len(worker["violations"]) for worker in new_workers),
                            "highest_risk": max((worker["risk_level"] for worker in new_workers), key=lambda level: {"SAFE": 0, "WARNING": 1, "HIGH": 2, "CRITICAL": 3}[level]),
                        },
                        "annotated_image_base64": encode_annotated_image(annotated),
                    }
                    response = requests.post(LARAVEL_ENDPOINT_URL, json=event_payload, timeout=10)
                    event_saved = response.ok
                    if event_saved:
                        for worker in new_workers:
                            active_workers[worker["worker_id"]] = {
                                "seen_at": now,
                                "best_score": float(worker.get("evidence_score", 0)),
                                "last_evidence_at": now,
                            }
                except requests.RequestException:
                    event_saved = False

            await websocket.send_json({
                "result": payload,
                "event_saved": event_saved,
                "event_workers": [worker["worker_id"] for worker in new_workers] if event_saved else [],
            })
    except WebSocketDisconnect:
        return


@app.post("/send-to-laravel")
def send_to_laravel(request: LaravelPayload) -> Dict[str, Any]:
    target_url = request.url or LARAVEL_ENDPOINT_URL
    try:
        response = requests.post(target_url, json=request.payload, timeout=10)
        return {
            "sent": response.ok,
            "target_url": target_url,
            "status_code": response.status_code,
            "response": response.text[:1000],
        }
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Gagal mengirim ke Laravel: {exc}") from exc
