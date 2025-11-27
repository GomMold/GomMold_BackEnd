import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

db = None

def init_firebase():
    global db

    if db is not None:
        return db

    try:
        cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_service_key.json")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "storageBucket": os.getenv("FIREBASE_BUCKET")
            })

        db = firestore.client()
        return db

    except Exception as e:
        print("Firebase init error:", e)
        return None
