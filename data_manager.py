import openpyxl
from collections import defaultdict
import os

def load_worker_data(file_path='data/worker_data.xlsx'):
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    wb = openpyxl.load_workbook(full_path)
    sheet = wb.active
    
    supervisors = defaultdict(list)
    workers = {}
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        supervisor, worker_name, worker_number, specialty, gender = row
        
        supervisors[supervisor].append(worker_name)
        workers[worker_name] = {
            'name': worker_name,
            'number': worker_number,
            'specialty': specialty.upper() if specialty else 'Not specified',
            'supervisor': supervisor,
            'gender': gender
        }
    
    print("Loaded worker data:")
    print("Supervisors:", dict(supervisors))
    print("Workers:", workers)
    return dict(supervisors), workers

def load_project_data(file_path='data/project_data.xlsx'):
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    wb = openpyxl.load_workbook(full_path)
    sheet = wb.active
    
    projects = {}
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        project_name, total_houses, num_modulos = row
        projects[project_name] = {
            'total_houses': total_houses,
            'num_modulos': num_modulos
        }
    
    print("Loaded project data:", projects)
    return projects

def load_activity_data(file_path='data/activity_data.xlsx'):
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    wb = openpyxl.load_workbook(full_path)
    sheet = wb.active
    
    activities = defaultdict(list)
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        specialty, activity = row
        activities[specialty.upper()].append(activity)
    
    print("Loaded activity data:", dict(activities))
    return dict(activities)

# Test the functions
if __name__ == "__main__":
    supervisors, workers = load_worker_data()
    projects = load_project_data()
    activities = load_activity_data()