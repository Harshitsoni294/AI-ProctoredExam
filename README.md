# 🧠 AI-Proctored Exam System

A real-time **AI-powered proctoring system** that ensures exam integrity by detecting mobile devices, monitoring head pose, and analyzing gaze direction using advanced computer vision models.

[![GitHub Repo](https://img.shields.io/badge/GitHub-Harshitsoni294%2FAI--ProctoredExam-blue?logo=github)](https://github.com/Harshitsoni294/AI-ProctoredExam)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Enabled-green?logo=opencv)
![YOLOv12](https://img.shields.io/badge/YOLOv12-Object_Detection-orange?logo=yolo)
![dlib](https://img.shields.io/badge/dlib-Facial_Landmarks-lightgrey)

---

## 🚀 Overview

The **AI-Proctored Exam System** automatically detects cheating behavior in online tests by analyzing:
- **Head & Eye Movement** (using dlib Shape Predictor 68)
- **Mobile Phone Detection** (using custom-trained YOLOv12)
- **Real-Time Monitoring & Alerts**

It provides a GUI-based interface for registration, calibration, and continuous monitoring.

---
## 🖥️ Interface Overview

### 🔹 Registration Window
The user enters their details before beginning the test.  
![ac279bf49f39405782f72711132dc1b6](https://github.com/user-attachments/assets/08983443-4f72-4cb3-ae54-03812f901897)


---

### 🔹 Eye Calibration
Performs initial eye-tracking calibration to establish gaze direction baselines.  
![887d7b8089254946ad84c24b51bf64d4](https://github.com/user-attachments/assets/d475de18-804b-44d7-a2ac-109582ecfb9c)


---

### 🔹 Real-Time Detection
Displays gaze direction, head orientation, and mobile detection results on screen.  
![85e805f332f042b89e15312fb510bb4a](https://github.com/user-attachments/assets/1e872056-f7e0-40cd-ba02-3f76a62e6c22)


---

### 🔹 Terminal Log Output
Every event and detected anomaly is logged with screenshot evidence.  
![1bca6dfb33b74052b025c4b52c3a20c7](https://github.com/user-attachments/assets/bf490644-5f8b-498b-bdee-8e51609c4a46)


---

## 🧩 Features

✅ **Head and Pupil Movement Detection**  
Tracks facial landmarks and analyzes gaze direction (left, right, up, down, center).  

✅ **Mobile Phone Detection (YOLOv12)**  
Detects presence of mobile phones using a YOLOv12 model trained on the [Roboflow Cellphone Dataset](https://universe.roboflow.com/d1156414/cellphone-0aodn).  

✅ **Real-Time Monitoring & Logging**  
Processes webcam feed and stores screenshots of flagged frames in `/log/`.  

✅ **User-Friendly GUI**  
PySimpleGUI interface for exam registration and calibration.  

✅ **Automated Alerts**  
Generates instant warnings or session termination upon detecting cheating behavior.

---


## 🧠 Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Programming Language** | Python 3.8+ |
| **Computer Vision** | OpenCV, dlib |
| **Object Detection** | YOLOv12 |
| **Model Dataset** | Roboflow Cellphone Detection |
| **Interface** | PySimpleGUI |
| **Logging** | OpenCV & OS I/O |

---

## ⚙️ Folder Structure

```
AI-ProctoredExam/
│── models/                 # Trained YOLO weights & dlib model  
│   ├── best_yolov12.pt
│   ├── shape_predictor_68_face_landmarks.dat
│── log/                    # Screenshots of violations
│── main.py                 # Entry point for detection system
│── head_pose.py            # Head orientation detection
│── eye_movement.py         # Gaze tracking module
│── mobile_detection.py     # YOLO-based mobile detection
│── requirements.txt        # Dependencies
│── README.md               # Project documentation
```

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Webcam
- Internet connection (for dataset/model download)

### Steps
```bash
# Clone repository
git clone https://github.com/Harshitsoni294/AI-ProctoredExam.git
cd AI-ProctoredExam

# Install dependencies
pip install -r requirements.txt

# Download dlib model
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
mv shape_predictor_68_face_landmarks.dat models/

# Add trained YOLO weights
# (download from Roboflow and place in models/)
```

---

## ▶️ Usage

Run the main application:

```bash
python main.py
```

System flow:
1. User registers in GUI  
2. Eye calibration begins  
3. Exam monitoring starts  
4. Alerts appear for gaze deviation or mobile detection  
5. Screenshots saved automatically in `/log/`

---

## 📊 Model Training Details

The YOLOv12 model was **trained from scratch** on the  
[Roboflow Cellphone Detection Dataset](https://universe.roboflow.com/d1156414/cellphone-0aodn)  
with:
- **10,000+ labeled images**
- **Batch size:** 16  
- **Epochs:** 100  
- **Accuracy:** ~95% mAP  
- **Framework:** PyTorch (Ultralytics YOLOv12)

---

## 📸 Demo Videos

- 🎥 [Gaze Detection Demo](https://github.com/Sania-hasann/Cheating-Surveillance-System/blob/main/Demo_vid/gaze_detection.mp4)  
- 🎥 [Head Movement Detection](https://github.com/Sania-hasann/Cheating-Surveillance-System/blob/main/Demo_vid/headpose_detection.mp4)  
- 🎥 [Mobile Detection](https://github.com/Sania-hasann/Cheating-Surveillance-System/blob/main/Demo_vid/Mobile-detection.mp4)

---

## 🧑‍💻 Author

**Harshit Soni**  
📧 harshitsoni2026@gmail.com  
🔗 [GitHub Profile](https://github.com/Harshitsoni294)

---

## 🪪 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

### 🌟 Acknowledgments
- [dlib](http://dlib.net/)  
- [OpenCV](https://opencv.org/)  
- [Ultralytics YOLO](https://github.com/ultralytics/yolov5)  
- [Roboflow](https://roboflow.com/) for dataset support

---

⭐ **If you like this project, give it a star on GitHub!**
