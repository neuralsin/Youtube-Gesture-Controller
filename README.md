# YouTube Gesture Controller

Control YouTube videos with just your hands. No mouse, no keyboard—just pure gesture-powered magic using computer vision and AI.

![demo](assets/demo.gif)

---

## Features

- Real-time hand tracking with MediaPipe
- Predefined gestures:
  - **Open palm** → Play
  - **Fist** → Pause
  - **Index + Middle** → Volume Up
  - **Ring + Pinky** → Volume Down
  - **Pinky only** → Next Video
  - **All but Pinky** → Previous Video
- Custom gesture training
- PiP hand-skeleton overlay for live feedback
- Cooldown to avoid repeated actions

---

## Tech Stack

- **Python**
- **OpenCV** – camera + drawing
- **MediaPipe** – hand landmark detection
- **PyAutoGUI** – keyboard emulation
- **NumPy** – landmark math
- **Pickle** – save custom gestures

---

## Setup Instructions

```bash
git clone https://github.com/neuralsin/Youtube-Gesture-Controller
cd YouTubeGestureController/src
pip install -r ../requirements.txt
python main.py
