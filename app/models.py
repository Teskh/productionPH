from datetime import datetime
from .database import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    worker_number = db.Column(db.String(50), nullable=False)
    supervisor = db.Column(db.String(100))
    worker_name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    project = db.Column(db.String(100), nullable=False)
    house = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    station_i = db.Column(db.String(50))
    station_f = db.Column(db.String(50))
    line = db.Column(db.String(50))
    pause_1_time = db.Column(db.DateTime)
    pause_1_reason = db.Column(db.String(200))
    resume_1_time = db.Column(db.DateTime)
    pause_2_time = db.Column(db.DateTime)
    pause_2_reason = db.Column(db.String(200))
    resume_2_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Task {self.id} - {self.worker_name} - {self.activity}>'
    @staticmethod
    def get_active_tasks(worker_number):
        return Task.query.filter(Task.worker_number == worker_number, Task.status.in_(['en proceso', 'Paused'])).all()

    @staticmethod
    def get_all_active_tasks():
        return Task.query.filter_by(status='en proceso').all()

    @staticmethod
    def get_active_task(worker_number):
        tasks = Task.get_active_tasks(worker_number)
        return next((task for task in tasks if task.status == 'en proceso'), None)

    @staticmethod
    def add_task(worker_number, worker_name, project, house, module, activity, station_i, line):
        try:
            new_task = Task(
                worker_number=worker_number,
                worker_name=worker_name,
                project=project,
                house=house,
                module=module,
                activity=activity,
                start_time=datetime.now(),
                status='en proceso',
                station_i=station_i,
                line=line
            )
            db.session.add(new_task)
            db.session.commit()
            current_app.logger.info(f"New task added successfully: {new_task.to_dict()}")
            return new_task
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"SQLAlchemy error adding task: {str(e)}")
            return None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error adding task: {str(e)}")
            return None

    @staticmethod
    def update_task(task_id, new_status, timestamp=None, pause_reason=None, station=None):
        from flask import current_app
        try:
            task = Task.query.get(task_id)
            if task:
                current_app.logger.debug(f"Updating task: {task.to_dict()}")
                task.status = new_status
                if new_status == 'Paused':
                    if not task.pause_1_time:
                        task.pause_1_time = timestamp
                        task.pause_1_reason = pause_reason
                    elif not task.pause_2_time:
                        task.pause_2_time = timestamp
                        task.pause_2_reason = pause_reason
                    else:
                        current_app.logger.warning(f"Task {task_id} has already been paused twice")
                        return None
                elif new_status == 'en proceso':
                    if task.pause_1_time and not task.resume_1_time:
                        task.resume_1_time = timestamp
                    elif task.pause_2_time and not task.resume_2_time:
                        task.resume_2_time = timestamp
                elif new_status == 'Finished':
                    task.end_time = timestamp
                    task.station_f = station
                db.session.commit()
                current_app.logger.info(f"Task {task_id} updated successfully")
                # Debug print
                print(f"DEBUG: Task updated in database - ID: {task_id}, Status: {new_status}, Timestamp: {timestamp}, Reason: {pause_reason}")
                return task
            current_app.logger.error(f"Task with ID {task_id} not found")
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"SQLAlchemy error updating task: {str(e)}")
            return None

    @staticmethod
    def get_user_tasks(worker_number):
        return Task.query.filter_by(worker_number=worker_number).order_by(Task.start_time.desc()).all()

    @staticmethod
    def get_related_active_tasks(project, house_number, n_modulo, activity):
        return Task.query.filter(
            Task.project == project,
            Task.house == house_number,
            Task.module == n_modulo,
            Task.activity == activity,
            Task.status.in_(['en proceso', 'Paused'])
        ).all()

    @staticmethod
    def finish_task(task_id, timestamp, station):
        from flask import current_app
        try:
            task = Task.query.get(task_id)
            if task and task.status in ['en proceso', 'Paused']:
                current_app.logger.debug(f"Finishing task: {task.to_dict()}")
                task.status = 'Finished'
                task.end_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
                task.station_f = station
                db.session.commit()
                current_app.logger.info(f"Task {task_id} finished successfully")
                return task
            current_app.logger.error(f"Task with ID {task_id} not found or not in the correct status")
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"SQLAlchemy error finishing task: {str(e)}")
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time,
            'worker_number': self.worker_number,
            'supervisor': self.supervisor,
            'worker_name': self.worker_name,
            'specialty': self.specialty,
            'project': self.project,
            'house': self.house,
            'module': self.module,
            'activity': self.activity,
            'status': self.status,
            'station_i': self.station_i,
            'station_f': self.station_f,
            'line': self.line,
            'pause_1_time': self.pause_1_time,
            'pause_1_reason': self.pause_1_reason,
            'resume_1_time': self.resume_1_time,
            'pause_2_time': self.pause_2_time,
            'pause_2_reason': self.pause_2_reason,
            'resume_2_time': self.resume_2_time,
            'end_time': self.end_time,
            'comment': self.comment
        }

    @staticmethod
    def get_task_by_id(task_id):
        from flask import current_app
        task = Task.query.get(task_id)
        if task:
            current_app.logger.debug(f"Task found: {task.to_dict()}")
        else:
            current_app.logger.error(f"No task found with ID: {task_id}")
        return task


    @staticmethod
    def get_finished_task(project, house_number, n_modulo, activity):
        return Task.query.filter_by(
            project=project,
            house=house_number,
            module=n_modulo,
            activity=activity,
            status='Finished'
        ).first()
