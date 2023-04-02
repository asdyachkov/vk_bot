import json
from typing import Any, Optional

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.game.models import GameDC, PlayerDC
from app.store.vk_api.dataclasses import (
    Update,
    UpdateEvent,
    UpdateObject,
    UpdateEventObject,
    Message,
)


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


def players_to_json(players: list[PlayerDC]) -> list[dict]:
    json_users = []
    for player in players:
        dict_to_append = {}
        dict_to_append["vk_id"] = player.vk_id
        dict_to_append["is_admin"] = player.is_admin
        dict_to_append["name"] = player.name
        dict_to_append["last_name"] = player.last_name
        dict_to_append["photo_id"] = player.photo_id
        dict_to_append["score"] = player.score
        dict_to_append["state"] = player.state
        dict_to_append["round_id"] = player.round_id
        json_users.append(dict_to_append)
    return json_users


def update_to_json(update: Update):
    return {
        "type": update.type,
        "object": {
            "id": update.object.id,
            "user_id": update.object.user_id,
            "body": update.object.body,
            "peer_id": update.object.peer_id,
        },
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
        },
    }


def json_to_update(data):
    if data["type"] == "message_new":
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
                group_id=data["object"]["group_id"],
                conversation_message_id=data["object"][
                    "conversation_message_id"
                ],
            ),
        )


def message_to_json(
    message: Message,
    function: str,
    winner: PlayerDC = 0,
    text: str = "",
    players: int = 0,
    game_id: int = 0,
    round_id: int = 0,
    variants: list[dict] = 0,
    variants_int: list[int] = 0,
):
    out = {
        "function": function,
        "message": {
            "user_id": message.user_id,
            "text": message.text,
            "peer_id": message.peer_id,
            "event_id": message.event_id,
            "group_id": message.group_id,
            "conversation_message_id": message.conversation_message_id,
        },
        "text": text,
        "players": players,
        "game_id": game_id,
        "round_id": round_id,
    }
    if winner != 0:
        out["winner"] = player_to_json(winner)
    if variants_int != 0:
        out["variants_int"] = variants_int
    if variants != 0:
        out["variants"] = [player for player in variants]
    return out


def player_to_json(player: PlayerDC):
    return {
        "vk_id": player.vk_id,
        "is_admin": player.is_admin,
        "name": player.name,
        "last_name": player.last_name,
        "photo_id": player.photo_id,
        "round_id": player.round_id,
    }


def json_to_message(update):
    return Message(
        user_id=update["message"]["user_id"],
        text=update["message"]["text"],
        peer_id=update["message"]["peer_id"],
        event_id=update["message"]["event_id"],
        group_id=update["message"]["group_id"],
        conversation_message_id=update["message"]["conversation_message_id"],
    )
