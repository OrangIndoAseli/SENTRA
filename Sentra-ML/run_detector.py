import argparse
import base64
import time
from typing import Any, Dict

import cv2
import requests

from app.config import DEFAULT_CAMERA_CODE, LOG_COOLDOWN_SECONDS, ensure_directories
from app.database import init_db, insert_detection_log
from app.detector import SentraDetector
from app.utils import append_jsonl, save_violation_screenshot


def parse_source(source: str) -> int | str:
    return int(source) if source.isdigit() else source


def should_log(payload: Dict[str, Any], last_log_time: float) -> bool:
    has_violation = payload.get("summary", {}).get("total_violation", 0) > 0
    cooldown_passed = time.time() - last_log_time >= LOG_COOLDOWN_SECONDS
    return has_violation and cooldown_passed


def main() -> None:
    parser = argparse.ArgumentParser(description="SENTRA-ML realtime detector")
    parser.add_argument("--source", default="0", help="Webcam index, CCTV URL, atau path file video.")
    parser.add_argument("--camera-code", default=DEFAULT_CAMERA_CODE, help="Kode kamera untuk payload dan log.")
    parser.add_argument("--no-window", action="store_true", help="Jalankan tanpa preview window.")
    parser.add_argument(
        "--backend-url",
        default="http://127.0.0.1:8000/api/detections",
        help="Endpoint Laravel untuk menyimpan kejadian. Kosongkan untuk menonaktifkan push.",
    )
    args = parser.parse_args()

    ensure_directories()
    init_db()

    detector = SentraDetector()
    capture = cv2.VideoCapture(parse_source(args.source))
    if not capture.isOpened():
        raise RuntimeError(f"Tidak bisa membuka source video: {args.source}")

    print("[SENTRA] Detector berjalan. Tekan 'q' untuk keluar.")
    last_log_time = 0.0

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        payload, annotated = detector.detect(frame, camera_code=args.camera_code, draw=True)

        if should_log(payload, last_log_time):
            screenshot_path = save_violation_screenshot(annotated)
            payload["summary"]["screenshot_saved"] = True
            payload["summary"]["screenshot_path"] = screenshot_path
            insert_detection_log(payload, screenshot_path=screenshot_path)
            append_jsonl(payload)
            if args.backend_url:
                encoded, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if encoded:
                    payload["annotated_image_base64"] = base64.b64encode(buffer).decode("ascii")
                try:
                    response = requests.post(args.backend_url, json=payload, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as exc:
                    print(f"[SENTRA] Gagal mengirim ke backend: {exc}")
            last_log_time = time.time()
            print(f"[SENTRA] Pelanggaran tersimpan: {screenshot_path}")

        if not args.no_window:
            cv2.imshow("SENTRA-ML Safety Detection", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
