import os
import cloudinary
from dotenv import load_dotenv
from flask import Flask, current_app
from flask_migrate import Migrate  
from extensions import db
from config import Config
from routes.public import public_bp
from routes.admin import admin_bp
from routes.student import student_bp



from routes.teacher import teacher_bp    

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['FLASK_SECRET_KEY']
cloudinary.config(cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],api_key=app.config["CLOUDINARY_API_KEY"],api_secret=app.config["CLOUDINARY_API_SECRET"])
# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# -----------------------
# Create tables safely (optional when using migrations)
with app.app_context():
    db.create_all()
# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(teacher_bp, url_prefix="/teacher")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
