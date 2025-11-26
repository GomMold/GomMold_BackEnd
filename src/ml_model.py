from ultralytics import YOLO
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/best.pt")

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
