import cv2

cap = cv2.VideoCapture(0)
opened = cap.isOpened()
if opened:
    while (opened):
        ret, frame = cap.read()
        if ret == True:
            cv2.imshow('frame', frame)
            if cv2.waitKey(2)==27:
                break