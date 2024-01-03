from asyncio import AbstractEventLoop
from os import environ
from typing import Self

from dotenv import load_dotenv
from twitchio import Message
from twitchio.ext import commands

from .ws_manager import WebSocketManager

load_dotenv()


class Bot(commands.Bot):
    def __init__(
        self: Self,
        loop: AbstractEventLoop,
        ws: WebSocketManager,
    ) -> None:
        self.loop = loop
        self.ws_manager = ws

        super().__init__(
            token=environ['TWITCH_TOKEN'],
            prefix='!',
            initial_channels=['dunossauro'],
        )

    async def event_message(self: Self, message: Message) -> None:
        await self.ws_manager.broadcast(
            {
                'name': message.author.name,
                'message': message.content,
                'type': 'textMessageEvent',
                'channel': 'messages',
            },
        )
