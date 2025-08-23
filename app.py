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
from models import  MPO

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
@app.route("/upload")
def teacher_upload():
    # Load teachers.json file
    json_path = os.path.join(current_app.root_path, "mpos.json")
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    count = 0
    for t in items:
        # Upload image and get hosted URL
        image_path = os.path.join(current_app.root_path, "static/images/mpos", t["filename"])
        if image_path:
            file_url = upload_to_imgbb(image_path)


            # Create teacher entry
            teacher = MPO(name=t["title"], designation=t["description"], image_url=file_url)

            db.session.add(teacher)
            count += 1

    db.session.commit()

    return f"✅ Uploaded {count} teachers to the database!"
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
