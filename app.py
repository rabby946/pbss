import os
from dotenv import load_dotenv
from flask import Flask
from extensions import db
from config import Config
from routes.public import public_bp
from routes.admin import admin_bp
from routes.ai_chat import ai_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['FLASK_SECRET_KEY']

# Initialize database
db.init_app(app)

# -----------------------
# Create tables safely
with app.app_context():
    db.create_all()  # Only creates tables if not exist; safe for Pooler usage

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(ai_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
