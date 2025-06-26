import firebase_admin
from firebase_admin import credentials, firestore
import os

# Use absolute path to the secrets directory in your home folder
key_path = os.path.expanduser("~/secrets/firebase_key.json")

cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
