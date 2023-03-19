from sqlalchemy import select, insert, and_, desc
from sqlalchemy.engine import CursorResult

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameDC, PlayerDC, GameScoreDC, GameDCModel, PlayerDCModel, GameScoreDCModel
)


class GameAccessor(BaseAccessor):
    async def get_all_users_by_chat_id(self, chat_id: int) -> list[PlayerDC] | None:
        query = select(GameDCModel.c.players).where(GameDCModel.c.chat_id == chat_id)
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        players_all = players.fetchall()
        if len(players_all) != 0:
            players_out = []
            for player in players_all:
                players_out.append(PlayerDC(player['vk_id'], player['name'], player['last_name'], player['score']))
            return players_out
        return None

    async def create_game(self, game: GameDC, player: PlayerDC, score: GameScoreDC) -> None:
        query = insert(GameScoreDCModel).values(score=score)
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
        query = insert(GameScoreDCModel).values(created_at=game.created_at, chat_id=game.chat_id, players=[])
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
        query = select(GameDCModel).where(and_(GameDCModel.c.chat_id == game.chat_id), GameDCModel.c.players == [])
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        created_game = games.fetchone()
        game_id = created_game['id']
        query = insert(PlayerDCModel).values(vk_id=player.vk_id, name=player.name, last_name=player.last_name, game_id=game_id, score=score.points)
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
        return None

    async def get_lat_game_by_chat_id(self, chat_id: int) -> tuple[GameDC, list[PlayerDC]] | None:
        query = select(GameDCModel).where(GameDCModel.c.chat_id == chat_id).order_by(desc(GameDCModel.c.created_at)).limit(1)
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        games_all = games.fetchone()
        if len(games_all) != 1:
            return None
        else:
            game = games_all[0]
            out_players = []
            query = select(PlayerDCModel).where(PlayerDCModel.c.game_id == game.id)
            async with self.app.database._engine.connect() as connection:
                players: CursorResult = await connection.execute(query)
            players_all = players.fetchall()
            for player in players_all:
                out_players.append(PlayerDC(player['vk_id'], player['name'], player['last_name'], player['score']))
            out_game = GameDC(games_all['id'], games_all['created_at'], games_all['chat_id'], out_players)
            return out_game, out_players
