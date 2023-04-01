import asyncio
from typing import Optional, TYPE_CHECKING

import pika
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.store.database import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None
        self.queue: Optional = None
        self.channel: Optional = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(self.app.config.database.url)
        self.queue = asyncio.Queue()
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = connection.channel()

    async def disconnect(self, *_: list, **__: dict) -> None:
        try:
            await self.session.close()
            await self._engine.dispose()
        except Exception as e:
            self.app.logger.log(1, e)
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None
