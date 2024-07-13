from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduled_tasks import pause_active_tasks
from config import Config

def create_app(config_class=Config):
    scheduler = BackgroundScheduler()
    scheduler.add_job(pause_active_tasks, 'cron', hour=17, minute=40)
    scheduler.start()
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    from app import routes
    app.register_blueprint(routes.bp)

    return app
