from asyncio import AbstractEventLoop
from os import environ
from typing import Self

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from twitchio import Message
from twitchio.ext import commands

from .database import async_session
from .models import Comment
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

    async def event_message(
        self: Self,
        message: Message,
    ) -> None:
        if message.author:
            await self.ws_manager.broadcast(
                {
                    'name': message.author.name,
                    'message': message.content,
                    'type': 'textMessageEvent',
                    'channel': 'messages',
                },
            )
            async with async_session() as session:
                session.add(
                    Comment(
                        name=message.author.name,
                        comment=message.content,
                        live='twitch',
                    )
                )
                await session.commit()

            await self.handle_commands(message)

        else:
            await self.ws_manager.broadcast(
                {
                    'name': 'bot!',
                    'message': message.content,
                    'type': 'textMessageEvent',
                    'channel': 'messages',
                },
            )

    @commands.command(name='curso')
    async def cmd_curso(self, ctx):
        await ctx.send('https://fastapidozero.dunossauro.com')

    @commands.command(name='youtube')
    async def cmd_youtube(self, ctx):
        await ctx.send('Se inscreve lá: https://www.youtube.com/dunossauro')

    @commands.command(name='telegram')
    async def cmd_telegram(self, ctx):
        await ctx.send('https://t.me/livepython')

    @commands.command(name='git')
    async def cmd_git(self, ctx):
        await ctx.send('http://github.com/dunossauro')

    @commands.command(name='me')
    async def cmd_me(self, ctx):
        await ctx.send('Todos os meus links: https://dunossauro.com')

    @commands.command(name='apoiase')
    async def cmd_apoiase(self, ctx):
        await ctx.send('http://apoia.se/livedepython')
