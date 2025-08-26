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
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

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
