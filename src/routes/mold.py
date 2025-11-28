from flask import Blueprint, request, jsonify
from src.firebase_init import init_firebase
from src.token_utils import token_required
from firebase_admin import storage
from src.ml_model import predict_image
import datetime
import pytz
import os
import tempfile

mold_bp = Blueprint("mold_bp", __name__)


CLASS_NAMES = ["mold"]
MIN_CONFIDENCE = 0.25


@mold_bp.route("/detect", methods=["POST"])
@token_required
def detect_mold(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    bucket_name = os.getenv("FIREBASE_BUCKET")
    bucket = storage.bucket(name=bucket_name)

    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = image.filename or "uploaded.jpg"

    analysis_name = request.form.get("analysis_name", "Untitled").strip() or "Untitled"

    image_bytes = image.read()

    blob = bucket.blob(f"detections/{current_user_id}/{filename}")
    blob.upload_from_string(image_bytes, content_type=image.content_type)
    image_url = blob.public_url

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        predictions = predict_image(tmp_path)

        cleaned = []
        for p in predictions:
            cleaned.append({
                **p,
                "class_name": "mold"
            })

        cleaned = [p for p in cleaned if p["confidence"] >= MIN_CONFIDENCE]

        has_mold = len(cleaned) > 0

        kst = pytz.timezone("Asia/Seoul")
        now = datetime.datetime.now(kst)
        timestamp = now.strftime("%Y-%m-%d %H:%M")

        if has_mold:
            result = {
                "status": "warning", 
                "message": "Mold detected", 
                "color": "red"
            }
        
        else:
            result = {"status": "safe",
                      "message": "No mold detected",
                      "color": "green"
                    }

        db.collection("detections").add({
            "user_id": current_user_id,
            "analysis_name": analysis_name,
            "image_name": filename,
            "image_url": image_url,
            "result": result["status"],
            "message": result["message"],
            "predictions": cleaned,
            "timestamp": now
        })

        os.remove(tmp_path)

        return jsonify({
            "success": True,
            "data": {
                **result,
                "analysis_name": analysis_name,
                "image_url": image_url,
                "predictions": cleaned,
                "timestamp": timestamp
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500