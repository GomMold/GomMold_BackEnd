import os
import requests
from ultralytics import YOLO
import cv2
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")
MODEL_URL = os.getenv("MODEL_URL")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading PyTorch model (.pt)...")

        if not MODEL_URL:
            raise RuntimeError("MODEL_URL environment variable is not set")

        r = requests.get(MODEL_URL, stream=True)
        if r.status_code != 200:
            raise Exception(f"Failed to download model: {r.status_code}")

        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)

        print("Download complete.")
    else:
        print("Model already exists, skipping.")

def load_model():
    download_model()

    print("Loading YOLOv8 PyTorch model (.pt)...")
    model = YOLO(MODEL_PATH)
    print("Model loaded successfully.")
    return model

model = load_model()

def predict_image(image_path):
    results = model(image_path, conf=0.25)[0]

    detections = []
    for box in results.boxes:
        detections.append({
            "x1": float(box.xyxy[0][0]),
            "y1": float(box.xyxy[0][1]),
            "x2": float(box.xyxy[0][2]),
            "y2": float(box.xyxy[0][3]),
            "class": int(box.cls[0]),
            "confidence": float(box.conf[0])
        })
    return detections