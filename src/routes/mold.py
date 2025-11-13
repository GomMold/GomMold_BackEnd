from flask import Blueprint, request, jsonify
from firebase_init import init_firebase
from token_utils import token_required
from roboflow import Roboflow
import datetime
import pytz
import os

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

    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = image.filename or "unknown.jpg"

    kst = pytz.timezone("Asia/Seoul")
    current_time = datetime.datetime.now(kst)
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        prediction = model.predict(image, confidence=40, overlap=30).json()
        predictions = prediction.get("predictions", [])

        if predictions:
            mold_type = predictions[0]["class"]
            result = {
                "status": "warning",
                "message": "Mold detected!",
                "mold_type": mold_type,
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
            "result": result["status"],
            "message": result["message"],
            "timestamp": current_time
        })

        return jsonify({
            "success": True,
            "data": result,
            "message": "Detection completed successfully."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Detection or Database error: {e}"}), 500