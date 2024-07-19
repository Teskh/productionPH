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

        if 'station_i' not in existing_column_names:
            db.engine.execute('ALTER TABLE task ADD COLUMN station_i VARCHAR(50)')
            print("Added station_i column to task table.")

        if 'station_f' not in existing_column_names:
            db.engine.execute('ALTER TABLE task ADD COLUMN station_f VARCHAR(50)')
            print("Added station_f column to task table.")

        if 'line' not in existing_column_names:
            db.engine.execute('ALTER TABLE task ADD COLUMN line VARCHAR(50)')
            print("Added line column to task table.")

        db.create_all()  # This will create any new tables if needed
        print("Database schema updated.")

if __name__ == "__main__":
    init_database()
