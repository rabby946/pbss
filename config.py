import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

    DATABASE_URL = os.getenv("DATABASE_URL")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    BKASH_BASE_URL = os.getenv("BKASH_BASE_URL")
    BKASH_USERNAME = os.getenv("BKASH_USERNAME")
    BKASH_PASSWORD = os.getenv("BKASH_PASSWORD")
    BKASH_APP_KEY = os.getenv("BKASH_APP_KEY")
    BKASH_APP_SECRET = os.getenv("BKASH_APP_SECRET")
    
        # bKash API Endpoints (for sandbox)
    BKASH_GRANT_TOKEN_URL = "/tokenized/checkout/token/grant"
    BKASH_CREATE_PAYMENT_URL = "/tokenized/checkout/create"
    BKASH_EXECUTE_PAYMENT_URL = "/tokenized/checkout/execute"
    BKASH_QUERY_PAYMENT_URL = "/tokenized/checkout/payment/status"

