from app.models import Task
from app.database import db
from datetime import datetime, time
from sqlalchemy.exc import SQLAlchemyError

def pause_active_tasks():
    end_of_day = datetime.combine(datetime.now().date(), time(14, 22, 00))
    try:
        active_tasks = Task.query.filter_by(status='en proceso').all()
        for task in active_tasks:
            task.status = 'Paused'
            task.end_time = end_of_day
        db.session.commit()
        print(f"Paused {len(active_tasks)} active tasks at end of day.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error pausing active tasks: {str(e)}")
