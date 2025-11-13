from flask import Blueprint, request, jsonify
from firebase_init import init_firebase
from token_utils import token_required
import datetime
import pytz
import random

mold_bp = Blueprint("mold_bp", __name__)

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

    mold_detected = random.choice([True, False])

    if mold_detected:
        result = {
            "status": "warning",
            "message": "Mold detected!",
            "mold_type": "Black Mold (Mock)",
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

    try:
        db.collection("detections").add({
            "user_id": current_user_id,
            "image_name": filename,
            "result": result["status"],
            "message": result["message"],
            "timestamp": current_time
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Database error: {e}"}), 500

    return jsonify({
        "success": True,
        "data": result,
        "message": "Detection completed successfully."
    }), 200