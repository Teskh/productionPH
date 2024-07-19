from app import create_app
from app.database import db

def init_database():
    app = create_app('development')
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create all tables
        print("Database reinitialized.")

if __name__ == "__main__":
    init_database()
