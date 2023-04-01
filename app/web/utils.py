from typing import Any, Optional

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.game.models import GameDC, PlayerDC
from app.store.vk_api.dataclasses import Update, UpdateEvent, UpdateObject, UpdateEventObject
from app.users.dataclassess import ChatUser


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        },
    )


def users_to_json(users: list[ChatUser]):
    json_users = []
    for user in users:
        json_users.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
    return json_users


def players_to_json(players: list[PlayerDC]):
    json_users = []
    for player in players:
        json_users.append(
            {
                "vk_id": player.vk_id,
                "name": player.name,
                "last_name": player.last_name,
                "score": player.score,
            }
        )
    return json_users


def game_to_json(game: GameDC):
    return {
        "chat_id": game.chat_id,
        "created_at": str(game.created_at),
        "players": players_to_json(game.players),
    }


def update_to_json(update: Update):
    return {
        "type": update.type,
        "object": {
            "id": update.object.id,
            "user_id": update.object.user_id,
            "body": update.object.body,
            "peer_id": update.object.peer_id,
        }
    }


def update_event_to_json(update: UpdateEvent):
    return {
        "type": update.type,
        "object": {
            "user_id": update.object.user_id,
            "payload": update.object.payload,
            "peer_id": update.object.peer_id,
            "event_id": update.object.event_id,
            "group_id": update.object.group_id,
            "conversation_message_id": update.object.conversation_message_id,
        }
    }


def json_to_update(data):
    if data['type'] == "message_new":
        return Update(
            type=data["type"],
            object=UpdateObject(
                id=data["object"]["id"],
                user_id=data["object"]["user_id"],
                body=data["object"]["body"],
                peer_id=data["object"]["peer_id"],
            ),
        )
    else:
        return UpdateEvent(
            type=data["type"],
            object=UpdateEventObject(
                user_id=data["object"]["user_id"],
                payload=data["object"]["payload"],
                peer_id=data["object"]["peer_id"],
                event_id=data["object"]["event_id"],
                group_id=data["group_id"],
                conversation_message_id=data["object"][
                    "conversation_message_id"
                ],
            ),
        )