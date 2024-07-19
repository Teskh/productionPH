import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    EXCEL_FILE = os.path.join(os.path.dirname(__file__), 'data', 'production_data.xlsx')
    EXCEL_LOCK_FILE = os.path.join(os.path.dirname(__file__), 'data', 'production_data.xlsx.lock')
    WORKER_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'worker_data.xlsx')
    PROJECT_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'project_data.xlsx')
    ACTIVITY_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'activity_data.xlsx')
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
