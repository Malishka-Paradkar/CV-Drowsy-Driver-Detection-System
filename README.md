# CV-Drowsy-Driver-Detection-System
# Drowsy Driver Detection System

A real-time computer vision system that monitors a driver's eyes via webcam and triggers an audio alert when drowsiness is detected — before an accident happens.

---

## Problem Statement

Driver drowsiness is responsible for a significant number of road accidents worldwide. Most drivers don't realise they are falling asleep until it's too late. This project addresses that gap by providing a low-cost, webcam-based early-warning system.

---

## How It Works

The system uses the **Eye Aspect Ratio (EAR)** — a simple yet effective metric:

```
         ‖p2−p6‖ + ‖p3−p5‖
EAR =  ─────────────────────
             2 · ‖p1−p4‖
```

- When eyes are **open**, EAR ≈ 0.30
- When eyes are **closed**, EAR drops below 0.25
- If EAR stays below the threshold for **20 consecutive frames** → alert fires

MediaPipe FaceMesh provides 468 facial landmarks at real-time speed, from which 12 eye-contour points (6 per eye) are extracted each frame.

---

## Project Structure

```
drowsy-driver-detection/
├── main.py          # Detection loop + webcam HUD
├── ear_utils.py     # EAR formula & landmark extraction
├── alert.py         # Audio alert (pygame / playsound / OS beep)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/drowsy-driver-detection.git
cd drowsy-driver-detection
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Python 3.9+** required. Tested on Windows 11, Ubuntu 22.04, macOS 13.

---

## Usage

```bash
# Basic — uses default webcam (index 0)
python main.py

# Different camera
python main.py --camera 1

# Hide landmark dots on eyes
python main.py --no-landmarks
```

### Controls
| Key | Action |
|-----|--------|
| `q` | Quit |

---

## HUD Explanation

| Element | Meaning |
|---------|---------|
| **Status** | AWAKE / DROWSY! / NO FACE |
| **EAR** | Current Eye Aspect Ratio (live value vs threshold) |
| **Progress bar** | Fills red as eyes stay closed — alert fires when full |
| **FPS** | Frames per second being processed |

---

## Tuning Parameters

Edit the constants at the top of `main.py`:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `EAR_THRESHOLD` | `0.25` | Lower → less sensitive; raise if false positives |
| `CONSEC_FRAMES` | `20` | Frames (~0.7 s at 30 fps) before alert triggers |
| `ALERT_COOLDOWN` | `3.0` | Seconds between repeated alerts |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `opencv-python` | Webcam capture & frame rendering |
| `mediapipe` | Face mesh & landmark detection |
| `pygame` | Audio alert playback |

---

## Limitations

- Requires good lighting and a front-facing camera
- May not work well with some glasses or extreme head angles
- Not a substitute for professional driver-monitoring hardware

---

## License

MIT — free to use, modify, and distribute.
