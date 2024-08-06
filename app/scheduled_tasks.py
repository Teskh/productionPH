from app.models import Task
from datetime import datetime
from flask import current_app
from app import create_app

def pause_active_tasks():
    app = create_app()
    with app.app_context():
        active_tasks = Task.get_all_active_tasks()
        for task in active_tasks:
            Task.update_task(
                task.id,
                'Paused',
                datetime.now(),
                'Fin de jornada - automatico'
            )
        app.logger.info(f"Automatically paused {len(active_tasks)} active tasks at end of day.")
