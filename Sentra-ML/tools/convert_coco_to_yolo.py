from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any


CLASS_MAP = {
    "head": 0,
    "helmet": 1,
    "person": 2,
}


def yolo_line(annotation: dict[str, Any], image: dict[str, Any], class_id: int) -> str:
    x, y, width, height = annotation["bbox"]
    image_width = image["width"]
    image_height = image["height"]

    x_center = (x + width / 2) / image_width
    y_center = (y + height / 2) / image_height
    norm_width = width / image_width
    norm_height = height / image_height

    return f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"


def convert_split(source_root: Path, output_root: Path, split: str) -> None:
    source_split = source_root / split
    annotation_path = source_split / "_annotations.coco.json"
    data = json.loads(annotation_path.read_text(encoding="utf-8"))

    images = {image["id"]: image for image in data["images"]}
    categories = {category["id"]: category["name"] for category in data["categories"]}
    labels_by_image: dict[int, list[str]] = defaultdict(list)

    for annotation in data["annotations"]:
        category_name = categories.get(annotation["category_id"], "")
        if category_name not in CLASS_MAP:
            continue

        image = images[annotation["image_id"]]
        labels_by_image[annotation["image_id"]].append(
            yolo_line(annotation, image, CLASS_MAP[category_name])
        )

    image_out = output_root / "images" / split
    label_out = output_root / "labels" / split
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    for image in images.values():
        filename = image["file_name"]
        shutil.copy2(source_split / filename, image_out / filename)
        label_file = label_out / f"{Path(filename).stem}.txt"
        label_file.write_text("\n".join(labels_by_image.get(image["id"], [])), encoding="utf-8")


def write_yaml(output_root: Path) -> None:
    dataset_path = output_root.resolve().as_posix()
    content = f"""path: {dataset_path}
train: images/train
val: images/test

names:
  0: head
  1: helmet
  2: person
"""
    (output_root / "data.yaml").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Roboflow COCO helmet dataset to YOLO format.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    for split in ["train", "test"]:
        convert_split(args.source, args.output, split)
    write_yaml(args.output)


if __name__ == "__main__":
    main()
