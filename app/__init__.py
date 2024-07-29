from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduled_tasks import pause_active_tasks
from .database import db
from .data_manager import load_activity_data, load_project_data, load_worker_data
from config import Config

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config[config_name])

    # Initialize SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

        # Load Excel data
        app.config['ACTIVITY_DATA'] = load_activity_data(app.config['ACTIVITY_DATA_PATH'])
        app.config['PROJECT_DATA'] = load_project_data(app.config['PROJECT_DATA_PATH'])
        app.config['WORKER_DATA'] = load_worker_data(app.config['WORKER_DATA_PATH'])

    # Set up scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(pause_active_tasks, 'cron', hour=17, minute=40)
    scheduler.start()

    # Register blueprints
    from app import routes
    app.register_blueprint(routes.bp)

    return app
