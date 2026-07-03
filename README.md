<div align="center">

# 🍺 Tangent Connect — AI Vision Beverage Detection System

**Real-time beverage identification, classification & counting powered by YOLOv8**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

</div>

---

## 📌 Overview

A local, offline Windows desktop application that connects to a camera (webcam, RTSP/IP camera, or video file), detects beverages in real time with a fine‑tuned **YOLOv8** model, classifies each item as **alcoholic / non‑alcoholic**, tracks and counts unique items, and lets you retrain the model on new products through a built‑in wizard — no coding required.

---
## 📸 Screenshots
 
<div align="center">
<img width="1356" height="910" alt="Screenshot 2026-02-09 104301" src="https://github.com/user-attachments/assets/771148d5-aea8-46d1-aaf4-78d1783ee9a3" />
<img width="1112" height="633" alt="Screenshot 2026-02-09 160907" src="https://github.com/user-attachments/assets/08717fe3-5d7e-4574-9bd4-93ca7aaf699a" />

</div>

## 🎬 Demo
 
<div align="center">

https://github.com/user-attachments/assets/3863fd66-dfed-4c40-a84f-fdd61e5c0326

</div>
---

## ✨ Features

- 🎥 **Multi-source input** — Webcam, RTSP/IP camera, video file, or built‑in demo mode
- 🧠 **AI detection** — Fine‑tuned YOLOv8 model, confidence scoring, custom class support
- 🏷️ **Classification** — Auto-tags each detection as alcoholic (red) or non‑alcoholic (green)
- 🔢 **Smart counting** — Centroid-based tracking prevents duplicate counts
- 🖥️ **Live overlay UI** — Bounding boxes, labels, and running totals on screen
- 🎓 **No-code training wizard** — Add new products and retrain the model from the UI
- 💾 **Data persistence** — SQLite session storage + one-click CSV export
- 🔌 **100% offline** — No cloud dependency, all processing runs locally

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Detection | YOLOv8 (Ultralytics) |
| Vision / Streaming | OpenCV |
| GUI | Tkinter + ttkbootstrap |
| Storage | SQLite, Pandas, CSV |
| Language | Python 3.9+ |

---

## 📁 Project Structure

```
tangent-connect-ai-vision/
├── main.py                    # Application entry point
├── RUN_APP.bat                # One-click Windows launcher
├── requirements.txt           # Python dependencies
├── config/
│   └── settings.py            # Detection, camera, tracking & UI settings
├── src/
│   ├── camera/                # Stream handling (webcam / RTSP / file)
│   ├── detection/              # YOLO inference wrapper
│   ├── tracking/               # Centroid object tracker
│   ├── gui/                    # Application window & controls
│   └── database/               # SQLite persistence layer
├── training_wizard.py         # Guided UI for training custom models
├── demo_video.py               # Simulated feed for demo mode
├── test_camera.py              # Camera connectivity diagnostic tool
├── models/                     # Trained model weights (.pt) — see note below
├── data/                       # Runtime database & dataset configs
├── exports/                    # CSV exports
├── docs/                       # Extended guides
└── assets/
    └── app_logo.jpg
```

> **Note:** Model weight files (`.pt`), training image sets, and `runs/` experiment logs are excluded from version control (see [`.gitignore`](#-gitignore)) — download or regenerate them via the training wizard, or attach them as a [GitHub Release](../../releases) / Git LFS asset.

---

## 🚀 Getting Started

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.9+
- Webcam or RTSP camera (optional — demo mode needs neither)

### Installation
```bash
git clone https://github.com/<your-username>/tangent-connect-ai-vision.git
cd tangent-connect-ai-vision
pip install -r requirements.txt
```

### Run
```bash
python main.py
```
or double-click **`RUN_APP.bat`** on Windows.

---

## 🕹️ Usage

1. Choose a camera source: **Webcam / Demo / RTSP / Video File**
2. Click **Connect**, then **▶ Start** to begin detection
3. View live bounding boxes, labels, and per-type counts
4. **File → Export** to save session data as CSV
5. **Model → Train New Model** to teach the system new products

---

## ⚙️ Configuration

Key parameters live in `config/settings.py`:

```python
CONFIDENCE_THRESHOLD = 0.25   # Detection sensitivity
IOU_THRESHOLD = 0.45          # Non-max suppression
TRACKING_MAX_DISTANCE = 50    # Tracking match distance (px)
BEVERAGE_CLASSES = {...}      # Custom product classes
```

---

## 🧩 Training a Custom Model

1. `Model` → `Train New Model`
2. Select/capture a labeled image set
3. Set epochs, batch size & image size
4. Start training — the wizard handles the YOLO fine-tuning pipeline
5. `Model` → `Load Custom Model` to activate the new weights

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---
