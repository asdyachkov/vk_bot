import asyncio
import typing
from logging import getLogger

from app.game.models import GameDC, RoundDC
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
            elif update.type == "message_event":
                if "callback_data" in update.object.payload.keys():
                    if (
                        update.object.payload["callback_data"]
                        == "recruiting_started"
                    ):
                        if not await self.app.store.game.is_chat_id_exists(
                            update.object.group_id
                        ):
                            if not await self.app.store.game.is_game_was_started_in_chat(
                                update.object.group_id
                            ):
                                await self.app.store.vk_api.answer_pop_up_notification(
                                    Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                    ),
                                    text="Регистрация начата",
                                )
                                await self.app.store.vk_api.start_recruiting_players(
                                    Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                        conversation_message_id=update.object.conversation_message_id,
                                    )
                                )
                                game_id = await self.app.store.game.create_game(
                                    GameDC(chat_id=int(update.object.group_id))
                                )
                                if game_id:
                                    await self.app.store.game.create_round(
                                        RoundDC(game_id=game_id)
                                    )
                                    asyncio.ensure_future(
                                        self.start_game(
                                            Message(
                                                user_id=update.object.user_id,
                                                text="",
                                                peer_id=update.object.peer_id,
                                                event_id=update.object.event_id,
                                                group_id=update.object.group_id,
                                                conversation_message_id=update.object.conversation_message_id,
                                            ),
                                            sleep=30,
                                            is_timer_end=True,
                                        )
                                    )
                            else:
                                await self.app.store.vk_api.answer_pop_up_notification(
                                    message=Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                        conversation_message_id=update.object.conversation_message_id,
                                    ),
                                    text="Игра уже идет",
                                )
                        else:
                            await self.app.store.vk_api.answer_pop_up_notification(
                                message=Message(
                                    user_id=update.object.user_id,
                                    text="",
                                    peer_id=update.object.peer_id,
                                    event_id=update.object.event_id,
                                    conversation_message_id=update.object.conversation_message_id,
                                ),
                                text="Набор в игру уже ведется",
                            )
                    elif update.object.payload["callback_data"] == "add me":
                        canceling_add = False
                        round_id = (
                            await self.app.store.game.get_round_by_group_id(
                                update.object.group_id
                            )
                        )
                        if round_id:
                            player = await self.app.store.vk_api.get_user_by_id(
                                update.object.user_id, round_id
                            )
                            if player:
                                if not await self.app.store.game.is_user_already_in_game(
                                    player
                                ):
                                    is_player_added = (
                                        await self.app.store.game.add_player(
                                            player
                                        )
                                    )
                                    if is_player_added:
                                        players = await self.app.store.game.get_players_by_round_id(
                                            round_id
                                        )
                                        await self.app.store.vk_api.edit_recruiting_players(
                                            Message(
                                                user_id=update.object.user_id,
                                                text="",
                                                peer_id=update.object.peer_id,
                                                event_id=update.object.event_id,
                                                conversation_message_id=update.object.conversation_message_id,
                                            ),
                                            players,
                                        )
                                    else:
                                        canceling_add = True
                                else:
                                    canceling_add = True
                            else:
                                canceling_add = True
                        else:
                            canceling_add = True
                        if canceling_add:
                            await self.app.store.vk_api.answer_pop_up_notification(
                                Message(
                                    user_id=update.object.user_id,
                                    text="",
                                    peer_id=update.object.peer_id,
                                    event_id=update.object.event_id,
                                ),
                                text="Вы уже зарегестрированы в этой игре",
                            )
                    elif update.object.payload["callback_data"] == "delete me":
                        canceling_delete = False
                        round_id = (
                            await self.app.store.game.get_round_by_group_id(
                                update.object.group_id
                            )
                        )
                        if round_id:
                            player = await self.app.store.vk_api.get_user_by_id(
                                update.object.user_id, round_id
                            )
                            if player:
                                if await self.app.store.game.is_user_already_in_game(
                                    player
                                ):
                                    await self.app.store.game.delete_player(
                                        player
                                    )
                                    players = await self.app.store.game.get_players_by_round_id(
                                        round_id
                                    )
                                    await self.app.store.vk_api.edit_recruiting_players(
                                        Message(
                                            user_id=update.object.user_id,
                                            text="",
                                            peer_id=update.object.peer_id,
                                            event_id=update.object.event_id,
                                            conversation_message_id=update.object.conversation_message_id,
                                        ),
                                        players,
                                    )
                                else:
                                    canceling_delete = True
                            else:
                                canceling_delete = True
                        else:
                            canceling_delete = True
                        if canceling_delete:
                            await self.app.store.vk_api.answer_pop_up_notification(
                                Message(
                                    user_id=update.object.user_id,
                                    text="",
                                    peer_id=update.object.peer_id,
                                    event_id=update.object.event_id,
                                ),
                                text="Вы еще не зарегестрированы в этой игре",
                            )
                    elif (
                        update.object.payload["callback_data"] == "delete game"
                    ):
                        game_id = await self.app.store.game.get_last_game_id_by_chat_id(
                            update.object.group_id
                        )
                        await self.cancel_game(
                            Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id,
                                conversation_message_id=update.object.conversation_message_id,
                                group_id=update.object.group_id,
                            ),
                            game_id=game_id,
                        )
                    elif update.object.payload["callback_data"] == "start game":
                        await self.start_game(
                            Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id,
                                conversation_message_id=update.object.conversation_message_id,
                                group_id=update.object.group_id,
                            ),
                            sleep=0,
                            is_timer_end=False,
                        )

    async def start_game(
        self, message: Message, sleep: int, is_timer_end: bool
    ):
        game_id = await self.app.store.game.get_last_game_id_by_chat_id(
            message.group_id
        )
        await asyncio.sleep(sleep)
        canceling_game = False
        if game_id:
            round_id = await self.app.store.game.get_round_by_group_id(
                message.group_id
            )
            if round_id:
                players_count = (
                    await self.app.store.game.get_players_by_round_id(round_id)
                )
                if players_count:
                    if players_count > 1:
                        await self.app.store.game.start_game(game_id)
                        await self.app.store.vk_api.start_game(message)
                    else:
                        canceling_game = True
                else:
                    canceling_game = True
            else:
                canceling_game = True
        else:
            canceling_game = True
        if canceling_game and is_timer_end:
            await self.cancel_game(message, game_id)
        else:
            await self.app.store.vk_api.answer_pop_up_notification(
                message=message, text="Недостаточно игроков, чтобы начать игру"
            )

    async def cancel_game(self, message: Message, game_id: int):
        is_game_deleted = await self.app.store.game.delete_game(game_id)
        if is_game_deleted:
            await self.app.store.vk_api.edit_recruiting_players_game_delete(
                message
            )
        else:
            await self.app.store.vk_api.answer_pop_up_notification(
                message, text="Не удалось отменить игру"
            )
