import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

db = None

def init_firebase():
    global db

    if db is not None:
        return db

    try:
        cred_path = os.getenv("FIREBASE_CREDENTIALS")

        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS not set in .env")
        
        if not os.path.isabs(cred_path):
            cred_path = os.path.join(os.path.dirname(__file__), cred_path)

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        if os.getenv("FLASK_DEBUG") == "1":
            print("Firebase connected")

    except Exception as e:
        if os.getenv("FLASK_DEBUG") == "1":
            print(f"Firebase error: {e}")
            
        db = None

    return db