from flask import Blueprint, jsonify, request
from src.firebase_init import init_firebase
from src.token_utils import token_required
from google.cloud import firestore

history_bp = Blueprint("history_bp", __name__)

@history_bp.route("/", methods=["GET"])
@token_required
def get_history(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    try:
        detections = (
            db.collection("detections")
              .where("user_id", "==", current_user_id)
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .get()
        )

        history_list = []
        for doc in detections:
            data = doc.to_dict()
            history_list.append({
                "id": doc.id,
                "analysis_name": data.get("analysis_name", "Untitled"),
                "image_url": data.get("image_url"),
                "result": data.get("result"),
                "message": data.get("message"),
                "predictions": data.get("predictions", []),
                "timestamp": str(data.get("timestamp"))
            })

        return jsonify({
            "success": True,
            "data": history_list,
            "message": "History loaded successfully."
        }), 200

    except Exception as e:
        print("History error:", e)
        return jsonify({
            "success": False,
            "error": "Failed to retrieve history",
            "details": str(e)
        }), 500