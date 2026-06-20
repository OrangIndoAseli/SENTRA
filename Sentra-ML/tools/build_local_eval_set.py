from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path


CATEGORIES = {
    "helmet_only": lambda classes: 1 in classes and 3 not in classes,
    "vest_only": lambda classes: 3 in classes and 1 not in classes,
    "helmet_and_vest": lambda classes: 1 in classes and 3 in classes,
    "no_ppe_or_head": lambda classes: 0 in classes and 1 not in classes and 3 not in classes,
}


def label_classes(label_path: Path) -> set[int]:
    classes: set[int] = set()
    if not label_path.exists():
        return classes
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if parts:
            classes.add(int(parts[0]))
    return classes


def image_for_label(images_dir: Path, label_path: Path) -> Path | None:
    for extension in [".jpg", ".jpeg", ".png"]:
        candidate = images_dir / f"{label_path.stem}{extension}"
        if candidate.exists():
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a small local evaluation set from YOLO labels.")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/ppe_yolo"))
    parser.add_argument("--assets", type=Path, default=Path("assets"))
    parser.add_argument("--output", type=Path, default=Path("evaluation/test_samples"))
    parser.add_argument("--per-category", type=int, default=12)
    parser.add_argument("--seed", type=int, default=88)
    args = parser.parse_args()

    random.seed(args.seed)
    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    candidates: dict[str, list[tuple[Path, set[int]]]] = defaultdict(list)
    for split in ["valid", "test", "train"]:
        labels_dir = args.dataset / "labels" / split
        images_dir = args.dataset / "images" / split
        if not labels_dir.exists() or not images_dir.exists():
            continue
        for label_path in labels_dir.glob("*.txt"):
            classes = label_classes(label_path)
            image_path = image_for_label(images_dir, label_path)
            if image_path is None:
                continue
            for category, matcher in CATEGORIES.items():
                if matcher(classes):
                    candidates[category].append((image_path, classes))

    manifest: list[dict[str, object]] = []
    for category, items in candidates.items():
        random.shuffle(items)
        category_dir = args.output / category
        category_dir.mkdir(parents=True, exist_ok=True)
        for index, (image_path, classes) in enumerate(items[: args.per_category], start=1):
            target = category_dir / f"{category}_{index:03d}{image_path.suffix.lower()}"
            shutil.copy2(image_path, target)
            manifest.append(
                {
                    "category": category,
                    "file": target.as_posix(),
                    "source": image_path.as_posix(),
                    "classes": sorted(classes),
                }
            )

    assets_dir = args.output / "real_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for image_path in sorted(args.assets.glob("sample*.jp*g")):
        target = assets_dir / image_path.name
        shutil.copy2(image_path, target)
        manifest.append(
            {
                "category": "real_assets",
                "file": target.as_posix(),
                "source": image_path.as_posix(),
                "classes": [],
            }
        )

    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created {len(manifest)} evaluation images in {args.output}")


if __name__ == "__main__":
    main()
