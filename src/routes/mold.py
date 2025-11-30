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

MIN_CONFIDENCE = 0.20

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

    blob.make_public()
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

        result = {
            "status": "warning" if has_mold else "safe",
            "message": "Mold detected" if has_mold else "No mold detected",
            "color": "red" if has_mold else "green"
        }

        timestamp_utc = datetime.datetime.utcnow()

        write_result, doc_ref = db.collection("detections").add({
            "user_id": current_user_id,
            "analysis_name": analysis_name,
            "image_name": filename,
            "image_url": image_url,
            "result": result["status"],
            "message": result["message"],
            "predictions": cleaned,
            "timestamp": timestamp_utc
        })

        os.remove(tmp_path)

        kst = pytz.timezone("Asia/Seoul")
        timestamp_kst = timestamp_utc.replace(tzinfo=pytz.utc).astimezone(kst)
        formatted_time = timestamp_kst.strftime("%Y-%m-%d %H:%M")

        return jsonify({
            "success": True,
            "data": {
                "id": doc_ref.id,
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
