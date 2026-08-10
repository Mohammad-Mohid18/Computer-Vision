import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# webcam = cv2.VideoCapture("http://192.168.18.208:8080/video")   # IP Camera
# webcam = cv2.VideoCapture(0)      # Laptop Camera
webcam = cv2.VideoCapture(1)        # Driod Camera (best)

webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    _, img = webcam.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #convert to grayscale

    gray_boosted = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray_boosted, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30)
    )   #detect faces
    
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)   # mark the face with a rectangle

    cv2.imshow("Face detection", img)
    key = cv2.waitKey(10)
    if key == 27:    #ascii code for ESC key
        break

webcam.release()
cv2.destroyAllWindows()