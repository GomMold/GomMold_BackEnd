from flask import Blueprint, jsonify, request
from src.firebase_init import init_firebase
from src.token_utils import token_required
from google.cloud import firestore
import datetime
import pytz

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
        kst = pytz.timezone("Asia/Seoul")  

        for doc in detections:
            data = doc.to_dict()
            ts = data.get("timestamp")


            if isinstance(ts, datetime.datetime):
                   
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=pytz.utc)
                ts_kst = ts.astimezone(kst)
                formatted_time = ts_kst.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_time = str(ts)

            history_list.append({
                "id": doc.id,
                "analysis_name": data.get("analysis_name", "Untitled"),
                "image_url": data.get("image_url"),
                "result": data.get("result"),
                "message": data.get("message"),
                "predictions": data.get("predictions", []),
                "timestamp": formatted_time,
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



@history_bp.route("/<doc_id>", methods=["PUT"])
@token_required
def update_analysis_name(current_user_id, doc_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    new_name = request.json.get("analysis_name")

    if not new_name:
        return jsonify({"success": False, "error": "analysis_name is required"}), 400

    try:
        doc_ref = db.collection("detections").document(doc_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"success": False, "error": "Record not found"}), 404

        if doc.to_dict().get("user_id") != current_user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        doc_ref.update({
            "analysis_name": new_name,
            "updated_at": datetime.datetime.utcnow()
        })

        return jsonify({
            "success": True,
            "message": "Analysis title updated successfully."
        }), 200

    except Exception as e:
        print("Update error:", e)
        return jsonify({
            "success": False,
            "error": "Failed to update analysis name",
            "details": str(e)
        }), 500
