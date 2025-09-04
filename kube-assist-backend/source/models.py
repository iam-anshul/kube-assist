from pydantic import BaseModel, UUID4
from typing import Literal
from uuid import UUID

class agentDeps(BaseModel):
    context_name: str
    kubeconfig_path: str
    access_key_id: str
    access_key: str

class chatRequest(BaseModel):
    prompt: str
    chat_id: UUID
    project_id: UUID
    model: Literal["openai", "anthropic"]

class kubeconfigRequest(BaseModel):
    kubeconfig_file: str
    project_id: UUID

class AddTaskRequest(BaseModel):
    chat_id: UUID
    project_id: UUID
    task_id: UUID

class UpdateTaskStatusRequest(BaseModel):
    task_id: UUID
    status: str

class set_aws_credsRequest(BaseModel):
    access_key_id: str
    access_key: str
    project_id: str
    region: str
    cluster_name: str
