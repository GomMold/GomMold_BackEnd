from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    from src.routes.mold import mold_bp
    app.register_blueprint(mold_bp, url_prefix="/api/mold")

    from src.routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")

    return app

app = create_app()
