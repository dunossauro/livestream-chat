from urllib.parse import unquote
from typing import Literal, TypeAlias, TypedDict

from fastapi.websockets import WebSocket
from pydantic import BaseModel, field_validator

TypeMessages: TypeAlias = Literal[
    'textMessageEvent',
    'superChatEvent',
    'superStickerEvent',
    'newSponsorEvent',
]


class WSClient(TypedDict):
    web_socket: WebSocket
    channel: Literal['messages', 'event']


class HighlightSchema(BaseModel):
    name: str
    message: str

    @field_validator('name')
    def unquote_name(cls, v):
        return unquote(v)

    @field_validator('message')
    def unquote_message(cls, v):
        return unquote(v)


class ChatMessage(TypedDict):
    type: str
    name: str
    message: str
