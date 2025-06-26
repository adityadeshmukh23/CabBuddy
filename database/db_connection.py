import firebase_admin
from firebase_admin import credentials, firestore
import os

# Load key from project’s secrets folder
cred = credentials.Certificate(os.path.join("secrets", "firebase_key.json"))
firebase_admin.initialize_app(cred)

db = firestore.client()
