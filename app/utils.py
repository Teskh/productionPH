from datetime import datetime
from app.models import Task
from app.database import db
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
import time

def format_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')

def get_task_summary(start_date, end_date):
    try:
        tasks = Task.query.filter(
            Task.start_time >= start_date,
            Task.start_time <= end_date
        ).all()
        
        summary = pd.DataFrame([
            {
                'worker_name': task.worker_name,
                'project': task.project,
                'activity': task.activity,
                'duration': (task.end_time - task.start_time).total_seconds() / 3600  # hours
            } for task in tasks if task.end_time
        ])
        
        return summary.groupby(['worker_name', 'project', 'activity']).sum().reset_index()
    except SQLAlchemyError as e:
        print(f"Error generating task summary: {str(e)}")
        return pd.DataFrame()

def safe_db_operation(operation):
    try:
        result = operation()
        db.session.commit()
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        return None

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper
