from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CreateProjectResponse(BaseModel):
    project_id: UUID

class GetProjectsIDsResponse(BaseModel):
    project_ids: list[UUID]

class GetChatIDs(BaseModel):
    chat_id: UUID
    project_id: UUID

class AddTaskResponse(BaseModel):
    task_status: str

class GetTaskStatusResponse(BaseModel):
    task_status: str

class GetTasksIDsResponse(BaseModel):
    user_id: UUID
    task_id: UUID
    project_id: UUID
    chat_id: UUID
    task_status: str
    created_at: datetime