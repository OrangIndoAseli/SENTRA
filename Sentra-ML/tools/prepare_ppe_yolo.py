from __future__ import annotations

import argparse
import csv
import shutil
from collections import defaultdict
from pathlib import Path


HELMET_CLASS_OFFSET = {
    0: 0,  # head
    1: 1,  # helmet
    2: 2,  # person
}
VEST_CLASS_MAP = {
    "Safety Vest": 3,
}


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_yolo_split(source_root: Path, output_root: Path, split: str, out_split: str) -> None:
    image_out = output_root / "images" / out_split
    label_out = output_root / "labels" / out_split
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    for image_path in (source_root / "images" / split).iterdir():
        if not image_path.is_file():
            continue
        target_name = f"helmet_{image_path.name}"
        shutil.copy2(image_path, image_out / target_name)

        label_path = source_root / "labels" / split / f"{image_path.stem}.txt"
        lines: list[str] = []
        if label_path.exists():
            for raw_line in label_path.read_text(encoding="utf-8").splitlines():
                parts = raw_line.split()
                if not parts:
                    continue
                class_id = HELMET_CLASS_OFFSET.get(int(parts[0]))
                if class_id is not None:
                    lines.append(" ".join([str(class_id), *parts[1:]]))
        (label_out / f"helmet_{image_path.stem}.txt").write_text("\n".join(lines), encoding="utf-8")


def convert_vest_split(source_split_root: Path, output_root: Path, split: str, out_split: str) -> None:
    image_out = output_root / "images" / out_split
    label_out = output_root / "labels" / out_split
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    annotation_path = source_split_root / split / split / "_annotations.csv"
    rows_by_file: dict[str, list[str]] = defaultdict(list)
    with annotation_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            class_id = VEST_CLASS_MAP.get(row["class"])
            if class_id is None:
                continue
            width = float(row["width"])
            height = float(row["height"])
            xmin = float(row["xmin"])
            ymin = float(row["ymin"])
            xmax = float(row["xmax"])
            ymax = float(row["ymax"])
            x_center = ((xmin + xmax) / 2) / width
            y_center = ((ymin + ymax) / 2) / height
            box_width = (xmax - xmin) / width
            box_height = (ymax - ymin) / height
            rows_by_file[row["filename"]].append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
            )

    image_dir = source_split_root / split / split
    for image_path in image_dir.iterdir():
        if not image_path.is_file() or image_path.name == "_annotations.csv":
            continue
        target_name = f"vest_{image_path.name}"
        shutil.copy2(image_path, image_out / target_name)
        label_lines = rows_by_file.get(image_path.name, [])
        (label_out / f"vest_{image_path.stem}.txt").write_text("\n".join(label_lines), encoding="utf-8")


def write_yaml(output_root: Path) -> None:
    content = f"""path: {output_root.resolve().as_posix()}
train: images/train
val: images/valid
test: images/test

names:
  0: head
  1: helmet
  2: person
  3: safety_vest
"""
    (output_root / "data.yaml").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare combined helmet + vest YOLO dataset.")
    parser.add_argument("--helmet-yolo", required=True, type=Path)
    parser.add_argument("--vest-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    reset_dir(args.output)
    copy_yolo_split(args.helmet_yolo, args.output, "train", "train")
    copy_yolo_split(args.helmet_yolo, args.output, "test", "valid")
    convert_vest_split(args.vest_root, args.output, "train", "train")
    convert_vest_split(args.vest_root, args.output, "valid", "valid")
    convert_vest_split(args.vest_root, args.output, "test", "test")
    write_yaml(args.output)


if __name__ == "__main__":
    main()
