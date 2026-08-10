"""
build_face_db.py
-----------------
Scans a folder of face photos organized as:

    dataset/
        PersonName1/
            img1.jpg
            img2.jpg
        PersonName2/
            img1.jpg
            ...

For every image, detects the (largest) face with YuNet, extracts a 128-d
embedding with SFace, and appends a row [name, f0, f1, ..., f127] to a CSV
file. This CSV becomes the database used by your recognition script.

Usage:
    python build_face_db.py --dataset dataset --output face_db.csv

Requirements:
    pip install opencv-python numpy
    Place these two model files next to this script (or pass --detector /
    --recognizer paths):
        face_detection_yunet_2023mar.onnx
        face_recognition_sface_2021dec.onnx
"""

import os
import csv
import argparse
import cv2
import numpy as np

VALID_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def build_models(detector_path, recognizer_path):
    detector = cv2.FaceDetectorYN.create(
        model=detector_path,
        config="",
        input_size=(320, 320),   # will be resized per-image below
        score_threshold=0.5,
        nms_threshold=0.3,
        top_k=5000,
    )
    recognizer = cv2.FaceRecognizerSF.create(model=recognizer_path, config="")
    return detector, recognizer


def get_largest_face(detector, img):
    """Detect faces in img and return the row for the largest one (or None)."""
    h, w = img.shape[:2]
    detector.setInputSize((w, h))
    _, faces = detector.detect(img)
    if faces is None or len(faces) == 0:
        return None
    # pick the face with the largest bounding box area (w * h)
    areas = faces[:, 2] * faces[:, 3]
    best_idx = int(np.argmax(areas))
    return faces[best_idx]


def process_dataset(dataset_dir, detector, recognizer, min_side=0):
    """
    Walk dataset_dir/<person_name>/<image files> and yield
    (person_name, embedding, image_path) for every image where a face
    was found.
    """
    people = sorted(
        d for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d))
    )

    if not people:
        print(f"No subfolders found in '{dataset_dir}'. "
              f"Expected structure: {dataset_dir}/PersonName/photo.jpg")
        return

    for person in people:
        person_dir = os.path.join(dataset_dir, person)
        image_files = sorted(
            f for f in os.listdir(person_dir)
            if f.lower().endswith(VALID_EXTS)
        )

        if not image_files:
            print(f"  [!] No images found for '{person}', skipping.")
            continue

        print(f"Processing '{person}' ({len(image_files)} images)...")

        for fname in image_files:
            fpath = os.path.join(person_dir, fname)
            img = cv2.imread(fpath)

            if img is None:
                print(f"    [!] Could not read '{fname}', skipping.")
                continue

            if min_side and min(img.shape[:2]) < min_side:
                print(f"    [!] '{fname}' too small, skipping.")
                continue

            face_row = get_largest_face(detector, img)
            if face_row is None:
                print(f"    [!] No face detected in '{fname}', skipping.")
                continue

            aligned = recognizer.alignCrop(img, face_row)
            embedding = recognizer.feature(aligned)  # shape (1, 128) float32

            print(f"    [OK] '{fname}' -> embedding extracted")
            yield person, embedding.flatten(), fpath


def write_csv(rows, output_path, append=False):
    """rows: iterable of (name, embedding_array)."""
    mode = "a" if append and os.path.exists(output_path) else "w"
    write_header = not (mode == "a")

    with open(output_path, mode, newline="") as f:
        writer = csv.writer(f)
        count = 0
        for name, embedding, _src in rows:
            if write_header:
                writer.writerow(["name"] + [f"f{i}" for i in range(embedding.shape[0])])
                write_header = False
            writer.writerow([name] + embedding.tolist())
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Build a face-embedding CSV database from labeled photos.")
    parser.add_argument("--dataset", default="dataset",
                         help="Path to dataset folder (default: ./dataset)")
    parser.add_argument("--output", default="face_db.csv",
                         help="Output CSV path (default: ./face_db.csv)")
    parser.add_argument("--detector", default="face_detection_yunet_2023mar.onnx",
                         help="Path to YuNet .onnx model")
    parser.add_argument("--recognizer", default="face_recognition_sface_2021dec.onnx",
                         help="Path to SFace .onnx model")
    parser.add_argument("--append", action="store_true",
                         help="Append to an existing CSV instead of overwriting it")
    parser.add_argument("--min-side", type=int, default=0,
                         help="Skip images smaller than this on their shortest side (optional)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    detector_path = args.detector if os.path.isabs(args.detector) else os.path.join(script_dir, args.detector)
    recognizer_path = args.recognizer if os.path.isabs(args.recognizer) else os.path.join(script_dir, args.recognizer)

    for p, label in [(detector_path, "detector"), (recognizer_path, "recognizer")]:
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"Could not find {label} model at '{p}'. "
                f"Download it from the OpenCV Zoo and place it next to this script, "
                f"or pass --{label} <path>."
            )

    if not os.path.isdir(args.dataset):
        raise FileNotFoundError(
            f"Dataset folder '{args.dataset}' not found. "
            f"Create it with one subfolder per person, each containing their photos."
        )

    detector, recognizer = build_models(detector_path, recognizer_path)

    rows = list(process_dataset(args.dataset, detector, recognizer, args.min_side))

    if not rows:
        print("\nNo embeddings were generated. Check that your dataset folder "
              "has subfolders per person with readable images containing visible faces.")
        return

    count = write_csv(rows, args.output, append=args.append)

    people_counts = {}
    for name, _emb, _src in rows:
        people_counts[name] = people_counts.get(name, 0) + 1

    print(f"\nDone. Wrote {count} embedding(s) to '{args.output}'.")
    for name, n in sorted(people_counts.items()):
        print(f"  - {name}: {n} embedding(s)")


if __name__ == "__main__":
    main()