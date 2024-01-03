from typing import Literal, TypeAlias, TypedDict

from fastapi.websockets import WebSocket
from pydantic import BaseModel

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


class ChatMessage(TypedDict):
    type: str
    name: str
    message: str
