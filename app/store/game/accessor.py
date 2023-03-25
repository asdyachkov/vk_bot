from sqlalchemy import select, insert, update, and_
from sqlalchemy.engine import CursorResult

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameDC,
    PlayerDC,
    GameDCModel,
    PlayerDCModel, RoundDC, RoundDCModel,
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

    async def create_game(self, game: GameDC) -> int:
        if not await self.is_chat_id_exists(game.chat_id):
            query = (
                insert(GameDCModel)
                .returning(GameDCModel.id)
                .values(chat_id=game.chat_id)
            )
            async with self.app.database._engine.connect() as connection:
                id_ = await connection.execute(query)
                await connection.commit()
            return int(id_.fetchone()[0])

    async def create_round(self, round: RoundDC) -> None:
        query = (
            insert(RoundDCModel)
            .returning(RoundDCModel.id)
            .values(game_id=round.game_id)
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()

    async def add_player(self, player: PlayerDC) -> None:
        query = (
            insert(PlayerDCModel)
            .returning(PlayerDCModel.id)
            .values(
                vk_id=player.vk_id,
                name=player.name,
                last_name=player.last_name,
                photo_id=player.photo_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()

    async def get_round_by_group_id(self, group_id: int) -> int:
        query = select(GameDCModel.rounds).where(GameDCModel.chat_id == group_id)
        async with self.app.database._engine.connect() as connection:
            rounds: CursorResult = await connection.execute(query)
        round = rounds.fetchone()
        return int(round[0])

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
        query = select(GameDCModel).where(and_(GameDCModel.chat_id == chat_id, GameDCModel.is_end == False))
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        game = games.fetchone()
        if not game:
            return False
        else:
            return True
