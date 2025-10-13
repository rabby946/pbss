import csv
from datetime import datetime
from app import app, db  #  make sure your app is imported
from models import User, Teacher  # import models

CSV_PATH = "backups/teachers_backup.csv"  # adjust if your path is different

def safe(value, fallback="demo"):
    """Return trimmed value or fallback."""
    return value.strip() if value and str(value).strip() else fallback

def import_teachers():
    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        count = 0

        for row in reader:
            name = safe(row.get("name"))
            position = safe(row.get("position"))
            qualification = safe(row.get("qualification"))
            phone = safe(row.get("phone"), "123456789")
            address = safe(row.get("address"))
            image_url = safe(row.get("image_url"), "demo.jpg")

            # Create new User for each teacher
            user = User(
                user_type="teacher",
                password="demo",  # you can later hash this if needed
            )
            db.session.add(user)
            db.session.flush()  # get user.id

            # Create Teacher record
            teacher = Teacher(
                user_id=user.id,
                name=name,
                position=position,
                qualification=qualification,
                phone=phone,
                address=address,
                image_url=image_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(teacher)
            count += 1

        db.session.commit()
        print(f"✅ Imported {count} teachers successfully!")

# ✅ FIX: Wrap inside Flask app context
if __name__ == "__main__":
    with app.app_context():
        import_teachers()
