from app.models import Task
from datetime import datetime
from app.utils import format_timestamp

def pause_active_tasks():
    active_tasks = Task.get_all_active_tasks()
    timestamp = format_timestamp()
    for task in active_tasks:
        Task.update_task(task['task_id'], 'Paused', timestamp, "Final del día automático")
