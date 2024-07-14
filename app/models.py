from app.utils import format_timestamp
from filelock import FileLock
import openpyxl
from datetime import datetime
import os

EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'production_data.xlsx')
EXCEL_LOCK_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'production_data.xlsx.lock')

class Task:
    @staticmethod
    def get_active_tasks(worker_number):
        lock = FileLock(EXCEL_LOCK_FILE)
        with lock:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            active_tasks = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if len(row) > 10 and str(row[2]) == str(worker_number) and row[10] in ['en proceso', 'Paused']:
                    task = {
                        'task_id': row[0],
                        'start_time': row[1],
                        'worker_number': row[2],
                        'user': row[4],
                        'project': row[6],
                        'house_number': row[7],
                        'n_modulo': row[8],
                        'activity': row[9],
                        'status': row[10],
                        'station': row[11] if len(row) > 11 else '',
                        'line': row[12] if len(row) > 12 else '',
                    }
                    if len(row) > 13:
                        task['pause_1_time'] = row[13]
                        task['pause_1_reason'] = row[14] if len(row) > 14 else ''
                    if len(row) > 15:
                        task['resume_1_time'] = row[15]
                    if len(row) > 16:
                        task['pause_2_time'] = row[16]
                        task['pause_2_reason'] = row[17] if len(row) > 17 else ''
                    if len(row) > 18:
                        task['resume_2_time'] = row[18]
                    active_tasks.append(task)
            return active_tasks

    @staticmethod
    def get_all_active_tasks():
        lock = FileLock(EXCEL_LOCK_FILE)
        with lock:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            active_tasks = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if len(row) > 10 and row[10] == 'en proceso':
                    task = {
                        'task_id': row[0],
                        'worker_number': row[2],
                    }
                    active_tasks.append(task)
            return active_tasks

    @staticmethod
    def get_active_task(worker_number):
        tasks = Task.get_active_tasks(worker_number)
        return next((task for task in tasks if task['status'] == 'en proceso'), None)

    @staticmethod
    def add_task(task_data):
        lock = FileLock(EXCEL_LOCK_FILE)
        with lock:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            new_row = [
                task_data.get('task_id', ''),
                format_timestamp(),
                task_data.get('worker_number', ''),
                task_data.get('supervisor', ''),
                task_data.get('user', ''),
                task_data.get('specialty', ''),
                task_data.get('project', ''),
                task_data.get('house_number', ''),
                task_data.get('n_modulo', ''),
                task_data.get('activity', ''),
                'en proceso',  # Default status when starting a new task
                task_data.get('station', ''),
                task_data.get('line', ''),
                '', '', '', '', '', '',  # Pause and Resume columns
                ''  # End Timestamp
            ]
            ws.append(new_row)
            wb.save(EXCEL_FILE)
        return True  # Indicate successful task addition

    @staticmethod
    def update_task(task_id, new_status, timestamp=None, pause_reason=None):
        lock = FileLock(EXCEL_LOCK_FILE)
        with lock:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=False):
                if row[0].value == task_id:
                    # Ensure the row has enough cells
                    while len(row) < 20:
                        ws.cell(row=row[0].row, column=len(row)+1, value='')
                    
                    row[10].value = new_status
                    if new_status == 'Paused':
                        if not row[13].value:  # First pause
                            row[13].value = timestamp
                            row[14].value = pause_reason
                        elif not row[16].value:  # Second pause
                            row[16].value = timestamp
                            row[17].value = pause_reason
                    elif new_status == 'en proceso':
                        if row[13].value and not row[15].value:  # First resume
                            row[15].value = timestamp
                        elif row[16].value and not row[18].value:  # Second resume
                            row[18].value = timestamp
                    elif new_status == 'Finished':
                        row[19].value = timestamp
                    break
            wb.save(EXCEL_FILE)

    @staticmethod
    def get_user_tasks(worker_number):
        lock = FileLock(EXCEL_LOCK_FILE)
        with lock:
            wb = openpyxl.load_workbook(EXCEL_FILE)
            ws = wb.active
            user_tasks = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if str(row[2]) == str(worker_number):
                    task = {
                        'task_id': row[0],
                        'start_time': row[1],
                        'worker_number': row[2],
                        'user': row[4],
                        'project': row[6],
                        'house_number': row[7],
                        'n_modulo': row[8],
                        'activity': row[9],
                        'status': row[10],
                    }
                    user_tasks.append(task)
            return user_tasks
