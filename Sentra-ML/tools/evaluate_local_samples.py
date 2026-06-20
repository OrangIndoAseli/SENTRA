from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2

from app.detector import SentraDetector


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SENTRA detector on local evaluation samples.")
    parser.add_argument("--samples", type=Path, default=Path("evaluation/test_samples"))
    parser.add_argument("--output", type=Path, default=Path("evaluation/results"))
    parser.add_argument("--confidence", type=float, default=0.35)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    annotated_dir = args.output / "annotated"
    annotated_dir.mkdir(parents=True, exist_ok=True)

    detector = SentraDetector(confidence=args.confidence)
    rows: list[dict[str, object]] = []
    payloads: list[dict[str, object]] = []

    image_paths = sorted(
        path
        for path in args.samples.rglob("*")
        if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    for image_path in image_paths:
        frame = cv2.imread(str(image_path))
        if frame is None:
            continue
        payload, annotated = detector.detect(frame, camera_code="EVAL", draw=True)
        relative = image_path.relative_to(args.samples)
        safe_name = "__".join(relative.parts)
        cv2.imwrite(str(annotated_dir / safe_name), annotated)

        detections = payload["detections"]
        rows.append(
            {
                "file": relative.as_posix(),
                "worker_count": payload["worker_count"],
                "total_violation": payload["summary"]["total_violation"],
                "highest_risk": payload["summary"]["highest_risk"],
                "helmet_ok": sum(1 for detection in detections if detection["helmet"]),
                "vest_ok": sum(1 for detection in detections if detection["vest"]),
                "no_helmet": sum(1 for detection in detections if "NO_HELMET" in detection["violations"]),
                "no_vest": sum(1 for detection in detections if "NO_VEST" in detection["violations"]),
            }
        )
        payloads.append({"file": relative.as_posix(), "payload": payload})

    with (args.output / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "file",
            "worker_count",
            "total_violation",
            "highest_risk",
            "helmet_ok",
            "vest_ok",
            "no_helmet",
            "no_vest",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    (args.output / "payloads.json").write_text(json.dumps(payloads, indent=2), encoding="utf-8")
    print(f"Evaluated {len(rows)} images. Summary: {args.output / 'summary.csv'}")


if __name__ == "__main__":
    main()
