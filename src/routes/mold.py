from flask import Blueprint, request, jsonify
from src.firebase_init import init_firebase
from src.token_utils import token_required
from firebase_admin import storage
from google.cloud import firestore
from src.ml_model import predict_image
import datetime
import pytz
import os
import tempfile

mold_bp = Blueprint("mold_bp", __name__)

CLASS_NAMES = ["mold"]
MIN_CONFIDENCE = 0.2

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

        cleaned = [
            {**p, "class_name": "mold"}
            for p in predictions if p["confidence"] >= MIN_CONFIDENCE
        ]

        has_mold = len(cleaned) > 0

        result = (
            {"status": "warning", "message": "Mold detected", "color": "red"}
            if has_mold
            else {"status": "safe", "message": "No mold detected", "color": "green"}
        )

        timestamp_value = firestore.SERVER_TIMESTAMP

        doc_ref = db.collection("detections").document()
        doc_ref.set({
            "user_id": current_user_id,
            "analysis_name": analysis_name,
            "image_name": filename,
            "image_url": image_url,
            "result": result["status"],
            "message": result["message"],
            "predictions": cleaned,
            "timestamp": timestamp_value
        })

        os.remove(tmp_path)

        now_kst = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("Asia/Seoul")
        )
        formatted_time = now_kst.strftime("%Y-%m-%d %H:%M")

        return jsonify({
            "success": True,
            "data": {
                **result,
                "analysis_name": analysis_name,
                "image_url": image_url,
                "predictions": cleaned,
                "timestamp": formatted_time
            }
        }), 200

    except Exception as e:
        print("Detection error:", e)
        return jsonify({"success": False, "error": str(e)}), 500