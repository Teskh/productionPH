from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.models import Task
from app.utils import format_timestamp, init_excel_file
from data_manager import load_worker_data, load_project_data, load_activity_data
import uuid

bp = Blueprint('main', __name__)

supervisors, workers = load_worker_data()
projects = load_project_data()
activities = load_activity_data()

@bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    
    if 'line' not in session:
        session['line'] = 'L1'
    if 'station' not in session:
        session['station'] = 1
    
    error = request.args.get('error')
    return render_template('index.html', supervisors=supervisors.keys(), line=session['line'], station=session['station'], error=error)

@bp.route('/get_workers/<supervisor>')
def get_workers(supervisor):
    workers_list = supervisors.get(supervisor, [])
    return jsonify(workers_list)

@bp.route('/submit', methods=['POST'])
def submit():
    identification_method = request.form['identification_method']
    if identification_method == 'worker_number':
        worker_number = request.form['worker_number']
        worker = next((w for w in workers.values() if str(w['number']) == worker_number), None)
        if worker:
            session['user'] = {
                'name': worker['name'],
                'number': worker['number'],
                'supervisor': worker['supervisor'],
                'specialty': worker['specialty'],
                'gender': worker['gender'],
                'line': session.get('line', 'L1'),
                'station': session.get('station', 1)
            }
            return redirect(url_for('main.dashboard'))
        else:
            flash('Número de trabajador inválido', 'danger')
            return redirect(url_for('main.index'))
    elif identification_method == 'supervisor':
        worker_name = request.form['worker_name']
        supervisor = request.form['supervisor']
        worker = workers.get(worker_name)
        if worker and worker['supervisor'] == supervisor:
            session['user'] = {
                'name': worker['name'],
                'number': worker['number'],
                'supervisor': worker['supervisor'],
                'specialty': worker['specialty'],
                'gender': worker['gender'],
                'line': session.get('line', 'L1'),
                'station': session.get('station', 1)
            }
            return redirect(url_for('main.dashboard'))
        else:
            flash('Trabajador no encontrado o supervisor incorrecto', 'danger')
            return redirect(url_for('main.index'))
    flash('Método de identificación inválido', 'danger')
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    user = session['user']
    
    if 'name' not in user:
        user['name'] = 'Usuario'
    else:
        user['name'] = ' '.join(word.capitalize() for word in user['name'].split())
    
    active_tasks = Task.get_active_tasks(user['number'])
    
    active_task = next((task for task in active_tasks if task['status'] == 'en proceso'), None)
    paused_tasks = [task for task in active_tasks if task['status'] == 'Paused']
    
    welcome_message = "Bienvenida" if user['gender'] == 'F' else "Bienvenido"
    
    return render_template('dashboard.html', user=user, active_task=active_task, paused_tasks=paused_tasks, welcome_message=welcome_message)

@bp.route('/start_new_task', methods=['GET', 'POST'])
def start_new_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    user = session['user']
    
    active_tasks = Task.get_active_tasks(user['number'])
    if any(task['status'] == 'en proceso' for task in active_tasks):
        flash('Ya tiene una tarea activa. Por favor, finalícela o páusela antes de iniciar una nueva.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        project = request.form['project']
        house_number = request.form['house_number']
        n_modulo = request.form['n_modulo']
        activity = request.form['activity']
        
        existing_task = next((task for task in active_tasks if 
                              task['user'] == user['name'] and
                              task['activity'] == activity and
                              task['project'] == project and
                              str(task['house_number']) == str(house_number) and
                              str(task['n_modulo']) == str(n_modulo)), None)
        
        if existing_task:
            flash('Ya iniciaste esta tarea para este módulo', 'warning')
            return redirect(url_for('main.dashboard'))
        
        session['last_project'] = project
        session['last_house_number'] = house_number
        session['last_n_modulo'] = n_modulo
        
        task_data = {
            'task_id': str(uuid.uuid4()),
            'worker_number': user['number'],
            'supervisor': user['supervisor'],
            'user': user['name'],
            'specialty': user['specialty'],
            'project': project,
            'house_number': house_number,
            'n_modulo': n_modulo,
            'activity': activity,
            'status': 'en proceso',
            'station': session['station'],
            'line': session['line']
        }
        
        Task.add_task(task_data)
        flash('Nueva tarea iniciada con éxito', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    last_project = session.get('last_project', '')
    last_house_number = session.get('last_house_number', '')
    last_n_modulo = session.get('last_n_modulo', '')
    
    if last_project:
        num_modulos = projects.get(last_project, {}).get('num_modulos', 3)
    else:
        num_modulos = max(projects[p].get('num_modulos', 3) for p in projects)
    
    return render_template('start_new_task.html', 
                           user=user, 
                           projects=projects, 
                           activities=activities.get(user['specialty'], []),
                           line=session.get('line', 'L1'),
                           station=session.get('station', 1),
                           last_project=last_project,
                           last_house_number=last_house_number,
                           last_n_modulo=last_n_modulo,
                           num_modulos=num_modulos)

@bp.route('/pause_task', methods=['POST'])
def pause_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    task_id = request.form.get('task_id')
    pause_type = request.form.get('pause_type')
    pause_reason = ""

    if pause_type == 'end_of_day':
        pause_reason = "Fin del día"
    elif pause_type == 'lunch_break':
        pause_reason = "Pausa para almorzar"
    elif pause_type == 'lack_of_materials':
        materials_reason = request.form.get('materials_reason', '')
        pause_reason = f"Falta de materiales: {materials_reason}"
    elif pause_type == 'other':
        other_reason = request.form.get('other_reason', '')
        pause_reason = f"Otra razón: {other_reason}"
    
    timestamp = format_timestamp()
    try:
        Task.update_task(task_id, 'Paused', timestamp, pause_reason)
        flash('Tarea pausada con éxito', 'success')
    except Exception as e:
        flash(f'Error al pausar la tarea: {str(e)}', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/resume_task', methods=['POST'])
def resume_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    user = session['user']
    task_id = request.form.get('task_id')
    
    active_task = Task.get_active_task(user['number'])
    if active_task:
        flash('Ya tiene una tarea activa. Por favor, finalícela o páusela antes de reanudar otra.', 'error')
        return redirect(url_for('main.dashboard'))
    
    timestamp = format_timestamp()
    try:
        Task.update_task(task_id, 'en proceso', timestamp)
        flash('Tarea reanudada con éxito', 'success')
    except Exception as e:
        flash(f'Error al reanudar la tarea: {str(e)}', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/finish_task', methods=['POST'])
def finish_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    task_id = request.form.get('task_id')
    timestamp = format_timestamp()
    try:
        Task.update_task(task_id, 'Finished', timestamp)
        flash('Tarea finalizada con éxito', 'success')
    except Exception as e:
        flash(f'Error al finalizar la tarea: {str(e)}', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/get_project_details/<project>')
def get_project_details(project):
    project_details = projects.get(project, {})
    return jsonify(project_details)

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['line'] = request.form['line']
        session['station'] = int(request.form['station'])
        flash('Configuraciones actualizadas con éxito', 'success')
        return redirect(url_for('main.index'))
    return render_template('settings.html', line=session.get('line', 'L1'), station=session.get('station', 1))

@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.index'))