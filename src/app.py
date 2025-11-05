# src/app.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_init import init_firebase
from routes.auth import auth_bp
from routes.user import user_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "dummy"  # loaded in token_utils
CORS(app)

# Initialize Firebase BEFORE registering routes
init_firebase()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)