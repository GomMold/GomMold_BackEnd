import os
import requests
import numpy as np
import cv2
import onnxruntime as ort

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")
MODEL_URL = os.getenv("MODEL_URL")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading ONNX model...")

        if not MODEL_URL:
            raise RuntimeError("MODEL_URL environment variable is not set")

        response = requests.get(MODEL_URL, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download model: HTTP {response.status_code}")

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

    outputs = session.run(None, {session.get_inputs()[0].name: img_input})
    preds = outputs[0]
    preds = preds.squeeze()

    boxes = []

    xywh = preds[:4, :]
    obj_conf = preds[4, :]
    cls_conf = preds[5:, :] 

    cls_ids = np.argmax(cls_conf, axis=0)
    cls_scores = cls_conf[cls_ids, np.arange(cls_conf.shape[1])]

    final_scores = obj_conf * cls_scores

    keep = final_scores > 0.25

    for i in np.where(keep)[0]:
        x, y, w, h = xywh[:, i]

        boxes.append({
            "x": float(x),
            "y": float(y),
            "width": float(w),
            "height": float(h),
            "class": int(cls_ids[i]),
            "confidence": round(float(final_scores[i]), 3)
        })

    return boxes