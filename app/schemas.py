from typing import Literal, TypeAlias, TypedDict

from pydantic import BaseModel

TypeMessages: TypeAlias = Literal[
    'textMessageEvent',
    'superChatEvent',
    'superStickerEvent',
    'newSponsorEvent',
]


class ChatSchema(BaseModel):
    type: TypeMessages = 'textMessageEvent'
    name: str
    message: str


class ChatMessage(TypedDict):
    type: str
    name: str
    message: str
