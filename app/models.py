from datetime import datetime
from .database import db
from sqlalchemy.exc import SQLAlchemyError

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_number = db.Column(db.String(50), nullable=False)
    worker_name = db.Column(db.String(100), nullable=False)
    project = db.Column(db.String(100), nullable=False)
    house = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    station_i = db.Column(db.String(50))
    line = db.Column(db.String(50))
    station_f = db.Column(db.String(50))

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
        return next((task for task in tasks if task['status'] == 'en proceso'), None)

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
            return new_task
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error adding task: {str(e)}")
            return None

    @staticmethod
    def update_task(task_id, new_status, timestamp=None, pause_reason=None, station=None):
        try:
            task = Task.query.get(task_id)
            if task:
                task.status = new_status
                if new_status == 'Paused':
                    if not task.pause_1_time:
                        task.pause_1_time = timestamp
                        task.pause_1_reason = pause_reason
                    elif not task.pause_2_time:
                        task.pause_2_time = timestamp
                        task.pause_2_reason = pause_reason
                elif new_status == 'en proceso':
                    if task.pause_1_time and not task.resume_1_time:
                        task.resume_1_time = timestamp
                    elif task.pause_2_time and not task.resume_2_time:
                        task.resume_2_time = timestamp
                elif new_status == 'Finished':
                    task.end_time = timestamp
                    task.station_f = station
                db.session.commit()
                return task
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error updating task: {str(e)}")
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
    def finish_related_tasks(project, house_number, n_modulo, activity, timestamp, station):
        from flask import current_app
        from datetime import datetime
        try:
            tasks = Task.query.filter(
                Task.project == project,
                Task.house == house_number,
                Task.module == n_modulo,
                Task.activity == activity,
                Task.status.in_(['en proceso', 'Paused'])
            ).all()
            
            current_app.logger.debug(f"Found {len(tasks)} related tasks to finish")
            
            end_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
            
            for task in tasks:
                current_app.logger.debug(f"Finishing task: {task.to_dict()}")
                task.status = 'Finished'
                task.end_time = end_time
                task.station_f = station
            
            db.session.commit()
            current_app.logger.info("Successfully finished all related tasks")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"SQLAlchemy error finishing related tasks: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error finishing related tasks: {str(e)}")
            return False

    def to_dict(self):
        return {
            'id': self.id,
            'worker_number': self.worker_number,
            'worker_name': self.worker_name,
            'project': self.project,
            'house': self.house,
            'module': self.module,
            'activity': self.activity,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'comment': self.comment,
            'station_i': self.station_i,
            'line': self.line,
            'station_f': self.station_f
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
    def add_comment(task_id, comment):
        try:
            task = Task.query.get(task_id)
            if task:
                task.comment = comment
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error adding comment: {str(e)}")
            return False

    @staticmethod
    def get_finished_task(project, house_number, n_modulo, activity):
        return Task.query.filter_by(
            project=project,
            house=house_number,
            module=n_modulo,
            activity=activity,
            status='Finished'
        ).first()
