from fastapi import Depends, APIRouter, HTTPException
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from source.routes.projects.crud import add_project_entry, get_project_entries, delete_project_entry
from source.database.database import get_db
from sqlalchemy.orm import Session
from source.schemas import CreateProjectResponse, GetProjectsIDsResponse
from uuid import UUID

project_router = APIRouter()

@project_router.post('/create-project', response_model=CreateProjectResponse)
async def create_project(session: SessionContainer = Depends(verify_session())) -> dict:
    return {"project_id": add_project_entry(session.get_user_id())}

@project_router.get('/get-projects', response_model=GetProjectsIDsResponse)
async def get_projects(session: SessionContainer = Depends(verify_session())) -> list[UUID]:
    return { "project_ids": get_project_entries(session.get_user_id())}

@project_router.delete('/delete-project', response_model=UUID) 
async def delete_project(project_id: UUID, session: SessionContainer = Depends(verify_session())) -> UUID:
    deleted_project = delete_project_entry(project_id)
    if deleted_project == None:
        raise HTTPException(status_code=400, detail='The given project id does not exits')
    return project_id