import asyncio
import typing
from logging import getLogger

from app.game.models import GameDC, RoundDC, PlayerDC
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
                if update.object.body == "/bot":
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
                        # добавить проверку началась ли игра
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
                                    is_player_added_to_leaderboard = await self.app.store.game.is_player_added_to_leaderboard(
                                        player.vk_id
                                    )
                                    is_player_added = (
                                        await self.app.store.game.add_player(
                                            player,
                                            is_player_added_to_leaderboard
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
                    elif "vk_id" in update.object.payload[
                        "callback_data"
                    ].split(":"):
                        (
                            is_score_increased,
                            round_id,
                        ) = await self.increase_player_score(update)
                        if is_score_increased:
                            message = Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id,
                                group_id=update.object.group_id,
                                conversation_message_id=update.object.conversation_message_id,
                            )
                            game_id = await self.app.store.game.is_game_was_started_in_chat(
                                message.group_id
                            )
                            (
                                round_state,
                                round_id,
                            ) = await self.app.store.game.get_round_state_by_game_id(game_id)
                            variants = await self.app.store.game.get_two_players_photo(
                                round_state, round_id, for_update=True
                            )
                            await self.app.store.vk_api.create_new_poll(
                                message,
                                variants,
                            )
                            await self.app.store.vk_api.answer_pop_up_notification(
                                message,
                                text="Ваш голос учтен",
                            )
                            await self.app.store.game.make_user_already_voited(
                                round_id, update.object.user_id
                            )
                        else:
                            await self.app.store.vk_api.answer_pop_up_notification(
                                Message(
                                    user_id=update.object.user_id,
                                    text="",
                                    peer_id=update.object.peer_id,
                                    event_id=update.object.event_id,
                                ),
                                text="Голосовать могут только пользователи, участвующие в игре и только один раз за раунд",
                            )
                    elif update.object.payload["callback_data"] == "check_leaderboard":
                        await self.show_leaderboard(
                            Message(
                                user_id=update.object.user_id,
                                text="",
                                peer_id=update.object.peer_id,
                                event_id=update.object.event_id,
                                conversation_message_id=update.object.conversation_message_id,
                                group_id=update.object.group_id,
                            )
                        )

    async def start_game(
        self, message: Message, sleep: int, is_timer_end: bool
    ):
        game_id = await self.app.store.game.get_last_game_id_by_chat_id(
            message.group_id
        )
        await asyncio.sleep(sleep)
        game_id_after_sleep = (
            await self.app.store.game.get_last_game_id_by_chat_id(
                message.group_id
            )
        )
        canceling_game = False
        game_is_avaible = False
        if game_id_after_sleep == game_id:
            game_is_avaible = True
        if game_id and game_id_after_sleep and game_is_avaible:
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
                        await self.send_game_message(message)
                    else:
                        canceling_game = True
                else:
                    canceling_game = True
            else:
                canceling_game = True
        else:
            game_is_avaible = False
        if canceling_game and is_timer_end and game_is_avaible:
            await self.cancel_game(message, game_id)
        elif game_is_avaible and canceling_game:
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

    async def send_game_message(self, message: Message):
        game_id = await self.app.store.game.is_game_was_started_in_chat(
            message.group_id
        )
        (
            round_state,
            round_id,
        ) = await self.app.store.game.get_round_state_by_game_id(game_id)
        if not await self.is_game_end(round_state, round_id):
            variants = await self.app.store.game.get_two_players_photo(
                round_state, round_id
            )
            if len(variants) == 0:
                await self.app.store.game.start_next_level(game_id)
                await self.send_game_message(message)
            elif len(variants) == 1:
                if (
                    await self.app.store.game.get_players_in_round(
                        round_state, round_id
                    )
                    > 1
                ):
                    player_id = (
                        await self.app.store.game.get_player_id_by_vk_id(
                            round_id, variants[0].vk_id
                        )
                    )
                    await self.app.store.game.increase_winner_state(player_id)
                    await self.app.store.game.start_next_level(game_id)
                    await self.send_game_message(message)
                else:
                    await self.end_game(round_state, round_id, message, game_id)
            elif len(variants) == 2:
                await self.app.store.vk_api.create_new_poll(message, variants)
                players_ids = (
                    await self.app.store.game.get_players_id_by_list_of_vk_id(
                        round_id, variants
                    )
                )
                await self.app.store.game.increase_players_is_plaid(players_ids)
                asyncio.ensure_future(
                    self.to_sum_up_round(variants, round_id, message)
                )
        else:
            await self.end_game(round_state, round_id, message, game_id)

    async def increase_player_score(self, update) -> [bool, int]:
        round_id = await self.app.store.game.get_round_by_group_id(
            group_id=update.object.group_id
        )
        if await self.is_player_can_void(update.object.user_id, round_id):
            player_id = await self.app.store.game.get_player_id_by_vk_id(
                round_id=round_id,
                vk_id=int(
                    update.object.payload["callback_data"].split(":")[1].strip()
                ),
            )
            await self.app.store.game.add_point_score_to_player_by_player_id(
                player_id=player_id,
            )
            await self.app.store.game.add_point_total_score_to_player_by_player_vk_id(
                vk_id=update.object.user_id,
            )
            return True, round_id
        else:
            return False, -1

    async def is_player_can_void(self, user_id: int, round_id: int):
        player_id = await self.app.store.game.get_player_id_by_vk_id(
            round_id, user_id
        )
        if player_id:
            if not await self.app.store.game.is_player_already_void(player_id):
                return True
        return False

    async def to_sum_up_round(
        self, variants: list[int], round_id: int, message: Message
    ):
        await asyncio.sleep(30)
        if await self.app.store.game.is_game_was_started_in_chat(
            message.group_id
        ):
            winner_id = await self.app.store.game.get_winner_round(
                variants, round_id
            )
            await self.app.store.game.increase_winner_state(winner_id)
            await self.app.store.game.reset_players_is_voited(round_id)
            await self.send_game_message(message)

    async def is_game_end(self, round_state: int, round_id: int):
        not_plaid_people_count = (
            await self.app.store.game.get_players_not_plaid_round(
                round_state, round_id
            )
        )
        next_round_people_count = (
            await self.app.store.game.get_players_in_next_round(
                round_state, round_id
            )
        )
        if not_plaid_people_count == 0 and next_round_people_count == 1:
            return True
        return False

    async def end_game(
        self, round_state: int, round_id: int, message: Message, game_id: int
    ):
        winner = await self.app.store.game.get_winner(round_state, round_id)
        await self.app.store.game.add_point_total_wins_to_player_by_player_vk_id(winner.vk_id)
        await self.app.store.game.end_game(game_id)
        await self.app.store.vk_api.end_game(message, winner)

    async def show_leaderboard(self, message: Message):
        leaders = await self.app.store.game.get_3_best_leaders()
        if leaders:
            sum_voites = await self.app.store.game.sum_voites()
            sum_wins = await self.app.store.game.sum_wins()
            message_text = f"За все время было отдано голосов: {sum_voites} и одержано побед: {sum_wins}%0aЗа все это время лучшими игроками стали:%0a"
            for i, leader in enumerate(leaders):
                message_text += f"%0a{i+1}. {leader.name} {leader.last_name}: Всего побед - {leader.total_wins}, всего получено голосов - {leader.total_score}"
        else:
            message_text = "Ни одна игра еще не была завершена"
        message.text = message_text
        await self.app.store.vk_api.edit_message_to_leaderboard(message)
