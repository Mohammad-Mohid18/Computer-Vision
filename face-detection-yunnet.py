import cv2

# Load YuNet DNN Model
detector = cv2.FaceDetectorYN.create(
    model="face_detection_yunet_2023mar.onnx",
    config="",
    input_size=(640, 480),
    score_threshold=0.5, 
    nms_threshold=0.3
)

webcam = cv2.VideoCapture(1)

# Set initial input size
detector.setInputSize((640, 480))

while True:
    ret, img = webcam.read()
    if not ret or img is None:
        continue

    h, w, _ = img.shape
    detector.setInputSize((w, h))

    # Deep Learning Face Detection
    _, faces = detector.detect(img)

    if faces is not None:
        for face in faces:
            box = face[0:4].astype(int)
            cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 255, 0), 2)
            
            confidence = face[-1]
            cv2.putText(img, f"{confidence:.2f}", (box[0], box[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("OpenCV Deep Learning Detection (YuNet)", img)

    if cv2.waitKey(10) == 27:
        break

webcam.release()
cv2.destroyAllWindows()