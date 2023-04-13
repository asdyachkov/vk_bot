import json
import random
import typing
from typing import Optional

import aioamqp
from aioamqp import channel
from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.game.models import PlayerDC
from app.store.vk_api.dataclasses import (
    Message,
    Update,
    UpdateObject,
    UpdateEvent,
    UpdateEventObject,
)
from app.store.vk_api.keyboards import (
    create_start_keyboard,
    create_recruiting_keyboard,
    create_new_poll_keyboard,
)
from app.store.vk_api.poller import Poller
from app.web.utils import update_to_json, update_event_to_json, json_to_message

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(
        self, app: "Application", is_for_poller: bool = True, *args, **kwargs
    ):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None
        self.channel: Optional[channel] = None
        self.is_for_poller = is_for_poller

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        transport, protocol = await aioamqp.connect(
            host="localhost", port=5672, login="guest", password="guest"
        )
        self.logger.info("Transport got")
        self.channel = await protocol.channel()
        self.logger.info("Channel got")
        await self.channel.queue_declare(queue_name="to_worker", durable=True)
        self.logger.info("Queue declared")
        if self.is_for_poller:
            try:
                await self._get_long_poll_service()
            except Exception as e:
                self.logger.error("Exception", exc_info=e)
            self.poller = Poller(app.store)
            self.logger.info("start polling")
        self.logger.info("Working....")

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 1,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            for update in raw_updates:
                if update["type"] == "message_new":
                    to_send = Update(
                        type=update["type"],
                        object=UpdateObject(
                            id=update["object"]["message"]["id"],
                            user_id=update["object"]["message"]["from_id"],
                            body=update["object"]["message"]["text"],
                            peer_id=update["object"]["message"]["peer_id"],
                        ),
                    )
                    await self.channel.basic_publish(
                        payload=json.dumps(update_to_json(to_send)).encode(),
                        exchange_name="",
                        routing_key="to_worker",
                    )

                elif update["type"] == "message_event":
                    to_send = UpdateEvent(
                        type=update["type"],
                        object=UpdateEventObject(
                            user_id=update["object"]["user_id"],
                            payload=update["object"]["payload"],
                            peer_id=update["object"]["peer_id"],
                            event_id=update["object"]["event_id"],
                            group_id=update["group_id"],
                            conversation_message_id=update["object"][
                                "conversation_message_id"
                            ],
                        ),
                    )
                    await self.channel.basic_publish(
                        payload=json.dumps(
                            update_event_to_json(to_send)
                        ).encode(),
                        exchange_name="",
                        routing_key="to_worker",
                    )

    async def handle_updates(self):
        await self.channel.basic_consume(self.callback, queue_name="to_sender")

    async def callback(self, channel, body, envelope, properties):
        data = json.loads(body)
        await self.proccessing_update(data)
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def proccessing_update(self, update):
        message = json_to_message(update)
        if update["function"] == "start_message":
            await self.start_message(message)
        elif update["function"] == "answer_pop_up_notification":
            await self.answer_pop_up_notification(message, update["text"])
        elif update["function"] == "start_recruiting_players":
            await self.start_recruiting_players(message)
        elif update["function"] == "edit_recruiting_players":
            await self.edit_recruiting_players(message, update["players"])
        elif update["function"] == "create_new_poll":
            await self.create_new_poll(message, update["variants"])
        elif update["function"] == "start_game":
            await self.start_game(message)
        elif update["function"] == "edit_recruiting_players_game_delete":
            await self.edit_recruiting_players_game_delete(message)
        elif update["function"] == "end_game":
            await self.end_game(message, update["winner"])
        elif update["function"] == "edit_message_to_leaderboard":
            await self.edit_message_to_leaderboard(message)

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                    "chat_id": 86,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def start_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.peer_id,
                    "message": "❗ Чтобы начать игру, необходмо набрать достаточное количество участников ❗",
                    "access_token": self.app.config.bot.token,
                    "chat_id": 86,
                    "keyboard": create_start_keyboard(),
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def create_new_poll(
        self, message: Message, variants: list[dict]
    ) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Выберите, чей аватар лучше.%0a%0aГолосование длиться 30 секунд. 😉",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "attachment": f"photo{variants[0]['photo_id']},photo{variants[1]['photo_id']}",
                    "user_id": message.user_id,
                    "keyboard": create_new_poll_keyboard(variants),
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def answer_pop_up_notification(
        self, message: Message, text: str
    ) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.sendMessageEventAnswer",
                params={
                    "event_id": message.event_id,
                    "user_id": message.user_id,
                    "peer_id": message.peer_id,
                    "event_data": json.dumps(
                        {"type": "show_snackbar", "text": f"{text}"}
                    ),
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def start_recruiting_players(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Нажмите на кнопку ниже, чтобы запустить регистрацию%0a%0a❗ Игра начнется через 30 секунд после начала регистрации",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "user_id": message.user_id,
                    "keyboard": create_recruiting_keyboard(),
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def edit_recruiting_players(
        self, message: Message, players: int
    ) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Нажмите на кнопку ниже, чтобы зарегестрироваться%0a%0aВсего участников: {players} 😲",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "user_id": message.user_id,
                    "keyboard": create_recruiting_keyboard(),
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def edit_recruiting_players_game_delete(
        self, message: Message
    ) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Игра была отменена 😔",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "user_id": message.user_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def edit_message_to_leaderboard(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": message.text,
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "user_id": message.user_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_user_by_id(self, id_: int, round_id: int) -> PlayerDC:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "users.get",
                params={
                    "user_ids": str(id_),
                    "fields": "photo_id",
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            if "photo_id" not in data["response"][0].keys():
                data["response"][0]["photo_id"] = "6492_192164258"
            return PlayerDC(
                last_name=data["response"][0]["last_name"],
                name=data["response"][0]["first_name"],
                photo_id=data["response"][0]["photo_id"],
                round_id=round_id,
                vk_id=id_,
            )

    async def start_game(self, message: Message):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Регистрация окончена!%0a%0aПриятной игры!❤",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "user_id": message.user_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def end_game(self, message: Message, winner: dict):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "peer_id": message.peer_id,
                    "message": f"Игра закончилась!%0a%0a👑 Победитель {winner['name']} {winner['last_name']} 👑",
                    "conversation_message_id": int(
                        message.conversation_message_id
                    ),
                    "attachment": f"photo{winner['photo_id']}",
                    "user_id": message.user_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
