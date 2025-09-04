from sqlalchemy.orm import Session
from source.database.models import Tasks
from uuid import UUID
from source.database.database import get_db

def add_task_entry(userID: UUID, taskID: UUID, projectID: UUID, chatID: UUID):
    new_task = Tasks(
        user_id = userID,
        task_id = taskID,
        project_id = projectID,
        chat_id = chatID,
        task_status = "Running"
    )
    with get_db() as db:
        db.add(new_task)
        db.commit()

def list_task_ids(userID: UUID) -> list[Tasks]:
    with get_db() as db:
        return db.query(Tasks).filter(Tasks.user_id==userID).order_by(Tasks.created_at).all()

def update_task_status_entry(userID: UUID, taskID: UUID, status: str):
    with get_db() as db:
        existing_task = db.query(Tasks).filter(Tasks.task_id==taskID, Tasks.user_id==userID).first()
        if existing_task:
            existing_task.task_status = status
        else:
            return None
        db.add(existing_task)
        db.commit()
    return status

def list_task_status(userID: UUID, taskID: UUID) -> str:
    with get_db() as db:    
        return db.query(Tasks).with_entities(Tasks.task_status).filter(Tasks.task_id==taskID, Tasks.user_id==userID).scalar()

def delete_task_entry(userID: UUID, taskID: UUID) -> UUID:
    with get_db() as db:
        task_id_row = db.get(Tasks, taskID)

        if task_id_row is None:
            print(task_id_row, "is none")
            return None
        
        if task_id_row.user_id != UUID(userID):
            print(task_id_row, "not equal", type(task_id_row.user_id), type(userID))
            return None

        db.delete(task_id_row)
        db.commit()
        return taskID