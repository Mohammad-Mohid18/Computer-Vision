# Face Detection & Recognition (YuNet + SFace)

A real-time face recognition system built with OpenCV's DNN face models:

- **[YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)** — detects faces in a frame and returns bounding boxes + 5 facial landmarks.
- **[SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface)** — turns a detected, aligned face into a 128-dimensional embedding (a numeric "fingerprint" of that face), which is then compared against a database of known people using cosine similarity.

No deep learning training is required — both models are pre-trained. You only need a handful of reference photos per person to "enroll" them.

## How it works

1. **Enrollment** — `face-embeddings.py` scans the `dataset/` folder (one subfolder per person, 3-5 photos each), detects the face in each photo, extracts its embedding, and appends a row to `face_db.csv`.
2. **Recognition** — `face-recognition.py` opens a live camera feed, detects faces frame-by-frame, extracts an embedding for each, and compares it against every row in `face_db.csv`. The closest match above a similarity threshold is labeled with the person's name; anything below the threshold is labeled `Unknown`.
3. `face-recognition.py` also supports **live enrollment** — press `e` while a face is on screen to add it to the database on the spot, without re-running the batch script.

## Project structure

```
Face-Detect+Recognize/
├── dataset/                                  # NOT committed to git (see .gitignore)
│   ├── PersonName1/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── img3.jpg
│   └── PersonName2/
│       ├── img1.jpg
│       └── img2.jpg
├── face_detection_yunet_2023mar.onnx          # detector model (download separately)
├── face_recognition_sface_2021dec.onnx        # recognizer model (download separately)
├── face-embeddings.py                         # batch enrollment script (dataset -> CSV)
├── face-recognition.py                        # live recognition + on-the-fly enrollment
├── face_db.csv                                # embeddings database (safe to commit)
├── .gitignore
└── README.md
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd Face-Detect+Recognize
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install opencv-python numpy
```

> If you ever see GUI windows not appearing, make sure `opencv-python-headless` isn't also installed alongside `opencv-python` — they conflict. Only `opencv-python` should be present:
> ```bash
> pip uninstall opencv-python-headless -y
> ```

### 3. Download the models

These `.onnx` files are too large/not meant for git and must be downloaded manually into the project root:

```bash
curl -L -o face_detection_yunet_2023mar.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx

curl -L -o face_recognition_sface_2021dec.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx
```

Verify both downloaded correctly (not an HTML error page or LFS pointer):

```bash
ls -lh face_detection_yunet_2023mar.onnx face_recognition_sface_2021dec.onnx
```
Expected sizes: detector ~230 KB, recognizer ~36 MB.

### 4. Build your dataset

dataset if needed: https://www.kaggle.com/datasets/atulanandjha/lfwpeople?resource=download

Create `dataset/<PersonName>/` for each person, with 3-5 clear photos:

- Mostly front-facing, slight head turns (±15-30°) are fine and actually help.
- Avoid full 90° profile shots — the aligner needs both eyes, nose, and mouth corners visible.
- Vary lighting/expression slightly across photos rather than using near-identical shots.

### 5. Generate embeddings

```bash
python face-embeddings.py --dataset dataset --output face_db.csv
```

This prints per-image progress and skips any photo where no face was detected. Re-run with `--append` to add new people later without wiping the existing CSV.

### 6. Run live recognition

```bash
python face-recognition.py
```

- **Green box + name + confidence score** → recognized face above the similarity threshold.
- **Red box + "Unknown"** → face detected but doesn't match anyone in the database closely enough.
- Press **`e`** to enroll the currently detected face on the spot (prompts for a name in the terminal).
- Press **`q`** or **`Esc`** to quit.

## Camera source

The camera index/source is set in `face-recognition.py`:

```python
webcam = cv2.VideoCapture(2)
```

This is **machine-specific** and may need to change:

| Value | Typical meaning |
|---|---|
| `0` | Laptop's built-in webcam (usually) |
| `1` | Next detected device — varies by OS/driver load order |
| `2` | DroidCam virtual camera, on this project's dev machine (Linux, via `v4l2loopback`) |
| `"http://<phone-ip>:4747/video"` | DroidCam network stream — works without any driver/kernel module, at the cost of slightly higher latency and typically capped resolution |

To find the right index on Linux:
```bash
v4l2-ctl --list-devices
```
This groups `/dev/video*` nodes by device name, so you can identify which index belongs to which camera. On Linux, DroidCam requires the `v4l2loopback` kernel module to be loaded (and may require disabling Secure Boot, since the module is often unsigned) before it will appear as a numbered camera device — otherwise, fall back to the URL stream method above.

## Tuning

- **`COSINE_THRESHOLD = 0.363`** in `face-recognition.py` — OpenCV's recommended threshold for SFace. Raise it to reduce false positives (stricter matching); lower it if real matches aren't being recognized (looser matching).
- **`score_threshold` / `nms_threshold`** in the `FaceDetectorYN.create(...)` call — controls how confident YuNet must be before reporting a detected face, and how it filters overlapping detections.

## Scaling beyond a CSV

`face_db.csv` stores one row per enrolled photo: `name, f0, f1, ..., f127`. This works well and stays fast (linear scan) for **tens to a few hundred people**. It's plain text, easy to inspect, and safe to commit to git since it contains no images — just numeric feature vectors.

If the database grows to **thousands of people**, or needs concurrent multi-process writes, consider migrating to:
- **SQLite** — same core idea (a `people` table with a name column and 128 float columns, or a serialized blob column), just swap `csv.reader`/`csv.writer` for `sqlite3` queries. Minimal code change.
- **A vector index (e.g., FAISS)** — for very large databases, to avoid a full linear scan on every recognition frame.

## What's committed to git vs. not

- **Committed:** `face-embeddings.py`, `face-recognition.py`, `face_db.csv`, `README.md`, `.gitignore`
- **Not committed:** `dataset/` (raw personal photos), the two `.onnx` model files (large binaries, downloadable separately), `venv/`

See `.gitignore` below.
