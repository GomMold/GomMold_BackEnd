from flask import Blueprint, jsonify
from src.firebase_init import init_firebase
from src.token_utils import token_required
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500
    
    doc = db.collection("users").document(current_user_id).get()

    if not doc.exists:
        return jsonify({"success": False, "error": "User not found"}), 404

    user_data = doc.to_dict()
    return jsonify({
        "success": True,
        "data": {
            "id": doc.id,
            "email": user_data.get("email"),
            "username": user_data.get("username")
        }
    }), 200

@user_bp.route("/update", methods=["PATCH"])
@token_required
def update_user(current_user_id):
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    data = request.get_json()
    updates = {}

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    users_ref = db.collection("users")

    if "username" in data:
        new_username = data["username"].strip()

        if not new_username:
            return jsonify({"success": False, "error": "Username cannot be empty."}), 400
        
        existing = list(users_ref.where("username", "==", new_username).get())

        for doc in existing:
            if doc.id != current_user_id:
                return jsonify({"success": False, "error": "Username has been taken."}), 400

        updates["username"] = new_username

        new_password = data["password"]

        if len(new_password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400

        updates["password"] = generate_password_hash(new_password)

    if updates:
        try:
            db.collection("users").document(current_user_id).update(updates)
        except Exception as e:
            return jsonify({"success": False, "error": f"Error updating profile: {e}"}), 400

    return jsonify({"success": True, "message": "Profile updated successfully."}), 200