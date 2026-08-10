import cv2   # type: ignore[import]

for index in range(4):
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"[SUCCESS] Camera index {index} is working!")
            cap.release()
            break
        cap.release()
    print(f"[FAILED] Camera index {index} failed.")