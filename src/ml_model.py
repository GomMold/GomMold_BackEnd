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
            raise Exception(f"Failed to download model: HTTP {response.status_code}")

        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)

        print("Download complete.")
    else:
        print("Model already exists. Skipping download.")

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

    h0, w0 = img.shape[:2]

    size = 640
    r = min(size / h0, size / w0)
    new_unpad = (int(w0 * r), int(h0 * r))

    img_resized = cv2.resize(img, new_unpad)
    dw, dh = size - new_unpad[0], size - new_unpad[1]
    dw /= 2
    dh /= 2

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

    img_padded = cv2.copyMakeBorder(img_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114,114,114))
    img_rgb = cv2.cvtColor(img_padded, cv2.COLOR_BGR2RGB)

    img_input = img_rgb.astype(np.float32) / 255.0
    img_input = np.transpose(img_input, (2, 0, 1))
    img_input = np.expand_dims(img_input, 0)

    return img_input, (h0, w0), (top, left), r

def nms(boxes, scores, iou_threshold=0.5):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    scores = np.array(scores)

    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        inter_w = np.maximum(0, xx2 - xx1)
        inter_h = np.maximum(0, yy2 - yy1)
        inter = inter_w * inter_h

        union = areas[i] + areas[order[1:]] - inter
        iou = inter / (union + 1e-6)

        order = order[1:][iou <= iou_threshold]

    return keep

def predict_image(image_path):
    img_input, (orig_h, orig_w), (pad_h, pad_w), r = preprocess_image(image_path)

    pred = session.run(None, {session.get_inputs()[0].name: img_input})[0]
    pred = pred.squeeze()

    xywh = pred[0:4, :]
    obj_conf = pred[4, :]
    cls_conf = pred[5:, :]

    cls_ids = np.argmax(cls_conf, axis=0)
    cls_scores = cls_conf[cls_ids, np.arange(cls_conf.shape[1])]
    scores = obj_conf * cls_scores

    mask = scores > 0.25
    if np.sum(mask) == 0:
        return []

    xywh = xywh[:, mask]
    scores = scores[mask]
    cls_ids = cls_ids[mask]

    x, y, w, h = xywh
    x1 = x - w/2
    y1 = y - h/2
    x2 = x + w/2
    y2 = y + h/2

    x1 = (x1 - pad_w) / r
    y1 = (y1 - pad_h) / r
    x2 = (x2 - pad_w) / r
    y2 = (y2 - pad_h) / r

    boxes = np.stack([x1, y1, x2, y2], axis=1)

    keep = nms(boxes, scores, iou_threshold=0.5)

    results = []
    for i in keep:
        results.append({
            "x1": float(boxes[i][0]),
            "y1": float(boxes[i][1]),
            "x2": float(boxes[i][2]),
            "y2": float(boxes[i][3]),
            "class": int(cls_ids[i]),
            "confidence": round(float(scores[i]), 3)
        })

    return results