from pydantic import BaseModel


class ChatSchema(BaseModel):
    type: str = 'textMessageEvent'
    name: str
    message: str
