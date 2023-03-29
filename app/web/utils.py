from typing import Any, Optional

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.game.models import GameDC, PlayerDC
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
