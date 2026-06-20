import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import DATABASE_PATH, ensure_directories
from app.utils import now_iso


def get_connection() -> sqlite3.Connection:
    ensure_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                camera_code TEXT NOT NULL,
                worker_count INTEGER NOT NULL,
                total_violation INTEGER NOT NULL,
                highest_risk TEXT NOT NULL,
                screenshot_path TEXT,
                raw_json TEXT NOT NULL
            )
            """
        )
        connection.commit()


def insert_detection_log(payload: Dict[str, Any], screenshot_path: Optional[str] = None) -> int:
    init_db()
    summary = payload.get("summary", {})
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO detection_logs (
                timestamp, camera_code, worker_count, total_violation,
                highest_risk, screenshot_path, raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_iso(),
                payload.get("camera_code", "CAM-01"),
                payload.get("worker_count", 0),
                summary.get("total_violation", 0),
                summary.get("highest_risk", "SAFE"),
                screenshot_path or summary.get("screenshot_path"),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_logs(limit: int = 100) -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, timestamp, camera_code, worker_count, total_violation,
                   highest_risk, screenshot_path, raw_json
            FROM detection_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_stats() -> Dict[str, Any]:
    init_db()
    logs = get_logs(limit=10000)
    totals = {
        "total_logs": len(logs),
        "total_violation": 0,
        "total_NO_HELMET": 0,
        "total_NO_VEST": 0,
        "total_DANGER_ZONE_ENTRY": 0,
        "latest_highest_risk": "SAFE",
    }

    if logs:
        totals["latest_highest_risk"] = logs[0]["highest_risk"]

    for log in logs:
        totals["total_violation"] += int(log["total_violation"])
        try:
            payload = json.loads(log["raw_json"])
        except json.JSONDecodeError:
            continue
        for detection in payload.get("detections", []):
            violations = detection.get("violations", [])
            totals["total_NO_HELMET"] += violations.count("NO_HELMET")
            totals["total_NO_VEST"] += violations.count("NO_VEST")
            totals["total_DANGER_ZONE_ENTRY"] += violations.count("DANGER_ZONE_ENTRY")

    return totals


Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
