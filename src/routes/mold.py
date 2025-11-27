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

CLASS_NAMES = ["mold", "no_mold"]

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
    filename = image.filename or "uploaded.jpg"

    analysis_name = request.form.get("analysis_name", "Untitled").strip()
    if not analysis_name:
        analysis_name = "Untitled"

    image_bytes = image.read()
    image.stream.seek(0)

    blob = bucket.blob(f"detections/{current_user_id}/{filename}")
    blob.upload_from_file(image.stream, content_type=image.content_type)
    image_url = blob.public_url

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        predictions = predict_image(tmp_path)

        predictions_clean = []
        for p in predictions:
            predictions_clean.append({
                **p,
                "class_name": CLASS_NAMES[p["class"]] if p["class"] < len(CLASS_NAMES) else "unknown"
            })

        predictions_clean = [p for p in predictions_clean if p["confidence"] >= 0.25]

        has_mold = any(p["class_name"] == "mold" for p in predictions_clean)

        kst = pytz.timezone("Asia/Seoul")
        current_time = datetime.datetime.now(kst)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

        if has_mold:
            result = {
                "status": "warning",
                "message": "Mold detected",
                "color": "red",
                "timestamp": formatted_time
            }
        else:
            result = {
                "status": "safe",
                "message": "No mold detected",
                "color": "green",
                "timestamp": formatted_time
            }

        db.collection("detections").add({
            "user_id": current_user_id,
            "analysis_name": analysis_name,
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
            "data": {
                **result,
                "analysis_name": analysis_name,
                "image_url": image_url,
                "predictions": predictions_clean
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500