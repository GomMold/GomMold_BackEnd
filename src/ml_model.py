
import os
import cv2
import requests
import numpy as np
import onnxruntime as ort

print("DEBUG MODEL_URL =", os.getenv("MODEL_URL"))


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.onnx")
MODEL_URL = os.getenv("MODEL_URL")

os.makedirs(MODEL_DIR, exist_ok=True)


# 1. Download ONNX model

def download_model():
    if os.path.exists(MODEL_PATH):
        print("ONNX model already exists. Skipping download.")
        return

    if not MODEL_URL:
        raise RuntimeError("MODEL_URL environment variable is not set")

    print("Downloading ONNX model...")

    r = requests.get(MODEL_URL, stream=True)

    if r.status_code != 200:
        raise RuntimeError(f"Failed to download model: HTTP {r.status_code}")

    with open(MODEL_PATH, "wb") as f:
        f.write(r.content)

    print("Model download complete.")


# 2. Load ONNX model

def load_model():
    download_model()

    print("Loading ONNX model...")
    session = ort.InferenceSession(
        MODEL_PATH, providers=["CPUExecutionProvider"]
    )
    print("Model loaded successfully.")
    return session


session = load_model()

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name


# 3. Preprocess image

def preprocess_image(image_path, img_size=640):
    img = cv2.imread(image_path)
    h0, w0 = img.shape[:2]

    img_resized = cv2.resize(img, (img_size, img_size))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_norm = img_rgb / 255.0
    img_transposed = np.transpose(img_norm, (2, 0, 1))
    img_input = img_transposed[np.newaxis, :, :, :].astype(np.float32)

    return img_input, w0, h0


# 4. Predict using ONNX

def predict_image(image_path):
    img_input, orig_w, orig_h = preprocess_image(image_path)

    outputs = session.run([output_name], {input_name: img_input})[0]

    # Ensure shape is [1, N, 6]
    if outputs.shape[-1] != 6:
        outputs = np.transpose(outputs, (0, 2, 1))

    detections = []

    for det in outputs[0]:
        x, y, w, h, obj_conf, cls_conf = det

        # For 1-class model: final confidence = obj_conf * cls_conf
        conf = float(obj_conf * cls_conf)

        if conf < 0.25:
            continue

        # Convert xywh to xyxy
        x1 = float((x - w / 2) * orig_w / 640)
        y1 = float((y - h / 2) * orig_h / 640)
        x2 = float((x + w / 2) * orig_w / 640)
        y2 = float((y + h / 2) * orig_h / 640)

        detections.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "confidence": conf,
            "class": 0   # Always class 0 (mold)
        })

    return detections
