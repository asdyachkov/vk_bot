from app.web.app import View
from app.web.utils import json_response, users_to_json


class GetUsersByPeerId(View):
    async def get(self):
        data = await self.request.json()
        peer_id = data["peer_id"]
        chat_users = await self.store.vk_api.get_all_users_in_chat_by_peer_id(peer_id=peer_id)
        if chat_users:
            return json_response(data={"users": users_to_json(chat_users)})
        return json_response(data={"users": "No users found"})
