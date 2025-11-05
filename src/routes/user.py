from flask import Blueprint, jsonify
from firebase_init import init_firebase
from token_utils import token_required

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user_id):
    db = init_firebase()  # <--- initialize Firebase here
    if db is None:
        return jsonify({"error": "Database not available"}), 500

    doc = db.collection("users").document(current_user_id).get()
    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    user_data = doc.to_dict()
    return jsonify({
        "id": doc.id,
        "email": user_data.get("email"),
        "username": user_data.get("username")
    }), 200