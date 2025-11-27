import os
import torch
from ultralytics import YOLO
from torch.serialization import add_safe_globals

from ultralytics.nn.tasks import DetectionModel
add_safe_globals([DetectionModel])

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/best.pt")
print("Checking YOLO model...")

def load_model():
    if os.path.exists(MODEL_PATH):
        print("Model already exists locally. Skipping download.")
        return YOLO(MODEL_PATH)
    else:
        raise FileNotFoundError(f"YOLO model not found at: {MODEL_PATH}")

print("Loading YOLO model...")
model = load_model()
print("Model loaded successfully.")

def predict_image(image_path):
    results = model(image_path)[0]

    predictions_clean = []
    for box in results.boxes:
        cls = int(box.cls.item())
        conf = float(box.conf.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        predictions_clean.append({
            "x": (x1 + x2) / 2,
            "y": (y1 + y2) / 2,
            "width": x2 - x1,
            "height": y2 - y1,
            "class": results.names[cls],
            "confidence": round(conf, 2)
        })

    return predictions_clean
