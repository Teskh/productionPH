import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Excel file paths
    ACTIVITY_DATA_PATH = os.environ.get('ACTIVITY_DATA_PATH')
    PROJECT_DATA_PATH = os.environ.get('PROJECT_DATA_PATH')
    WORKER_DATA_PATH = os.environ.get('WORKER_DATA_PATH')

    # Ensure all required environment variables are set
    required_env_vars = ['DATABASE_URL', 'ACTIVITY_DATA_PATH', 'PROJECT_DATA_PATH', 'WORKER_DATA_PATH']
    for var in required_env_vars:
        if os.environ.get(var) is None:
            raise ValueError(f"Environment variable {var} is not set")

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
