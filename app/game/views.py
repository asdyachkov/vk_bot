from app.game.models import GameDC, PlayerDC
from app.web.app import View
from app.web.utils import json_response, game_to_json, players_to_json


class AddGameView(View):
    async def post(self):
        data = await self.request.json()
        players = []
        for player in data["game"]["players"]:
            players.append(PlayerDC(vk_id=player["vk_id"], name=player["name"], last_name=player["last_name"], score=player["score"]))
        game = GameDC(chat_id=data["game"]["chat_id"], players=players)
        await self.store.game.create_game(game=game)
        return json_response(data={"status": "ok"})


class GetGameByChatIdView(View):
    async def get(self):
        data = await self.request.json()
        chat_id = data['chat_id']
        out_game = await self.store.game.get_last_game_by_chat_id(chat_id)
        if out_game:
            return json_response(data={"game": game_to_json(out_game)})
        else:
            return json_response(data={"error": "No game found"})


class GetUsersByChatIdView(View):
    async def get(self):
        data = await self.request.json()
        chat_id = data['chat_id']
        out_users = await self.store.game.get_all_users_by_chat_id(chat_id)
        if out_users:
            return json_response(data={"users": players_to_json(out_users)})
        else:
            return json_response(data={"error": "No users found"})

