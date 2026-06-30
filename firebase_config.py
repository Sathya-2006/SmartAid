import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

firebase_json = os.environ.get("FIREBASE_KEY")

if not firebase_admin._apps:
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
