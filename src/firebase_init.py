# src/firebase_init.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS = os.path.join(
    os.path.dirname(__file__),
    os.getenv("FIREBASE_CREDENTIALS")  # e.g., 'firebase_config.json'
)

db = None  # Firestore client

def init_firebase():
    global db
    if db is not None:
        return db  # Already initialized

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase connected")
    except Exception as e:
        print(f"Firebase error: {e}")
        db = None
    return db