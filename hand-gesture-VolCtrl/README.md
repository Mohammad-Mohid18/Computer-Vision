# 🖐️ Hand Gesture System Volume Control (Linux / Wayland)

A real-time Computer Vision application that lets you control your Linux system volume using natural hand gestures via webcam. 

Built using **OpenCV** for camera handling, **Google MediaPipe** for hand landmark tracking, and **PipeWire (`wpctl`)** for native Linux audio control on Wayland desktop environments.

---

## 🌟 Features

* **Real-Time Hand Landmark Detection:** Accurately tracks index finger and thumb tip positions frame-by-frame.
* **Euclidean Distance Measurement:** Dynamically measures the pixel gap between fingertips to trigger volume shifts.
* **Wayland & PipeWire Native:** Bypasses X11 display security restrictions and works out-of-the-box on modern Linux desktops without requiring `sudo` privileges.
* **On-Screen HUD:** Displays live numerical distance readouts and active `VOL UP` / `VOL DOWN` status indicators directly on the video feed.
* **Keypress Debouncing:** Throttles signal updates to prevent overwhelming the system audio server.

---

## 💻 System Compatibility & Prerequisites

### Tested Environment
* **OS:** Ubuntu 22.04 LTS / 24.04 LTS / 26.04 LTS
* **Display Server:** Wayland
* **Audio Server:** PipeWire / WirePlumber (`wpctl`)
* **Python Version:** Python 3.10 or 3.11
* **Hardware:** Any standard USB or integrated camera

### Python Dependencies
* `opencv-python` (>= 4.8.0)
* `mediapipe` (>= 0.10.9)
* `protobuf` (>= 3.20.3, < 4.24)

---

## 📥 Installation & Setup

1. **Clone the Repository:**
   Open your terminal and clone this repository to your local directory:
   `git clone https://github.com/your-username/hand-gesture-VolCtrl.git`
   `cd hand-gesture-VolCtrl`

2. **Create a Virtual Environment:**
   `python3 -m venv venv`
   `source venv/bin/activate`

3. **Install Required Packages:**
   `pip install opencv-python "mediapipe>=0.10.9" "protobuf>=3.20.3,<4.24"`

---

## 🚀 How to Run

Execute the main script within your active virtual environment:

`python hand-volume-control.py`

> **Note:** Do NOT run the script using `sudo`. Running as `root` will prevent the script from connecting to your user account's Wayland display server and PipeWire audio session.

---

## 🖐️ Gesture Controls & Thresholds

| Gesture Action | Distance Threshold | System Action | Visual Feedback |
| :--- | :--- | :--- | :--- |
| **Open Pinch** (Fingers Wide) | Distance > 80 pixels | Volume Increases by 5% | Green `VOL UP` indicator |
| **Closed Pinch** (Fingers Together) | Distance < 30 pixels | Volume Decreases by 5% | Red `VOL DOWN` indicator |
| **Neutral Position** | 30 <= Distance <= 80 | No Change | Distance value only |

To close the application, press the `ESC` key while focusing on the video preview window.

---

## 🧠 How It Works Behind the Scenes

1. **Frame Capture & Normalization:** OpenCV reads raw frames from the webcam, horizontally flips them for a natural mirror effect, and converts BGR color spaces to RGB.
2. **Landmark Extraction:** MediaPipe Hand Landmarker processes the RGB frame and detects 21 distinct 3D landmarks on the detected hand.
3. **Keypoint Mapping:** The application targets **Landmark 8** (Index Finger Tip) and **Landmark 4** (Thumb Tip) and maps their normalized coordinates to pixel locations on your screen:
   * $x = \text{landmark.x} \times \text{frame\_width}$
   * $y = \text{landmark.y} \times \text{frame\_height}$
4. **Euclidean Distance Computation:** The spatial gap between the two fingertips is calculated:
   $$\text{Distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
5. **System Signal Execution:** When the calculated distance crosses designated thresholds, a background subprocess invokes Linux's native WirePlumber command (`wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+` or `5%-`).

---

## 🔧 Troubleshooting

* **AttributeError: module 'mediapipe' has no attribute 'solutions':**
  This usually happens due to package file corruption or conflicting older builds. Fix it by running:
  `pip uninstall -y mediapipe protobuf`
  `pip install "protobuf>=3.20.3,<4.24" mediapipe==0.10.9`

* **Volume is not changing on Wayland:**
  Verify that your terminal session has active WirePlumber tools by running `wpctl status` in your terminal. Ensure the Python script is launched without `sudo`.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.