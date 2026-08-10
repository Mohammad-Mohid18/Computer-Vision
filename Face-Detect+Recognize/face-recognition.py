import os
import cv2
import numpy as np
import csv

script_dir = os.path.dirname(os.path.abspath(__file__))
detector_path = os.path.join(script_dir, "face_detection_yunet_2023mar.onnx")
recognizer_path = os.path.join(script_dir, "face_recognition_sface_2021dec.onnx")
db_path = os.path.join(script_dir, "face_db.csv")

detector = cv2.FaceDetectorYN.create(model=detector_path, config="", input_size=(640, 480),
                                      score_threshold=0.5, nms_threshold=0.3)
recognizer = cv2.FaceRecognizerSF.create(model=recognizer_path, config="")

COSINE_THRESHOLD = 0.363


def load_db():
    db = []  # list of (name, embedding np.array)
    if os.path.exists(db_path):
        with open(db_path, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                name = row[0]
                vec = np.array([float(x) for x in row[1:]], dtype=np.float32)
                db.append((name, vec))
    return db


def save_entry(name, embedding):
    file_exists = os.path.exists(db_path)
    with open(db_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name"] + [f"f{i}" for i in range(embedding.shape[0])])
        writer.writerow([name] + embedding.flatten().tolist())


def get_embedding(img, face_row):
    aligned = recognizer.alignCrop(img, face_row)
    return recognizer.feature(aligned)


def match(feature, db):
    best_name, best_score = None, -1
    for name, db_feature in db:
        score = recognizer.match(feature, db_feature, cv2.FaceRecognizerSF_FR_COSINE)
        if score > best_score:
            best_name, best_score = name, score
    if best_score >= COSINE_THRESHOLD:
        return best_name, best_score
    return None, best_score


face_db = load_db()

#url = "http://192.168.18.208:4747/video"

webcam = cv2.VideoCapture(2)
detector.setInputSize((640, 480))
print("Press 'e' to enroll detected face, 'q'/ESC to quit.")

while True:
    ret, img = webcam.read()
    if not ret or img is None:
        continue

    h, w, _ = img.shape
    detector.setInputSize((w, h))
    _, faces = detector.detect(img)

    current_face = None
    if faces is not None:
        for face in faces:
            current_face = face
            box = face[0:4].astype(int)
            feature = get_embedding(img, face)
            name, score = match(feature, face_db)

            label = f"{name} ({score:.2f})" if name else f"Unknown ({score:.2f})"
            color = (0, 255, 0) if name else (0, 0, 255)
            cv2.rectangle(img, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), color, 2)
            cv2.putText(img, label, (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Face Recognition (YuNet + SFace)", img)
    key = cv2.waitKey(10) & 0xFF
    if key in (27, ord('q')):
        break
    elif key == ord('e') and current_face is not None:
        name = input("Enter name for this face: ").strip()
        if name:
            feature = get_embedding(img, current_face)
            save_entry(name, feature)
            face_db.append((name, feature))
            print(f"Enrolled '{name}'")

webcam.release()
cv2.destroyAllWindows()