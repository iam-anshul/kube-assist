from fastapi import Depends, APIRouter, HTTPException
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from source.routes.tasks.crud import add_task_entry, list_task_ids, update_task_status_entry, list_task_status, delete_task_entry
from source.database.database import get_db
from sqlalchemy.orm import Session
from source.models import AddTaskRequest, UpdateTaskStatusRequest
from source.schemas import AddTaskResponse, GetTaskStatusResponse, GetTasksIDsResponse
from source.database.models import Tasks
from uuid import UUID

task_router = APIRouter()

@task_router.post('/add-task', response_model=AddTaskResponse)
def add_task(request: AddTaskRequest, session: SessionContainer = Depends(verify_session())):
    add_task_entry(session.get_user_id(), request.task_id, request.project_id, request.chat_id)
    return {"task_id": request.task_id}

@task_router.get('/get-task-ids', response_model=list[GetTasksIDsResponse])
def get_user_task_ids(session: SessionContainer = Depends(verify_session())) -> list[GetTasksIDsResponse]:
    return list_task_ids(session.get_user_id())

@task_router.patch('/update-task-status')
def update_task_status(request: UpdateTaskStatusRequest, session: SessionContainer = Depends(verify_session())) -> str:
    updated = update_task_status_entry(session.get_user_id(), request.task_id, request.status)

    if not updated:
        raise HTTPException(status_code=400, detail='No task found with the given task id')
    
    return request.status
    
@task_router.get('/get-task-status', response_model=GetTaskStatusResponse)
def get_task_status(task_id: UUID, session: SessionContainer = Depends(verify_session())) -> GetTaskStatusResponse:
    status = list_task_status(session.get_user_id(), task_id)
    if not status:
        raise HTTPException(status_code=400, detail='No task found with the given task id')
    
    return {"task_status": status}

@task_router.delete('/delete-task')
def delete_task(task_id: UUID, session: SessionContainer = Depends(verify_session())) -> UUID:
    deleted = delete_task_entry(session.get_user_id(), task_id)
    if not deleted:
        raise HTTPException(status_code=400, detail='No task found with the given task id')
    
    return deleted

