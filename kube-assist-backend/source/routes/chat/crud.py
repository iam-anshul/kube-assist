from sqlalchemy.orm import Session
from source.database.models import MessageHistory, ChatIDs, Conversation
from uuid import UUID, uuid4
from sqlalchemy.orm.attributes import flag_modified
from source.database.database import get_db

def add_chatID_entry(user_id: UUID, project_id: UUID) -> UUID:
    generated_chat_id = uuid4()
    with get_db() as db:
        new_chat = ChatIDs(
            user_id = user_id,
            chat_id = generated_chat_id,
            project_id = project_id
        )
        
        db.add(new_chat)
        db.commit()

    return generated_chat_id

def delete_chatID_entry(chat_id: UUID) -> UUID:
    with get_db() as db:
        chat_id_row = db.get(ChatIDs, chat_id)
        
        db.delete(chat_id_row)
        db.commit()
    return chat_id
    

def get_conversation(chat_id: UUID, userID: UUID) -> list[dict]:
    with get_db() as db:
        conversation_rows = (
            db.query(Conversation.user_conversation)
            .filter(Conversation.chat_id == chat_id, Conversation.user_id==userID)
            .all()
        )

    return [row[0] for row in conversation_rows]  # Extract JSON values
    

def render_chat(userID: UUID) -> list:
    with get_db() as db:
        iDs = db.query(ChatIDs).with_entities(ChatIDs.chat_id, ChatIDs.project_id).filter(ChatIDs.user_id==userID).order_by(ChatIDs.created_at).all()
    return [{'chat_id': chat_id, 'project_id': project_id} for chat_id, project_id in iDs]

def add_message(userID: UUID, chat_id: UUID, message: bytes, conversation: dict, project_id: UUID):
    new_message_entry = MessageHistory(
        chat_data_id=uuid4(),
        chat_id=chat_id,
        user_id=userID,
        data=message,
        project_id = project_id
    )

    with get_db() as db:
        existing_conversation = db.query(Conversation).filter(Conversation.chat_id == chat_id).first()
        
        if existing_conversation:
            existing_conversation.user_conversation.append(conversation)
            existing_conversation.conversation_count += 1
            flag_modified(existing_conversation, "user_conversation")
        else:
            print("No conversation")
            existing_conversation = Conversation(
                id=uuid4(),
                conversation_count = 1,
                chat_id=chat_id,
                user_id=userID,
                user_conversation=[conversation],
                project_id = project_id
            )
        
        db.add(existing_conversation)
        db.add(new_message_entry)
        db.commit() 
        print("//////////////////// Added")
