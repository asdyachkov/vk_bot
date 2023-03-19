import typing
from typing import Optional

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.users.dataclassess import ChatUser

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class UserAccessor(BaseAccessor):
    def __init__(self, app: "Application"):
        super().__init__(app)
        self.session: Optional[ClientSession] = None

    async def connect(self, app: "Application"):
        self.session = app.database.session

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def get_all_users_in_chat_by_peer_id(self, peer_id: int) -> list[ChatUser] | None:
        async with self.session.get(
                self._build_query(
                    API_PATH,
                    "messages.getConversationMembers",
                    params={
                        "peer_id": peer_id,
                        "access_token": self.app.config.bot.token,
                    },
                )
        ) as resp:
            data = await resp.json()
            users = data.get("profiles", [])
            user_objects = []
            for user in users:
                user_objects.append(ChatUser(user['id'], user['first_name'], user['last_name'], user['deactivated'], user['is_closed']))
            if len(user_objects) > 0:
                return user_objects
            return None
