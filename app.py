import os
import json
from dotenv import load_dotenv
from flask import Flask, current_app
from flask_migrate import Migrate  
from extensions import db, mail
from config import Config
from routes.public import public_bp
from routes.admin import admin_bp
from routes.ai_chat import ai_bp
from utils import upload_to_imgbb
from models import  Gallery

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['FLASK_SECRET_KEY']

# Initialize extensions
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)  

# -----------------------
# Create tables safely (optional when using migrations)
with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(ai_bp)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
