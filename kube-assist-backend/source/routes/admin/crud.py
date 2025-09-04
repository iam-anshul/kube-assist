from sqlalchemy.orm import Session
from source.database.models import ChatIDs, MessageHistory
from uuid import UUID
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from source.database.database import get_db

def get_all_chat_id(userID: UUID) -> list:
    with get_db() as db:
        iDs = db.query(ChatIDs).with_entities(ChatIDs.chat_id, ChatIDs.project_id).order_by(ChatIDs.created_at).all()
    return [{'chat_id': chat_id, 'project_id': project_id} for chat_id, project_id in iDs]

def get_message_history(chat_id: UUID) -> list[ModelMessage] | None:
    with get_db() as db:
        message_rows = db.query(MessageHistory).with_entities(MessageHistory.data).filter(MessageHistory.chat_id==chat_id).order_by(MessageHistory.created_at).all()
        
        messages: list[ModelMessage] = []
        for row in message_rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
    return messages