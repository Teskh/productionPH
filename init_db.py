from app import create_app
from app.database import db
from app.models import Task
from sqlalchemy import inspect

def init_database():
    app = create_app('development')
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = inspector.get_columns('task')
        existing_column_names = [col['name'] for col in existing_columns]

        new_columns = [
            ('supervisor', 'VARCHAR(100)'),
            ('specialty', 'VARCHAR(100)'),
            ('pause_1_time', 'DATETIME'),
            ('pause_1_reason', 'VARCHAR(200)'),
            ('resume_1_time', 'DATETIME'),
            ('pause_2_time', 'DATETIME'),
            ('pause_2_reason', 'VARCHAR(200)'),
            ('resume_2_time', 'DATETIME'),
            ('station_i', 'VARCHAR(50)'),
            ('station_f', 'VARCHAR(50)'),
            ('line', 'VARCHAR(50)')
        ]

        for column_name, column_type in new_columns:
            if column_name not in existing_column_names:
                db.session.execute(db.text(f'ALTER TABLE task ADD COLUMN {column_name} {column_type}'))
                print(f"Added {column_name} column to task table.")

        db.session.commit()
        db.create_all()  # This will create any new tables if needed
        print("Database schema updated.")

if __name__ == "__main__":
    init_database()
