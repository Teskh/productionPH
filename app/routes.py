from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from app.models import Task, SQLAlchemyError
from app.utils import format_timestamp
from app.data_manager import load_worker_data, load_project_data, load_activity_data
from app.database import db
import uuid
from collections import Counter
import logging

bp = Blueprint('main', __name__)

supervisors = {}
workers = {}
projects = {}
activities = {}

def load_data():
    global supervisors, workers, projects, activities
    try:
        supervisors, workers = load_worker_data(current_app.config['WORKER_DATA_PATH'])
        projects = load_project_data(current_app.config['PROJECT_DATA_PATH'])
        activities = load_activity_data(current_app.config['ACTIVITY_DATA_PATH'])
        logging.info("Data loaded successfully")
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        flash("Error al cargar los datos. Por favor, contacte al administrador.", "danger")

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
    
    try:
        active_tasks = Task.get_active_tasks(user['number'])
        
        active_task = next((task for task in active_tasks if task.status == 'en proceso'), None)
        paused_tasks = [task for task in active_tasks if task.status == 'Paused']
        
        welcome_message = "Bienvenida" if user.get('gender') == 'F' else "Bienvenido"
        
        return render_template('dashboard.html', user=user, active_task=active_task, paused_tasks=paused_tasks, welcome_message=welcome_message)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error al cargar las tareas: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/start_new_task', methods=['GET', 'POST'])
def start_new_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    user = session['user']
    
    try:
        active_tasks = Task.get_active_tasks(user['number'])
        if any(task.status == 'en proceso' for task in active_tasks):
            flash('Ya tiene una tarea activa. Por favor, finalícela o páusela antes de iniciar una nueva.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        projects_data = {project: projects[project] for project in projects}
        
        # Get the most frequent tasks for the user
        user_tasks = Task.get_user_tasks(user['number'])
        task_counter = Counter(task.activity for task in user_tasks)
        frequent_tasks = [task for task, count in task_counter.most_common(3) if count >= 2]

        if request.method == 'POST':
            project = request.form['project']
            house_number = request.form['house_number']
            n_modulo = request.form['n_modulo']
            activity = request.form['activity']
            
            # Check for existing active tasks
            existing_task = next((task for task in active_tasks if 
                                  task.worker_name == user['name'] and
                                  task.activity == activity and
                                  task.project == project and
                                  str(task.house) == str(house_number) and
                                  str(task.module) == str(n_modulo)), None)
            
            if existing_task:
                flash('Ya iniciaste esta tarea para este módulo', 'warning')
                return render_template('start_new_task.html', 
                                       user=user, 
                                       projects=projects_data, 
                                       activities=activities,
                                       user_specialty=user['specialty'],
                                       line=session.get('line', 'L1'),
                                       station_i=session.get('station', 1),
                                       last_project=project,
                                       last_house_number=house_number,
                                       last_n_modulo=n_modulo,
                                       frequent_tasks=frequent_tasks,
                                       num_modulos=projects_data[project]['num_modulos'])
            
            # Check for finished tasks
            finished_task = Task.get_finished_task(project, house_number, n_modulo, activity)
            if finished_task:
                flash('Esta tarea ya ha sido realizada para este módulo', 'warning')
                return render_template('start_new_task.html', 
                                       user=user, 
                                       projects=projects_data, 
                                       activities=activities,
                                       user_specialty=user['specialty'],
                                       line=session.get('line', 'L1'),
                                       station_i=session.get('station', 1),
                                       last_project=project,
                                       last_house_number=house_number,
                                       last_n_modulo=n_modulo,
                                       frequent_tasks=frequent_tasks,
                                       num_modulos=projects_data[project]['num_modulos'])
            
            session['last_project'] = project
            session['last_house_number'] = house_number
            session['last_n_modulo'] = n_modulo
            
            new_task = Task.add_task(
                worker_number=user['number'],
                worker_name=user['name'],
                project=project,
                house=house_number,
                module=n_modulo,
                activity=activity,
                station_i=session['station'],
                line=session['line']
            )
            
            if new_task:
                flash('Nueva tarea iniciada con éxito', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Error al iniciar la tarea', 'danger')
        
        last_project = session.get('last_project', '')
        last_house_number = session.get('last_house_number', '')
        last_n_modulo = session.get('last_n_modulo', '')
        
        all_activities = [activity for specialty_activities in activities.values() for activity in specialty_activities]
        user_activities = activities.get(user['specialty'], [])
        other_activities = list(set(all_activities) - set(user_activities))
        
        # Get the number of modules for the last selected project
        num_modulos = projects_data.get(last_project, {}).get('num_modulos', 1) if last_project else 1
        
        return render_template('start_new_task.html', 
                               user=user, 
                               projects=projects_data, 
                               activities=activities,
                               user_specialty=user['specialty'],
                               line=session.get('line', 'L1'),
                               station_i=session.get('station', 1),
                               last_project=last_project,
                               last_house_number=last_house_number,
                               last_n_modulo=last_n_modulo,
                               frequent_tasks=frequent_tasks,
                               num_modulos=num_modulos)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error al iniciar la tarea: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@bp.route('/pause_task', methods=['POST'])
def pause_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    task_id = request.form.get('task_id')
    pause_type = request.form.get('pause_type')
    pause_reason = ""

    if pause_type == 'end_of_day':
        pause_reason = "Final del día"
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
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error al pausar la tarea: {str(e)}', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/resume_task', methods=['POST'])
def resume_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    user = session['user']
    task_id = request.form.get('task_id')
    
    try:
        active_task = Task.get_active_task(user['number'])
        if active_task:
            flash('Ya tiene una tarea activa. Por favor, finalícela o páusela antes de reanudar otra.', 'error')
            return redirect(url_for('main.dashboard'))
        
        timestamp = format_timestamp()
        Task.update_task(task_id, 'en proceso', timestamp)
        flash('Tarea reanudada con éxito', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error al reanudar la tarea: {str(e)}', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/finish_task', methods=['POST'])
def finish_task():
    if 'user' not in session:
        return redirect(url_for('main.index'))
    task_id = request.form.get('task_id')
    timestamp = format_timestamp()
    
    try:
        # Get the task details
        task = Task.get_task_by_id(task_id)
        if not task:
            flash('Tarea no encontrada', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Check for related active tasks
        related_tasks = Task.get_related_active_tasks(task.project, task.house, task.module, task.activity)
        
        # If there are other active related tasks, don't allow finishing
        if len(related_tasks) > 1:  # > 1 because it includes the current task
            flash('No se puede finalizar la tarea porque otros usuarios tienen la misma tarea activa', 'warning')
            return redirect(url_for('main.dashboard'))
        
        # Finish the task for all related users (including paused tasks)
        Task.finish_related_tasks(task.project, task.house, task.module, task.activity, timestamp, session['station'])
        flash('Tarea finalizada con éxito para todos los usuarios relacionados', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
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

@bp.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
    
    task_id = request.form.get('task_id')
    comment = request.form.get('comment')
    
    if not task_id or not comment:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    try:
        Task.add_comment(task_id, comment)
        return jsonify({'success': True, 'message': 'Comentario agregado con éxito'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al agregar comentario: {str(e)}'}), 500
@bp.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    db.session.rollback()
    # Log the error
    print(f"Database error occurred: {str(error)}")
    return "An error occurred with the database. Please try again later.", 500
