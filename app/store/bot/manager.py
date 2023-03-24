import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update, UpdateEvent

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update | UpdateEvent]):
        for update in updates:
            if update.type == "message_new":
                if update.object.body == "/start":
                    await self.app.store.vk_api.start_message(
                        Message(
                            user_id=update.object.user_id,
                            text=update.object.body,
                            peer_id=update.object.peer_id,
                        )
                    )
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=update.object.body,
                            peer_id=update.object.peer_id,
                        )
                    )
            elif update.type == "message_event":
                if "callback_data" in update.object.payload.keys():
                    if update.object.payload["callback_data"] == "recruiting_started":
                        await self.app.store.vk_api.answer_start_message(
                            Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id
                            )
                        )
                        await self.app.store.vk_api.start_recruiting_players(
                            Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id,
                                conversation_message_id=update.object.conversation_message_id
                            )
                        )
