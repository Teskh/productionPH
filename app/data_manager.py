from flask import current_app
import pandas as pd
from collections import defaultdict
import requests
import io
from app.models import Task
from app.database import db
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime

def reload_worker_data(app):
    with app.app_context():
        app.supervisors, app.workers = load_worker_data(app.config['WORKER_DATA_URL'])
        app.projects = load_project_data(app.config['PROJECT_DATA_PATH'])
        app.activities = load_activity_data(app.config['ACTIVITY_DATA_PATH'])
        app.config['LAST_WORKER_DATA_UPDATE'] = datetime.now().isoformat()
    print("All data reloaded successfully")

def load_excel_data(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error loading Excel file {file_path}: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on error

def load_worker_data(worker_data_url):
    try:
        response = requests.get(worker_data_url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        supervisors = defaultdict(list)
        workers = {}
        
        for _, row in df.iterrows():
            supervisor, worker_name, worker_number, specialty, gender = row
            
            supervisors[supervisor].append(worker_name)
            workers[worker_name] = {
                'name': worker_name,
                'number': worker_number,
                'specialty': specialty.upper() if specialty else 'Not specified',
                'supervisor': supervisor,
                'gender': gender
            }
        
        return dict(supervisors), workers
    except Exception as e:
        print(f"Error loading worker data from URL: {str(e)}")
        return {}, {}

def load_project_data(project_data_path):
    df = load_excel_data(project_data_path)
    projects = {}
    
    for _, row in df.iterrows():
        project_name, total_houses, num_modulos = row
        projects[project_name] = {
            'total_houses': total_houses,
            'num_modulos': num_modulos
        }
    
    return projects

def load_activity_data(activity_data_path):
    df = load_excel_data(activity_data_path)
    activities = defaultdict(list)
    
    for _, row in df.iterrows():
        specialty, activity = row
        activities[specialty.upper()].append(activity)
    
    return dict(activities)

def get_active_tasks():
    try:
        return Task.query.filter_by(status='en proceso').all()
    except SQLAlchemyError as e:
        print(f"Error retrieving active tasks: {str(e)}")
        return []

def get_paused_tasks():
    try:
        return Task.query.filter_by(status='Paused').all()
    except SQLAlchemyError as e:
        print(f"Error retrieving paused tasks: {str(e)}")
        return []

def get_finished_tasks(start_date, end_date):
    try:
        return Task.query.filter(
            Task.status == 'Finished',
            Task.end_time >= start_date,
            Task.end_time <= end_date
        ).all()
    except SQLAlchemyError as e:
        print(f"Error retrieving finished tasks: {str(e)}")
        return []

def export_data(start_date, end_date, filename):
    try:
        tasks = Task.query.filter(
            Task.start_time >= start_date,
            Task.start_time <= end_date
        ).all()
        
        task_data = pd.DataFrame([
            {
                'worker_name': task.worker_name,
                'project': task.project,
                'activity': task.activity,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'status': task.status
            } for task in tasks
        ])
        
        activity_data = pd.read_excel(current_app.config['ACTIVITY_DATA_PATH'])
        project_data = pd.read_excel(current_app.config['PROJECT_DATA_PATH'])
        
        with pd.ExcelWriter(filename) as writer:
            task_data.to_excel(writer, sheet_name='Tasks', index=False)
            activity_data.to_excel(writer, sheet_name='Activities', index=False)
            project_data.to_excel(writer, sheet_name='Projects', index=False)
        
        print(f"Data exported to {filename}")
    except Exception as e:
        print(f"Error exporting data: {str(e)}")

def get_task_statistics():
    try:
        total_tasks = Task.query.count()
        active_tasks = Task.query.filter_by(status='en proceso').count()
        finished_tasks = Task.query.filter_by(status='Finished').count()
        return {
            'total': total_tasks,
            'active': active_tasks,
            'finished': finished_tasks
        }
    except SQLAlchemyError as e:
        print(f"Error getting task statistics: {str(e)}")
        return {'total': 0, 'active': 0, 'finished': 0}

def safe_db_operation(operation):
    try:
        result = operation()
        db.session.commit()
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        return None

def add_new_task(worker_number, worker_name, project, house, module, activity):
    return safe_db_operation(lambda: Task.add_task(worker_number, worker_name, project, house, module, activity))

# Test the functions
if __name__ == "__main__":
    supervisors, workers = load_worker_data()
    projects = load_project_data()
    activities = load_activity_data()
    print("Active tasks:", get_active_tasks())
    print("Task statistics:", get_task_statistics())
