from flask import Flask
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.history import history_bp
from src.routes.mold import mold_bp
from src.routes.chatbot import chatbot_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "healthy"}, 200

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(mold_bp, url_prefix="/api/mold")
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

    return app

app = create_app()
