from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.firebase_init import init_firebase
from src.token_utils import create_token

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    username = data.get("username") or ""
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    if len(password) < 5:
        return jsonify({"success": False, "error": "Password too short"}), 400

    users_ref = db.collection("users")

    if users_ref.where("email", "==", email).get():
        return jsonify({"success": False, "error": "Email already exists"}), 400
    
    if users_ref.where("username", "==", username).get():
        return jsonify({"success": False, "error": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)

    doc_ref = users_ref.add({
        "email": email,
        "password": hashed_pw,
        "username": username
    })

    return jsonify({"success": True, "message": "Registration successful. Please log in."}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    db = init_firebase()
    if db is None:
        return jsonify({"success": False, "error": "Server connection error"}), 500

    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    users_ref = db.collection("users")
    users = list(users_ref.where("email", "==", email).get())

    if not users:
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    user_doc = users[0]
    user_data = user_doc.to_dict()

    if not check_password_hash(user_data["password"], password):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    token = create_token(user_doc.id)
    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"id": user_doc.id, "email": email, "username": user_data.get("username")}
        }
    }), 200