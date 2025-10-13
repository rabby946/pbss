import csv
import os
from datetime import datetime
from extensions import db
from app import app  # ensure app context is available
from models import Teacher, Student, Gallery

def backup_table_to_csv(model, filename, fields):
    """Backup any SQLAlchemy model table to CSV with UTF-8 support."""
    with app.app_context():
        records = model.query.all()
        if not records:
            print(f"⚠️ No data found in {model.__tablename__}, skipping...")
            return

        # Open with UTF-8-SIG for Excel and Unicode support
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)  # Write column headers
            
            for record in records:
                row = []
                for field in fields:
                    value = getattr(record, field, "")
                    # Convert non-string values safely
                    if isinstance(value, (list, dict)):
                        import json
                        value = json.dumps(value, ensure_ascii=False)
                    elif value is None:
                        value = ""
                    row.append(str(value))
                writer.writerow(row)

        print(f"✅ Backup completed for {model.__tablename__} → {filename}")


def backup_all():
    """Backup Teachers, Students, and Gallery tables to CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("backups", exist_ok=True)

    teacher_file = f"backups/teachers_backup_{timestamp}.csv"
    student_file = f"backups/students_backup_{timestamp}.csv"
    gallery_file = f"backups/gallery_backup_{timestamp}.csv"

    backup_table_to_csv(
        Teacher,
        teacher_file,
        ["id", "name", "position", "image_url", "timestamp"]
    )

    backup_table_to_csv(
        Student,
        student_file,
        ["id", "name", "roll", "image_url", "timestamp"]
    )

    backup_table_to_csv(
        Gallery,
        gallery_file,
        ["id", "title", "description", "images", "timestamp"]
    )

    print("\n🎉 All backups completed successfully with UTF-8 encoding!")


if __name__ == "__main__":
    backup_all()
