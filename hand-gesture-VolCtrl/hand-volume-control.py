import cv2
import subprocess
import mediapipe as mp

webcam = cv2.VideoCapture(0)
my_hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
drawing_utils = mp.solutions.drawing_utils

def set_volume(action):
    """Native Wayland / PipeWire audio control for Ubuntu."""
    if action == "up":
        # Increases default audio sink volume by 5%
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+" ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif action == "down":
        # Decreases default audio sink volume by 5%
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-" ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

frame_counter = 0 

while True:
    _, image = webcam.read()
    if image is None:
        break

    image = cv2.flip(image, 1)
    frame_height, frame_width, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output = my_hands.process(rgb_image)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            drawing_utils.draw_landmarks(image, hand)
            landmarks = hand.landmark
            
            x1, y1 = 0, 0
            x2, y2 = 0, 0

            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                # Index Finger Tip (ID 8)
                if id == 8:
                    cv2.circle(img=image, center=(x, y), radius=10, color=(0, 255, 0), thickness=-1)
                    x1, y1 = x, y

                # Thumb Tip (ID 4)
                if id == 4:
                    cv2.circle(img=image, center=(x, y), radius=10, color=(0, 0, 255), thickness=-1)
                    x2, y2 = x, y

            if x1 != 0 and x2 != 0:
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
                
                # Raw pixel distance calculation
                dist = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)

                # Show live distance on feed for calibration
                cv2.putText(image, f"Distance: {dist}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                frame_counter += 1
                # Trigger action every 3 frames to avoid overwhelming audio daemon
                if frame_counter % 3 == 0:
                    if dist > 110:  # Pinch wide -> Volume Up
                        set_volume("up")
                        cv2.putText(image, "VOL UP", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    elif dist < 80: # Pinch closed -> Volume Down
                        set_volume("down")
                        cv2.putText(image, "VOL DOWN", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand volume control using python", image)
    key = cv2.waitKey(10)
    if key == 27:  # ESC key
        break

webcam.release()
cv2.destroyAllWindows()