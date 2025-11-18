import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from firebase_init import init_firebase
from routes.auth import auth_bp
from routes.user import user_bp
from routes.history import history_bp
from routes.chatbot import chatbot_bp
from routes.mold import mold_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app)

init_firebase()

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(history_bp, url_prefix="/api/history")
app.register_blueprint(mold_bp, url_prefix="/api/mold")
app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)