from flask import Blueprint, jsonify
from firebase_init import init_firebase
from token_utils import token_required
from google.cloud import firestore
import datetime

history_bp = Blueprint('history_bp', __name__)

@history_bp.route("/history", methods=["GET"])
@token_required
def get_history(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    try:
        detections_ref = (
            db.collection("detections")
              .where("user_id", "==", current_user_id)
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        detections = [doc.to_dict() for doc in detections_ref.get()]

        if not detections:
            return jsonify({
                "success": True,
                "data": [],
                "message": "No detection history found."
            }), 200

        return jsonify({
            "success": True,
            "data": detections,
            "message": "Detection history retrieved successfully."
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve history",
            "details": str(e)
        }), 500