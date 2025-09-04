from fastapi import Depends, APIRouter
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from fastapi.responses import PlainTextResponse
from source.routes.admin.crud import get_all_chat_id, get_message_history
from source.database.database import get_db
from sqlalchemy.orm import Session
from pydantic_ai.messages import ModelMessage
from uuid import UUID

admin_router = APIRouter()

@admin_router.get('/get-message-histroy', response_model=list[ModelMessage])
async def get_history(chat_id: UUID, session: SessionContainer = Depends(verify_session())):
    return get_message_history(chat_id)

@admin_router.get('/get-user')
async def get_user_id(session: SessionContainer = Depends(verify_session())):
    return {"user_id": session.get_user_id()}

@admin_router.post('/signout')
async def signout(session: SessionContainer = Depends(verify_session())):
    session.revoke_session()
    return PlainTextResponse(content="success")

@admin_router.get('/get-chat-IDs')
async def get_chat_ids(session: SessionContainer = Depends(verify_session())):
    print(get_all_chat_id(session.get_user_id()))
    return get_all_chat_id(session.get_user_id())