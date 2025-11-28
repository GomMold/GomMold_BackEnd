import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

db = None

def init_firebase():
    global db

    if db is not None:
        return db

    try:
        cred_json = os.getenv("FIREBASE_CREDENTIALS")
        bucket_name = os.getenv("FIREBASE_BUCKET")

        if not cred_json:
            raise ValueError("Missing FIREBASE_CREDENTIALS")
        if not bucket_name:
            raise ValueError("Missing FIREBASE_BUCKET")

        cred_dict = json.loads(cred_json)

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                "storageBucket": bucket_name
            })

        db = firestore.client()
        return db

    except Exception as e:
        print("Firebase init error:", e)
        return None