from pydantic import BaseModel, UUID4

class chatResponse(BaseModel):
    querry: str
    response: str
    chat_id: UUID4
    chat_data_id: UUID4


