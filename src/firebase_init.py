import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage

db = None

def init_firebase():
    global db

    if db is not None:
        return db

    try:
        cred_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
        bucket_name = os.getenv("FIREBASE_BUCKET")

        if not cred_file:
            raise ValueError("Missing FIREBASE_CREDENTIALS_FILE")
        if not bucket_name:
            raise ValueError("Missing FIREBASE_BUCKET")

        cred = credentials.Certificate(cred_file)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                "storageBucket": bucket_name
            })

        db = firestore.client()
        return db

    except Exception as e:
        print("Firebase init error:", e)
        return None
