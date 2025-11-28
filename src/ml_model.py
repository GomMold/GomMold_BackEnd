import os
import requests
import numpy as np
import cv2
import onnxruntime as ort

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.onnx")
MODEL_URL = os.getenv("MODEL_URL")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading ONNX model...")

        if not MODEL_URL:
            raise RuntimeError("MODEL_URL environment variable is not set")

        response = requests.get(MODEL_URL, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download model: HTTP", response.status_code)

        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)

        print("Download complete.")
    else:
        print("Model already exists. Skipping.")

def load_model():
    download_model()
    print("Loading ONNX model...")
    session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    print("ONNX model loaded successfully.")
    return session

session = load_model()

def preprocess_image(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError("Could not load image.")

    img_resized = cv2.resize(img, (640, 640))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_input = img_rgb.astype(np.float32) / 255.0
    img_input = np.transpose(img_input, (2, 0, 1))
    img_input = np.expand_dims(img_input, axis=0)

    return img_input, img.shape[1], img.shape[0]

def predict_image(image_path):
    img_input, orig_w, orig_h = preprocess_image(image_path)

    output = session.run(None, {session.get_inputs()[0].name: img_input})[0][0]

    boxes = []

    for pred in output:
        x1, y1, x2, y2 = pred[:4]
        obj_conf = pred[4]
        class_scores = pred[5:]

        cls = int(np.argmax(class_scores))
        cls_conf = class_scores[cls]

        score = obj_conf * cls_conf

        if score < 0.25:
            continue

        boxes.append({
            "x": float((x1 + x2) / 2),
            "y": float((y1 + y2) / 2),
            "width": float(x2 - x1),
            "height": float(y2 - y1),
            "class": cls,
            "confidence": round(float(score), 2)
        })

    return boxes