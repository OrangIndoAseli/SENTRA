import os
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
CAPTURES_DIR = BASE_DIR / "captures"
LOGS_DIR = BASE_DIR / "logs"
SAMPLE_VIDEOS_DIR = BASE_DIR / "sample_videos"

CUSTOM_MODEL_PATH = MODELS_DIR / "best.pt"
HELMET_MODEL_PATH = MODELS_DIR / "helmet.pt"
VEST_MODEL_PATH = MODELS_DIR / "vest.pt"
SH17_ASSIST_MODEL_PATH = MODELS_DIR / "candidate_sh17.pt"
FALLBACK_MODEL_NAME = "yolov8n.pt"

DATABASE_PATH = BASE_DIR / "sentra_logs.db"
JSONL_LOG_PATH = LOGS_DIR / "detection_logs.jsonl"

DEFAULT_CAMERA_CODE = "CAM-01"
LOG_COOLDOWN_SECONDS = 5
DEFAULT_CONFIDENCE = 0.35
PPE_WORN_CONFIDENCE = float(os.getenv("SENTRA_PPE_WORN_CONFIDENCE", "0.35"))

LARAVEL_ENDPOINT_URL = os.getenv("SENTRA_LARAVEL_URL", "http://127.0.0.1:8000/api/detections")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("SENTRA_CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

DANGER_ZONE = {
    "x1": 100,
    "y1": 300,
    "x2": 600,
    "y2": 700,
}

CLASS_ALIASES: Dict[str, List[str]] = {
    "person": ["person", "worker", "pedestrian"],
    "helmet": ["helmet", "hardhat", "hard_hat", "safety helmet", "safety_helmet"],
    "vest": ["safety vest", "safety_vest", "vest", "reflective vest", "reflective_vest"],
    "no_helmet": ["no-helmet", "no helmet", "no_helmet", "without helmet"],
    "no_vest": ["no-vest", "no vest", "no_vest", "without vest"],
}


def ensure_directories() -> None:
    for directory in [MODELS_DIR, CAPTURES_DIR, LOGS_DIR, SAMPLE_VIDEOS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def get_model_path() -> str:
    ensure_directories()
    if CUSTOM_MODEL_PATH.exists():
        return str(CUSTOM_MODEL_PATH)

    print(
        "[SENTRA] Warning: models/best.pt tidak ditemukan. "
        "Menggunakan fallback yolov8n.pt; deteksi helmet/vest kemungkinan tidak tersedia. "
        "Masukkan model custom PPE ke models/best.pt untuk hasil akurat."
    )
    return FALLBACK_MODEL_NAME


def get_helmet_model_path() -> str:
    ensure_directories()
    if HELMET_MODEL_PATH.exists():
        return str(HELMET_MODEL_PATH)
    return get_model_path()


def get_vest_model_path() -> str:
    ensure_directories()
    if VEST_MODEL_PATH.exists():
        return str(VEST_MODEL_PATH)
    return get_model_path()


def get_sh17_assist_model_path() -> str | None:
    ensure_directories()
    if SH17_ASSIST_MODEL_PATH.exists():
        return str(SH17_ASSIST_MODEL_PATH)
    return None
