from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from app.models import Task, SQLAlchemyError
from app.utils import format_timestamp, parse_timestamp
from datetime import datetime
from app.database import db
from app.data_manager import load_worker_data, load_project_data, load_activity_data
import uuid
from collections import Counter
import logging

bp = Blueprint('main', __name__)

@bp.before_request
def load_data():
    if not hasattr(current_app, 'supervisors') or not hasattr(current_app, 'workers'):
        current_app.supervisors, current_app.workers = load_worker_data(current_app.config['WORKER_DATA_URL'])
    if not hasattr(current_app, 'projects'):
        current_app.projects = load_project_data(current_app.config['PROJECT_DATA_PATH'])
    if not hasattr(current_app, 'activities'):
        current_app.activities = load_activity_data(current_app.config['ACTIVITY_DATA_PATH'])

@bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    
    line = session.get('line', 'L1')
    station = session.get('station', 1)
    
    error = request.args.get('error')
    return render_template('index.html', supervisors=current_app.supervisors.keys(), line=line, station=station, error=error)

@bp.route('/get_workers/<supervisor>')
def get_workers(supervisor):
    workers_list = current_app.supervisors.get(supervisor, [])
    return jsonify({'workers': workers_list})

@bp.route('/submit', methods=['POST'])
def submit():
    current_app.logger.debug("Submit route called")
    identification_method = request.form['identification_method']
    current_app.logger.debug(f"Identification method: {identification_method}")
    if identification_method == 'worker_number':
        worker_number = request.form['worker_number']
        current_app.logger.debug(f"Worker number: {worker_number}")
        worker = next((w for w in current_app.workers.values() if str(w['number']) == worker_number), None)
        if worker:
            current_app.logger.debug(f"Worker found: {worker}")
            session['user'] = {
                'name': worker['name'],
                'number': worker['number'],
                'supervisor': worker['supervisor'],
                'specialty': worker['specialty'],
                'gender': worker['gender'],
                'line': session.get('line', 'L1'),
                'station': session.get('station', 1)
            }
            current_app.logger.debug("Redirecting to dashboard")
            return redirect(url_for('main.dashboard'))
        else:
            current_app.logger.debug("Invalid worker number")
            flash('Número de trabajador inválido', 'danger')
            return redirect(url_for('main.index'))
    elif identification_method == 'supervisor':
        worker_name = request.form['worker_name']
        supervisor = request.form['supervisor']
        current_app.logger.debug(f"Worker name: {worker_name}, Supervisor: {supervisor}")
        worker = current_app.workers.get(worker_name)
        if worker and worker['supervisor'] == supervisor:
            current_app.logger.debug(f"Worker found: {worker}")
            session['user'] = {
                'name': worker['name'],
                'number': worker['number'],
                'supervisor': worker['supervisor'],
                'specialty': worker['specialty'],
                'gender': worker['gender'],
                'line': session.get('line', 'L1'),
                'station': session.get('station', 1)
            }
            current_app.logger.debug("Redirecting to dashboard")
            return redirect(url_for('main.dashboard'))
        else:
            current_app.logger.debug("Worker not found or incorrect supervisor")
            flash('Trabajador no encontrado o supervisor incorrecto', 'danger')
            return redirect(url_for('main.index'))
    current_app.logger.debug("Invalid identification method")
    flash('Método de identificación inválido', 'danger')
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
def dashboard():
    current_app.logger.debug("Dashboard route called")
    if 'user' not in session:
        current_app.logger.debug("User not in session, redirecting to index")
        return redirect(url_for('main.index'))
    
    # Refresh user data
    worker_number = session['user']['number']
    user = next((w for w in current_app.workers.values() if w['number'] == worker_number), None)
    if not user:
        current_app.logger.error(f"User with number {worker_number} not found in updated data")
        return redirect(url_for('main.logout'))
    
    session['user'] = user
    current_app.logger.debug(f"Updated user in session: {user}")
    
    if 'name' not in user:
        user['name'] = 'Usuario'
    else:
        user['name'] = ' '.join(word.capitalize() for word in user['name'].split())
    
    try:
        active_tasks = Task.get_active_tasks(user['number'])
        current_app.logger.debug(f"Active tasks: {active_tasks}")
        
        active_task = next((task for task in active_tasks if task.status == 'en proceso'), None)
        paused_tasks = [task for task in active_tasks if task.status == 'Paused']
        
        welcome_message = "Bienvenida" if user.get('gender') == 'F' else "Bienvenido"
        
        current_app.logger.debug(f"Active task: {active_task}")
        current_app.logger.debug(f"Paused tasks: {paused_tasks}")
        
        current_app.logger.debug("Rendering dashboard template")
        return render_template('dashboard.html', user=user, active_task=active_task, paused_tasks=paused_tasks, welcome_message=welcome_message, worker_number=user['number'])
    except SQLAlchemyError as e:
        current_app.logger.error(f"SQLAlchemy error in dashboard: {str(e)}")
        db.session.rollback()
        flash(f'Error al cargar las tareas: {str(e)}', 'danger')
        session.pop('user', None)  # Clear the user session on error
        return redirect(url_for('main.index'))

