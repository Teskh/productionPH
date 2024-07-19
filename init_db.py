from app import create_app
from app.database import db

def init_database():
    app = create_app('development')
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == "__main__":
    init_database()
