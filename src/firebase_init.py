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
        bucket_name = os.getenv("FIREBASE_BUCKET")

        if not cred_path:
            raise ValueError("FIREBASE_CREDENTIALS not set in .env")
        
        if not bucket_name:
            raise ValueError("FIREBASE_BUCKET not set in .env")
        
        if not os.path.isabs(cred_path):
            cred_path = os.path.join(os.path.dirname(__file__), cred_path)

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "storageBucket": bucket_name
            })

        db = firestore.client()

    except Exception as e:
        print("Firebase init error:", e)
        db = None

    return db