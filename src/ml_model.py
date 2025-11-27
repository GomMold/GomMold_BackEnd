import os
import requests
import torch
from ultralytics import YOLO

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")
MODEL_URL = os.getenv("MODEL_URL")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading model from Firebase...")
        response = requests.get(MODEL_URL, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download model: HTTP {response.status_code}")

        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)

        print("Download complete.")
    else:
        print("Model already exists locally. Skipping download.")

def load_model():
    print("Checking YOLO model...")
    download_model()

    print("Loading YOLO model...")

    torch.serialization.add_safe_globals([torch.nn.modules.container.Sequential])

    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully.")
    return model

model = load_model()

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
