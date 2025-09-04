from sqlalchemy.orm import Session
from source.database.models import Projects
from uuid import UUID, uuid4
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy.orm.attributes import flag_modified
from source.database.database import get_db

def add_project_entry(user_id: UUID) -> UUID:
    with get_db() as db:
        generated_project_id = uuid4()
        new_project = Projects(
            project_id = generated_project_id,
            user_id=user_id
        )

        db.add(new_project)
        db.commit()

    return generated_project_id

def get_project_entries(user_id: UUID) -> list[UUID]:
    with get_db() as db:
        ids = db.query(Projects).with_entities(Projects.project_id).filter(Projects.user_id == user_id).order_by(Projects.created_at).all()
    
    return [id_[0] for id_ in ids]

def delete_project_entry(project_id: UUID) -> UUID:
    with get_db() as db:
        project_row = db.get(Projects, project_id)
        if project_row:
            db.delete(project_row)
            db.commit()
            return project_id
        else:
            return None