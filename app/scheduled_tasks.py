from app.models import Task
from flask import current_app
from datetime import datetime

def pause_active_tasks():
    with current_app.app_context():
        active_tasks = Task.get_all_active_tasks()
        for task in active_tasks:
            Task.update_task(
                task.id,
                'Paused',
                datetime.now(),
                'Fin de jornada - automatico'
            )
        current_app.logger.info(f"Automatically paused {len(active_tasks)} active tasks at end of day.")
