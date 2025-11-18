from flask import Blueprint, request, jsonify
from firebase_init import init_firebase
from token_utils import token_required
from roboflow import Roboflow
from firebase_admin import storage
import datetime
import pytz
import os
import tempfile

mold_bp = Blueprint("mold_bp", __name__)

rf = Roboflow(api_key=os.getenv("ROBOFLOW_API_KEY"))
project_name, version = os.getenv("ROBOFLOW_MODEL_ID").split("/")
model = rf.project(project_name).version(int(version)).model

@mold_bp.route("/detect", methods=["POST"])
@token_required
def detect_mold(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500
    
    FIREBASE_BUCKET = os.getenv("FIREBASE_BUCKET")
    bucket = storage.bucket(name=FIREBASE_BUCKET)
    
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = image.filename or "unknown.jpg"

    image_stream_copy = image.stream.read()
    image_stream_length = len(image_stream_copy)
    image.stream.seek(0)

    blob = bucket.blob(f"detections/{current_user_id}/{filename}")
    blob.upload_from_file(image.stream_copy, content_type=image.content_type)
    image_url = blob.public_url

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(image_stream_copy)
        tmp_path = tmp.name

    kst = pytz.timezone("Asia/Seoul")
    current_time = datetime.datetime.now(kst)
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        prediction = model.predict(tmp_path, confidence=70, overlap=30).json()
        predictions = prediction.get("predictions", [])

        predictions_clean = [
            {
                "x": p["x"],
                "y": p["y"],
                "width": p["width"],
                "height": p["height"],
                "class": p["class"],
                "confidence": round(p["confidence"], 2)
            }
            for p in predictions
            if p["confidence"] >= 0.5
        ]

        if predictions_clean:
            mold_type = predictions_clean [0]["class"]
            result = {
                "status": "warning",
                "message": "Mold detected!",
                "mold_type": mold_type,
                "predictions": predictions_clean,
                "advice": "Avoid contact and ventilate the area immediately.",
                "risk_level": "High",
                "color": "red",
                "timestamp": formatted_time
             }
            
        else:
            result = {
                "status": "safe",
                "message": "You are safe. No mold detected.",
                "color": "green",
                "timestamp": formatted_time
            }

        db.collection("detections").add({
            "user_id": current_user_id,
            "image_name": filename,
            "image_url": image_url,
            "result": result["status"],
            "message": result["message"],
            "predictions": predictions_clean,
            "timestamp": current_time
        })

        os.remove(tmp_path)

        return jsonify({
            "success": True,
            "data": result,
            "message": "Detection completed successfully."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Detection or Database error: {e}"}), 500