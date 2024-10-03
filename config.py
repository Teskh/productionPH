import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'production_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Excel file paths with default values
    ACTIVITY_DATA_PATH = os.environ.get('ACTIVITY_DATA_PATH') or os.path.join(basedir, 'data', 'activity_data.xlsx')
    PROJECT_DATA_PATH = os.environ.get('PROJECT_DATA_PATH') or os.path.join(basedir, 'data', 'project_data.xlsx')
    #WORKER_DATA_PATH = os.environ.get('WORKER_DATA_PATH') or os.path.join(basedir, 'data', 'worker_data.xlsx')
    
    WORKER_DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS047eA-lEVKaum6s6w3-j0pjE0NsC5-oFdtN-RfzzlDEBk3ASxKvX3I2epBhBwm3otgwri3q3e3d6Q/pub?gid=0&single=true&output=csv"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}
