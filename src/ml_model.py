import os
import requests
from ultralytics import YOLO

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")

MODEL_URL = os.getenv("MODEL_URL")

def download_model():
    if os.path.exists(MODEL_PATH):
        print("Model already exists locally. Skipping download.")
        return

    if not MODEL_URL:
        raise ValueError("MODEL_URL environment variable not set.")

    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Downloading model from: {MODEL_URL}")
    
    response = requests.get(MODEL_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download model. Status: {response.status_code}")

    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print("Model downloaded and saved at:", MODEL_PATH)

print("Checking YOLO model...")

download_model()

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
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
