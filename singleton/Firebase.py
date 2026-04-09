from firebase_admin import credentials, auth
import firebase_admin
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseAuth:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAuth, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if not firebase_admin._apps:
            # Create Firebase credentials JSON dynamically from environment variables
            service_account_json = {
                "type": os.getenv("FIREBASE_TYPE"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
                "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
            }
            cred = credentials.Certificate(service_account_json)
            firebase_admin.initialize_app(cred)
    
    def verify_token(self, id_token):
        try:
            decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=10)
            return decoded_token
        except auth.ExpiredIdTokenError as expired:
            print("Token Expired: ", expired)
            return None
        except auth.InvalidIdTokenError as invalid:
            print("Invalid token: ", invalid)
            return None

    def get_user(self, uid):
        try:
            return auth.get_user(uid)
        except auth.UserNotFoundError as userNotFound:
            print("User not found: ", userNotFound)
            return None
        except Exception as e:
            print("Error while fetching user: ", e)
            return None