from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "healthy"}, 200

    from src.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from src.routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    from src.routes.history import history_bp
    app.register_blueprint(history_bp, url_prefix="/api/history")

    from src.routes.mold import mold_bp
    app.register_blueprint(mold_bp, url_prefix="/api/mold")

    from src.routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

    return app

app = create_app()
