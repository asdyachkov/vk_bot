import json
import typing
from logging import getLogger
from typing import Optional

import aioamqp
from aioamqp import channel
from aiohttp import ClientSession

from app.game.models import GameDC, RoundDC
from app.store.vk_api.dataclasses import Message
from app.web.utils import (
    json_to_update,
    message_to_json,
    players_to_json,
    json_to_message,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")
        self.channel: Optional[channel] = None
        self.channel_for_sending: Optional[channel] = None
        self.channel_for_delay_message: Optional[channel] = None
        self.session: Optional[ClientSession] = None

    async def connect(self):
        await self.app.database.connect()
        transport, protocol = await aioamqp.connect(
            host="127.0.0.1", port=5672, login="guest", password="guest"
        )
        self.channel = await protocol.channel()
        self.channel_for_delay_message = await protocol.channel()
        self.channel_for_sending = await protocol.channel()
        self.logger.info("Channel got")
        await self.channel.queue_declare(queue_name="to_worker", durable=True)
        await self.channel.queue_bind(
            exchange_name="amq.direct",
            queue_name="to_worker",
            routing_key="to_worker",
        )
        await self.channel_for_sending.queue_declare(
            queue_name="to_sender", durable=True
        )
        await self.channel_for_delay_message.queue_declare(
            queue_name="for_delay",
            durable=True,
            arguments={
                "x-message-ttl": 60000,
                "x-dead-letter-exchange": "amq.direct",
                "x-dead-letter-routing-key": "to_worker",
            },
        )
        self.logger.info("Queue declared")
        self.logger.info("Working....")

    async def handle_updates(self):
        await self.channel.basic_consume(self.callback, queue_name="to_worker")

    async def callback(self, channel, body, envelope, properties):
        data = json.loads(body)
        await self.proccessing_update(data)
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def proccessing_update(self, data):
        if "function" in data.keys():
            if data["function"] == "self.to_sum_up_round":
                message = json_to_message(data)
                await self.to_sum_up_round(
                    data["variants"], data["round_id"], message
                )
            elif data["function"] == "self.start_game":
                message = json_to_message(data)
                await self.start_game(message, data["game_id"])
        elif data["type"] == "message_new":
            update = json_to_update(data)
            if update.object.body == "/bot":
                await self.channel_for_sending.basic_publish(
                    payload=json.dumps(
                        message_to_json(
                            message=Message(
                                user_id=update.object.user_id,
                                text=update.object.body,
                                peer_id=update.object.peer_id,
                            ),
                            function="start_message",
                        )
                    ).encode(),
                    exchange_name="",
                    routing_key="to_sender",
                )
        elif data["type"] == "message_event":
            update = json_to_update(data)
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
                            await self.channel_for_sending.basic_publish(
                                payload=json.dumps(
                                    message_to_json(
                                        message=Message(
                                            user_id=update.object.user_id,
                                            text="",
                                            peer_id=update.object.peer_id,
                                            event_id=update.object.event_id,
                                        ),
                                        text="Регистрация начата ✅",
                                        function="answer_pop_up_notification",
                                    )
                                ).encode(),
                                exchange_name="",
                                routing_key="to_sender",
                            )
                            await self.channel_for_sending.basic_publish(
                                payload=json.dumps(
                                    message_to_json(
                                        message=Message(
                                            user_id=update.object.user_id,
                                            text="",
                                            peer_id=update.object.peer_id,
                                            event_id=update.object.event_id,
                                            conversation_message_id=update.object.conversation_message_id,
                                        ),
                                        function="start_recruiting_players",
                                    )
                                ).encode(),
                                exchange_name="",
                                routing_key="to_sender",
                            )
                            game_id = await self.app.store.game.create_game(
                                GameDC(chat_id=int(update.object.group_id))
                            )
                            if game_id:
                                await self.app.store.game.create_round(
                                    RoundDC(game_id=game_id)
                                )
                                await self.channel_for_delay_message.basic_publish(
                                    payload=json.dumps(
                                        message_to_json(
                                            message=Message(
                                                user_id=update.object.user_id,
                                                text="",
                                                peer_id=update.object.peer_id,
                                                event_id=update.object.event_id,
                                                group_id=update.object.group_id,
                                                conversation_message_id=update.object.conversation_message_id,
                                            ),
                                            game_id=game_id,
                                            function="self.start_game",
                                        )
                                    ).encode(),
                                    exchange_name="",
                                    routing_key="for_delay",
                                )
                        else:
                            await self.channel_for_sending.basic_publish(
                                payload=json.dumps(
                                    message_to_json(
                                        message=Message(
                                            user_id=update.object.user_id,
                                            text="",
                                            peer_id=update.object.peer_id,
                                            event_id=update.object.event_id,
                                            conversation_message_id=update.object.conversation_message_id,
                                        ),
                                        text="❌ Игра уже идет ❌",
                                        function="answer_pop_up_notification",
                                    )
                                ).encode(),
                                exchange_name="",
                                routing_key="to_sender",
                            )
                    else:
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                        conversation_message_id=update.object.conversation_message_id,
                                    ),
                                    text="❌ Набор в игру уже ведется ❌",
                                    function="answer_pop_up_notification",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                elif update.object.payload["callback_data"] == "add me":
                    canceling_add = False
                    game_id = (
                        await self.app.store.game.is_game_was_started_in_chat(
                            update.object.group_id
                        )
                    )
                    if not game_id:
                        round_id = (
                            await self.app.store.game.get_round_by_group_id(
                                update.object.group_id
                            )
                        )
                        if round_id:
                            is_admin = (
                                await self.app.store.admin.is_admin_by_vk_id(
                                    update.object.user_id
                                )
                            )
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
                                            is_player_added_to_leaderboard,
                                            is_admin,
                                        )
                                    )
                                    if is_player_added:
                                        players = await self.app.store.game.get_players_by_round_id(
                                            round_id
                                        )
                                        await self.channel_for_sending.basic_publish(
                                            payload=json.dumps(
                                                message_to_json(
                                                    message=Message(
                                                        user_id=update.object.user_id,
                                                        text="",
                                                        peer_id=update.object.peer_id,
                                                        event_id=update.object.event_id,
                                                        conversation_message_id=update.object.conversation_message_id,
                                                    ),
                                                    players=players,
                                                    function="edit_recruiting_players",
                                                )
                                            ).encode(),
                                            exchange_name="",
                                            routing_key="to_sender",
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
                            await self.channel_for_sending.basic_publish(
                                payload=json.dumps(
                                    message_to_json(
                                        message=Message(
                                            user_id=update.object.user_id,
                                            text="",
                                            peer_id=update.object.peer_id,
                                            event_id=update.object.event_id,
                                        ),
                                        text="❗ Вы уже зарегестрированы в этой игре ❗",
                                        function="answer_pop_up_notification",
                                    )
                                ).encode(),
                                exchange_name="",
                                routing_key="to_sender",
                            )
                    else:
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                    ),
                                    text="❌ Игра уже началась ❌",
                                    function="answer_pop_up_notification",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                elif update.object.payload["callback_data"] == "delete me":
                    canceling_delete = False
                    round_id = await self.app.store.game.get_round_by_group_id(
                        update.object.group_id
                    )
                    if round_id:
                        player = await self.app.store.vk_api.get_user_by_id(
                            update.object.user_id, round_id
                        )
                        if player:
                            if await self.app.store.game.is_user_already_in_game(
                                player
                            ):
                                await self.app.store.game.delete_player(player)
                                players = await self.app.store.game.get_players_by_round_id(
                                    round_id
                                )
                                await self.channel_for_sending.basic_publish(
                                    payload=json.dumps(
                                        message_to_json(
                                            message=Message(
                                                user_id=update.object.user_id,
                                                text="",
                                                peer_id=update.object.peer_id,
                                                event_id=update.object.event_id,
                                                conversation_message_id=update.object.conversation_message_id,
                                            ),
                                            players=players,
                                            function="edit_recruiting_players",
                                        )
                                    ).encode(),
                                    exchange_name="",
                                    routing_key="to_sender",
                                )
                            else:
                                canceling_delete = True
                        else:
                            canceling_delete = True
                    else:
                        canceling_delete = True
                    if canceling_delete:
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                    ),
                                    text="❗ Вы еще не зарегестрированы в этой игре ❗",
                                    function="answer_pop_up_notification",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                elif update.object.payload["callback_data"] == "delete games":
                    game_id = (
                        await self.app.store.game.get_last_game_id_by_chat_id(
                            update.object.group_id
                        )
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
                elif update.object.payload["callback_data"] == "start games":
                    game_id = (
                        await self.app.store.game.get_last_game_id_by_chat_id(
                            update.object.group_id
                        )
                    )
                    await self.channel.basic_publish(
                        payload=json.dumps(
                            message_to_json(
                                message=Message(
                                    user_id=update.object.user_id,
                                    text="",
                                    peer_id=update.object.peer_id,
                                    event_id=update.object.event_id,
                                    group_id=update.object.group_id,
                                    conversation_message_id=update.object.conversation_message_id,
                                ),
                                game_id=game_id,
                                function="self.start_game",
                            )
                        ).encode(),
                        exchange_name="",
                        routing_key="to_worker",
                    )
                elif "vk_id" in update.object.payload["callback_data"].split(
                    ":"
                ):
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
                        ) = await self.app.store.game.get_round_state_by_game_id(
                            game_id
                        )
                        variants = (
                            await self.app.store.game.get_two_players_photo(
                                round_state, round_id, for_update=True
                            )
                        )
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=message,
                                    variants=players_to_json(variants),
                                    function="create_new_poll",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=message,
                                    text="Ваш голос учтен ✅",
                                    function="answer_pop_up_notification",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                        await self.app.store.game.make_user_already_voited(
                            round_id, update.object.user_id
                        )
                    else:
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=Message(
                                        user_id=update.object.user_id,
                                        text="",
                                        peer_id=update.object.peer_id,
                                        event_id=update.object.event_id,
                                    ),
                                    text="❌ Голосовать могут только пользователи, участвующие в игре и только один раз за раунд ❌",
                                    function="answer_pop_up_notification",
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                elif (
                    update.object.payload["callback_data"]
                    == "check_leaderboard"
                ):
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

    async def start_game(self, message: Message, game_id: int = 0):
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
                        await self.channel_for_sending.basic_publish(
                            payload=json.dumps(
                                message_to_json(
                                    message=message, function="start_game"
                                )
                            ).encode(),
                            exchange_name="",
                            routing_key="to_sender",
                        )
                        await self.send_game_message(message)
                    else:
                        canceling_game = True
                else:
                    canceling_game = True
            else:
                canceling_game = True
        else:
            game_is_avaible = False
        if canceling_game and game_is_avaible:
            await self.cancel_game(message, game_id)
        elif game_is_avaible and canceling_game:
            await self.channel_for_sending.basic_publish(
                payload=json.dumps(
                    message_to_json(
                        message=message,
                        text="Недостаточно игроков, чтобы начать игру 😔",
                        function="answer_pop_up_notification",
                    )
                ).encode(),
                exchange_name="",
                routing_key="to_sender",
            )

    async def cancel_game(self, message: Message, game_id: int):
        round_id = await self.app.store.game.get_round_by_group_id(
            message.group_id
        )
        is_game_deleted = await self.app.store.game.delete_game(
            game_id, round_id
        )
        if is_game_deleted:
            await self.channel_for_sending.basic_publish(
                payload=json.dumps(
                    message_to_json(
                        message=message,
                        function="edit_recruiting_players_game_delete",
                    )
                ).encode(),
                exchange_name="",
                routing_key="to_sender",
            )
        else:
            await self.channel_for_sending.basic_publish(
                payload=json.dumps(
                    message_to_json(
                        message=message,
                        text="❌ Не удалось отменить игру ❌",
                        function="answer_pop_up_notification",
                    )
                ).encode(),
                exchange_name="",
                routing_key="to_sender",
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
                await self.channel_for_sending.basic_publish(
                    payload=json.dumps(
                        message_to_json(
                            message=message,
                            variants=players_to_json(variants),
                            function="create_new_poll",
                        )
                    ).encode(),
                    exchange_name="",
                    routing_key="to_sender",
                )
                players_ids = (
                    await self.app.store.game.get_players_id_by_list_of_vk_id(
                        round_id, variants
                    )
                )
                await self.app.store.game.increase_players_is_plaid(players_ids)
                await self.channel_for_delay_message.basic_publish(
                    payload=json.dumps(
                        message_to_json(
                            message=message,
                            round_id=round_id,
                            variants=players_to_json(variants),
                            function="self.to_sum_up_round",
                        )
                    ).encode(),
                    exchange_name="",
                    routing_key="for_delay",
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
        if not await self.app.store.game.is_player_already_void(user_id, round_id):
            return True
        return False

    async def to_sum_up_round(
        self, variants: list[dict], round_id: int, message: Message
    ):
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
        await self.app.store.game.add_point_total_wins_to_player_by_player_vk_id(
            winner.vk_id
        )
        await self.app.store.game.end_game(game_id)
        await self.channel_for_sending.basic_publish(
            payload=json.dumps(
                message_to_json(
                    message=message, winner=winner, function="end_game"
                )
            ).encode(),
            exchange_name="",
            routing_key="to_sender",
        )

    async def show_leaderboard(self, message: Message):
        leaders = await self.app.store.game.get_3_best_leaders()
        if leaders:
            sum_voites = await self.app.store.game.sum_voites()
            sum_wins = await self.app.store.game.sum_wins()
            message_text = f"👑 За все время было отдано голосов: {sum_voites} и одержано побед: {sum_wins} 👑%0aЗа все это время лучшими игроками стали:%0a"
            for i, leader in enumerate(leaders):
                message_text += f"%0a{i+1}. {leader.name} {leader.last_name}: Всего побед - {leader.total_wins}, всего получено голосов - {leader.total_score}"
        else:
            message_text = "Ни одна игра еще не была завершена"
        message.text = message_text
        await self.channel_for_sending.basic_publish(
            payload=json.dumps(
                message_to_json(
                    message=message, function="edit_message_to_leaderboard"
                )
            ).encode(),
            exchange_name="",
            routing_key="to_sender",
        )
