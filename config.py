import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

    # Use Supabase Transaction Pooler / Shared Pooler URI
    DATABASE_URL = os.getenv("DATABASE_URL")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

    # Upload directories
    UPLOAD_DIRS = {
        'gallery': os.path.join(BASE_DIR, 'static', 'images', 'gallery'),
        'teachers': os.path.join(BASE_DIR, 'static', 'images', 'teachers'),
        'mpos': os.path.join(BASE_DIR, 'static', 'images', 'mpos'),
        'committees': os.path.join(BASE_DIR, 'static', 'images', 'committees'),
        'students': os.path.join(BASE_DIR, 'static', 'images', 'students'), 
        'results': os.path.join(BASE_DIR, 'static', 'files', 'results'),
        'routine': os.path.join(BASE_DIR, 'static', 'files', 'routine')
    }

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
