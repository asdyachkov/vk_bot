from sqlalchemy import select, insert, update
from sqlalchemy.engine import CursorResult

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameDC,
    PlayerDC,
    GameDCModel,
    PlayerDCModel,
    GameScoreDCModel,
)


class GameAccessor(BaseAccessor):
    async def get_all_users_by_chat_id(
        self, chat_id: int
    ) -> list[PlayerDC] | None:
        query = select(PlayerDCModel).where(PlayerDCModel.game_id == chat_id)
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        players_all = players.fetchall()
        if players_all:
            players_out = []
            for player in players_all:
                players_out.append(
                    PlayerDC(player[0], player[1], player[2], player[4])
                )
            return players_out
        return None

    async def create_game(self, game: GameDC) -> None:
        if not await self.is_chat_id_exists(game.chat_id):
            query = (
                insert(GameDCModel)
                .returning(GameDCModel.chat_id)
                .values(created_at=game.created_at, chat_id=game.chat_id)
            )
        else:
            query = (
                update(GameDCModel)
                .returning(GameDCModel.chat_id)
                .values(created_at=game.created_at)
                .where(GameDCModel.chat_id == game.chat_id)
            )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()
        game_id = id_.fetchone()[0]
        for player in game.players:
            score_id = await self.get_all_scores(player.score)
            if not score_id:
                query = (
                    insert(GameScoreDCModel)
                    .returning(GameScoreDCModel.id)
                    .values(points=player.score)
                )
                async with self.app.database._engine.connect() as connection:
                    id_ = await connection.execute(query)
                    await connection.commit()
                score_id = id_.fetchone()[0]
            if not await self.is_player_exists(player.vk_id):
                query = insert(PlayerDCModel).values(
                    vk_id=player.vk_id,
                    name=player.name,
                    last_name=player.last_name,
                    game_id=game_id,
                    score_id=score_id,
                )
            else:
                query = (
                    update(PlayerDCModel)
                    .values(
                        name=player.name,
                        last_name=player.last_name,
                        game_id=game_id,
                        score_id=score_id,
                    )
                    .where(PlayerDCModel.vk_id == player.vk_id)
                )
            async with self.app.database._engine.connect() as connection:
                await connection.execute(query)
                await connection.commit()
        return None

    async def get_last_game_by_chat_id(self, chat_id: int) -> GameDC | None:
        query = select(GameDCModel).where(GameDCModel.chat_id == chat_id)
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        games_all = games.fetchone()
        if not games_all:
            return None
        else:
            out_players = []
            query = select(PlayerDCModel).where(
                PlayerDCModel.game_id == chat_id
            )
            async with self.app.database._engine.connect() as connection:
                players: CursorResult = await connection.execute(query)
            players_all = players.fetchall()
            for player in players_all:
                out_players.append(
                    PlayerDC(player[0], player[1], player[2], player[4])
                )
            out_game = GameDC(
                created_at=games_all[0],
                chat_id=games_all[1],
                players=out_players,
            )
            return out_game

    async def get_all_scores(self, score: int) -> int | None:
        query = select(GameScoreDCModel.id).where(
            GameScoreDCModel.points == score
        )
        async with self.app.database._engine.connect() as connection:
            scores: CursorResult = await connection.execute(query)
        score = scores.fetchone()
        if not score:
            return None
        else:
            return score[0]

    async def is_player_exists(self, vk_id) -> bool:
        query = select(PlayerDCModel).where(PlayerDCModel.vk_id == vk_id)
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        player = players.fetchone()
        if not player:
            return False
        else:
            return True

    async def is_chat_id_exists(self, chat_id) -> bool:
        query = select(GameDCModel).where(GameDCModel.chat_id == chat_id)
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        game = games.fetchone()
        if not game:
            return False
        else:
            return True
