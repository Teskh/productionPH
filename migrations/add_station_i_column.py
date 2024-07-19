import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from sqlalchemy import inspect

def add_station_i_column():
    app = create_app('development')
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = inspector.get_columns('task')
        existing_column_names = [col['name'] for col in existing_columns]

        if 'station_i' not in existing_column_names:
            db.engine.execute('ALTER TABLE task ADD COLUMN station_i VARCHAR(50)')
            print("Added station_i column to task table.")
        else:
            print("station_i column already exists in task table.")

        db.create_all()  # This will create any new tables if needed
        print("Database schema updated.")

if __name__ == "__main__":
    add_station_i_column()