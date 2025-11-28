import os
from flask import Flask
from flask_cors import CORS

from src.firebase_init import init_firebase

app = Flask(__name__)
CORS(app)

from src.routes.mold import mold_bp
from src.routes.chatbot import chatbot_bp

app.register_blueprint(mold_bp)
app.register_blueprint(chatbot_bp)