@bp.route('/start_new_task', methods=['GET', 'POST'])
def start_new_task():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
    user = session['user']
    
    try:
        if request.method == 'POST':
            active_tasks = Task.get_active_tasks(user['number'])
            if any(task.status == 'en proceso' for task in active_tasks):
                return jsonify({'success': False, 'message': 'Ya tiene una tarea activa. Por favor, finalícela o páusela antes de iniciar una nueva.'})
            
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
                return jsonify({'success': False, 'message': 'Ya iniciaste esta tarea para este módulo'})
            
            # Check for finished tasks
            finished_task = Task.get_finished_task(project, house_number, n_modulo, activity)
            if finished_task:
                return jsonify({'success': False, 'message': 'Esta tarea ya ha sido realizada para este módulo'})
            
            session['last_project'] = project
            session['last_house_number'] = house_number
            session['last_n_modulo'] = n_modulo
            
            try:
                new_task = Task.add_task(
                    worker_number=user['number'],
                    worker_name=user['name'],
                    project=project,
                    house=house_number,
                    module=n_modulo,
                    activity=activity,
                    station_i=session.get('station', 1),  # Use get() with a default value
                    line=session.get('line', 'L1')  # Use get() with a default value
                )
            
                if new_task:
                    current_app.logger.info(f"New task created successfully: {new_task.to_dict()}")
                    return jsonify({'success': True, 'message': 'Nueva tarea iniciada con éxito'})
                else:
                    current_app.logger.error("Task.add_task returned None")
                    return jsonify({'success': False, 'message': 'Error al iniciar la tarea: La función add_task devolvió None'})
            except Exception as e:
                current_app.logger.error(f"Error creating new task: {str(e)}")
                return jsonify({'success': False, 'message': f'Error al iniciar la tarea: {str(e)}'})
        else:
            projects_data = {project: current_app.projects[project] for project in current_app.projects}
            
            # Get the most frequent tasks for the user
            user_tasks = Task.get_user_tasks(user['number'])
            task_counter = Counter(task.activity for task in user_tasks)
            frequent_tasks = [task for task, count in task_counter.most_common(3) if count >= 2]
            
            last_project = session.get('last_project', '')
            last_house_number = session.get('last_house_number', '')
            last_n_modulo = session.get('last_n_modulo', '')
            
            all_activities = [activity for specialty_activities in current_app.activities.values() for activity in specialty_activities]
            user_activities = current_app.activities.get(user['specialty'], [])
            other_activities = list(set(all_activities) - set(user_activities))
            
            # Get the number of modules for the last selected project
            num_modulos = projects_data.get(last_project, {}).get('num_modulos', 1) if last_project else 1
            
            return render_template('start_new_task.html', 
                                   user=user, 
                                   projects=projects_data, 
                                   activities=current_app.activities,
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
        return jsonify({'success': False, 'message': f'Error al iniciar la tarea: {str(e)}'}), 500

@bp.route('/pause_task', methods=['POST'])
def pause_task():
    if 'user' not in session:
        current_app.logger.warning("User not in session, returning unauthorized")
        return redirect(url_for('main.index'))
    
    task_id = request.form.get('task_id')
    pause_type = request.form.get('pause_type')
    
    current_app.logger.debug(f"Attempting to pause task with ID: {task_id}")
    current_app.logger.debug(f"Form data: {request.form}")
    current_app.logger.debug(f"Session data: {session}")
    
    if not task_id:
        current_app.logger.error("No task_id provided in the form data")
        flash('No se proporcionó ID de tarea', 'danger')
        return redirect(url_for('main.dashboard'))
    
    pause_reason_map = {
        'end_of_day': "Final del día",
        'lunch_break': "Pausa para almorzar",
        'lack_of_materials': f"Falta de materiales: {request.form.get('materials_reason', '')}",
        'other': f"Otra razón: {request.form.get('other_reason', '')}"
    }
    pause_reason = pause_reason_map.get(pause_type, "")
    
    timestamp = parse_timestamp(format_timestamp())
    
    try:
        task = Task.get_task_by_id(task_id)
        if not task:
            current_app.logger.error(f"Task with ID {task_id} not found in the database")
            flash('Tarea no encontrada en la base de datos', 'danger')
            return redirect(url_for('main.dashboard'))
        
        current_app.logger.debug(f"Task found: {task.to_dict()}")
        current_app.logger.debug(f"Session user: {session['user']}")
        
        if str(task.worker_number) != str(session['user']['number']):
            current_app.logger.error(f"Task {task_id} does not belong to the current user")
            current_app.logger.debug(f"Task worker number: {task.worker_number}, Session user number: {session['user']['number']}")
            flash('Esta tarea no pertenece al usuario actual', 'danger')
            return redirect(url_for('main.dashboard'))
        
        if task.status == 'Paused':
            current_app.logger.warning(f"Task {task_id} is already paused")
            flash('Esta tarea ya está pausada', 'warning')
            return redirect(url_for('main.dashboard'))
        
        task.status = 'Paused'
        if not task.pause_1_time:
            task.pause_1_time = timestamp
            task.pause_1_reason = pause_reason
        elif not task.pause_2_time:
            task.pause_2_time = timestamp
            task.pause_2_reason = pause_reason
        else:
            current_app.logger.warning(f"Task {task_id} has already been paused twice")
            flash('Esta tarea ya ha sido pausada dos veces', 'warning')
            return redirect(url_for('main.dashboard'))
        
        db.session.commit()
        
        # Validate the data after the commit
        updated_task = Task.get_task_by_id(task_id)
        if (task.pause_1_time and updated_task.pause_1_time != task.pause_1_time) or \
           (task.pause_2_time and updated_task.pause_2_time != task.pause_2_time):
            current_app.logger.error(f"Pause time and reason were not correctly written to the database for task {task_id}")
            flash('Error al guardar la información de pausa en la base de datos', 'danger')
            return redirect(url_for('main.dashboard'))
        
        current_app.logger.info(f"Task {task_id} paused successfully")
        current_app.logger.debug(f"DEBUG: Task paused - ID: {task_id}, Timestamp: {timestamp}, Reason: {pause_reason}")
        
        flash('Tarea pausada con éxito', 'success')
        return redirect(url_for('main.dashboard'))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"SQLAlchemy error pausing task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al pausar la tarea: {str(e)}'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error pausing task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error inesperado al pausar la tarea: {str(e)}'}), 500

@bp.route('/resume_task', methods=['POST'])
def resume_task():
    if 'user' not in session:
        current_app.logger.warning("User not in session")
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
    
    user = session['user']
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        task_id = data.get('task_id')
    else:
        task_id = request.form.get('task_id')
    
    current_app.logger.debug(f"Attempting to resume task with ID: {task_id}")
    current_app.logger.debug(f"Request data: {request.get_data()}")
    current_app.logger.debug(f"Session data: {session}")
    
    if not task_id:
        current_app.logger.error("No task_id provided in the request data")
        return jsonify({'success': False, 'message': 'No se proporcionó un ID de tarea válido'}), 400
    
    try:
        active_task = Task.get_active_task(user['number'])
        if active_task:
            current_app.logger.warning(f"User {user['number']} already has an active task")
            return jsonify({'success': False, 'message': 'Ya tiene una tarea activa. Por favor, finalícela o páusela antes de reanudar otra.'}), 400
        
        task = Task.get_task_by_id(task_id)
        if not task:
            current_app.logger.error(f"Task with ID {task_id} not found")
            return jsonify({'success': False, 'message': 'Tarea no encontrada'}), 404
        
        if task.status != 'Paused':
            current_app.logger.warning(f"Task {task_id} is not in Paused state")
            return jsonify({'success': False, 'message': 'Esta tarea no está pausada y no puede ser reanudada'}), 400
        
        timestamp = parse_timestamp(format_timestamp())
        updated_task = Task.update_task(task_id, 'en proceso', timestamp)
        if updated_task:
            current_app.logger.info(f"Task {task_id} resumed successfully")
            return jsonify({'success': True, 'message': 'Tarea reanudada con éxito'})
        else:
            current_app.logger.error(f"Failed to resume task {task_id}")
            return jsonify({'success': False, 'message': 'Error al reanudar la tarea'}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"SQLAlchemy error resuming task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al reanudar la tarea: {str(e)}'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error resuming task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error inesperado al reanudar la tarea: {str(e)}'}), 500

@bp.route('/finish_task', methods=['POST'])
def finish_task():
    if 'user' not in session:
        current_app.logger.warning("User not in session")
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

    task_id = request.form.get('task_id')
    timestamp = datetime.now()
    station = session.get('station')

    current_app.logger.debug(f"Attempting to finish task with ID: {task_id}")
    current_app.logger.debug(f"Form data: {request.form}")
    current_app.logger.debug(f"Session data: {session}")

    if not task_id:
        current_app.logger.error("No task_id provided in the form data")
        return jsonify({'success': False, 'message': 'No se proporcionó un ID de tarea válido'}), 400

    try:
        task = Task.get_task_by_id(task_id)
        if not task:
            current_app.logger.error(f"Task with ID {task_id} not found in the database")
            return jsonify({'success': False, 'message': 'Tarea no encontrada en la base de datos'}), 404

        if str(task.worker_number) != str(session['user']['number']):
            current_app.logger.error(f"Task {task_id} does not belong to the current user")
            return jsonify({'success': False, 'message': 'Esta tarea no pertenece al usuario actual'}), 403

        if task.status not in ['en proceso', 'Paused']:
            current_app.logger.warning(f"Task {task_id} is not in a valid state to be finished")
            return jsonify({'success': False, 'message': 'Esta tarea no está en un estado válido para ser finalizada'}), 400

        related_tasks = Task.get_related_active_tasks(task.project, task.house, task.module, task.activity)
        if len(related_tasks) > 1:
            active_tasks = [t for t in related_tasks if t.status == 'en proceso']
            if len(active_tasks) > 1:
                return jsonify({'success': False, 'message': 'No se puede finalizar la tarea porque hay otra persona trabajando en la misma tarea. Debe pausar su tarea primero.'}), 400

        finished_tasks = Task.finish_related_tasks(task.project, task.house, task.module, task.activity, timestamp, station)
        if finished_tasks:
            current_app.logger.info(f"Successfully finished related tasks for Project: {task.project}, House: {task.house}, Module: {task.module}, Activity: {task.activity}")
            return jsonify({'success': True, 'message': 'Tarea(s) finalizada(s) con éxito'})
        else:
            current_app.logger.error(f"Failed to finish related tasks for task {task_id}")
            return jsonify({'success': False, 'message': 'Error al finalizar la(s) tarea(s)'}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"SQLAlchemy error finishing task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al finalizar la tarea: {str(e)}'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error finishing task: {str(e)}")
        return jsonify({'success': False, 'message': f'Error inesperado al finalizar la tarea: {str(e)}'}), 500

@bp.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user' not in session:
        current_app.logger.warning("User not in session")
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

    task_id = request.form.get('task_id')
    comment = request.form.get('comment')

    current_app.logger.debug(f"Attempting to add comment to task with ID: {task_id}")
    current_app.logger.debug(f"Comment: {comment}")

    if not task_id or not comment:
        current_app.logger.error("No task_id or comment provided in the form data")
        return jsonify({'success': False, 'message': 'No se proporcionó un ID de tarea válido o un comentario'}), 400

    try:
        task = Task.get_task_by_id(task_id)
        if not task:
            current_app.logger.error(f"Task with ID {task_id} not found in the database")
            return jsonify({'success': False, 'message': 'Tarea no encontrada en la base de datos'}), 404

        if str(task.worker_number) != str(session['user']['number']):
            current_app.logger.error(f"Task {task_id} does not belong to the current user")
            return jsonify({'success': False, 'message': 'Esta tarea no pertenece al usuario actual'}), 403

        task.comment = comment
        db.session.commit()

        current_app.logger.info(f"Successfully added comment to task {task_id}")
        return jsonify({'success': True, 'message': 'Comentario agregado con éxito'})
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"SQLAlchemy error adding comment: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al agregar el comentario: {str(e)}'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error adding comment: {str(e)}")
        return jsonify({'success': False, 'message': f'Error inesperado al agregar el comentario: {str(e)}'}), 500

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

@bp.route('/check_data_update')
def check_data_update():
    last_update_time = current_app.config.get('LAST_WORKER_DATA_UPDATE')
    return jsonify({'last_update': last_update_time})

@bp.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    db.session.rollback()
    # Log the error
    print(f"Database error occurred: {str(error)}")
    return "An error occurred with the database. Please try again later.", 500
