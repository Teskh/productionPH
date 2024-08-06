from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .database import db
from .data_manager import load_activity_data, load_project_data, load_worker_data
from config import config
import os

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config[config_name])

    # Set a secret key
    app.secret_key = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Initialize SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

        # Load Excel data
        app.config['ACTIVITY_DATA'] = load_activity_data(app.config['ACTIVITY_DATA_PATH'])
        app.config['PROJECT_DATA'] = load_project_data(app.config['PROJECT_DATA_PATH'])
        app.config['WORKER_DATA'] = load_worker_data(app.config['WORKER_DATA_PATH'])

    # Register blueprints
    from app import routes
    app.register_blueprint(routes.bp)

    # Set up scheduler
    scheduler = BackgroundScheduler()
    from .scheduled_tasks import pause_active_tasks
    scheduler.add_job(pause_active_tasks, 'cron', hour=11, minute=19)
    scheduler.start()

    return app
