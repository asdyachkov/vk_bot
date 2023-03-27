from sqlalchemy import select, insert, update, and_, func, delete, desc
from sqlalchemy.engine import CursorResult

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameDC,
    PlayerDC,
    GameDCModel,
    PlayerDCModel,
    RoundDC,
    RoundDCModel,
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

    async def get_two_players_photo(self, score: int, round_id: int) -> list:
        query = (
            select(PlayerDCModel)
            .where(and_(PlayerDCModel.score < score, PlayerDCModel.round_id == round_id))
            .limit(2)
        )
        async with self.app.database._engine.connect() as connection:
            players_ = await connection.execute(query)
            await connection.commit()
        players = players_.fetchall()
        players_out = []
        for player in players:
            players_out.append(
                PlayerDC(
                    vk_id=player[1],
                    name=player[3],
                    last_name=player[4],
                    # photo_id=player[5],
                    photo_id="429598238_457264709",
                    round_id=player[8],
                )
            )
        return players_out

    async def delete_game(self, game_id: int) -> bool:
        query = (
            delete(GameDCModel)
            .returning(GameDCModel.id)
            .where(GameDCModel.id == game_id)
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()
        ids = id_.fetchone()
        if ids:
            return True
        else:
            return False

    async def create_round(self, round: RoundDC) -> None:
        query = (
            insert(RoundDCModel)
            .returning(RoundDCModel.id)
            .values(game_id=round.game_id)
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()

    async def add_player(self, player: PlayerDC) -> bool:
        query = (
            insert(PlayerDCModel)
            .returning(PlayerDCModel.id)
            .values(
                vk_id=player.vk_id,
                name=player.name,
                last_name=player.last_name,
                photo_id=player.photo_id,
                round_id=player.round_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()
        ids = id_.fetchone()
        if ids:
            return True
        return False

    async def delete_player(self, player: PlayerDC) -> None:
        query = (
            delete(PlayerDCModel)
            .returning(PlayerDCModel.id)
            .where(
                PlayerDCModel.vk_id == player.vk_id,
                PlayerDCModel.name == player.name,
                PlayerDCModel.last_name == player.last_name,
                PlayerDCModel.photo_id == player.photo_id,
                PlayerDCModel.round_id == player.round_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()

    async def is_user_already_in_game(self, player: PlayerDC) -> bool:
        query = select(PlayerDCModel).where(
            PlayerDCModel.vk_id == player.vk_id,
            PlayerDCModel.name == player.name,
            PlayerDCModel.last_name == player.last_name,
            PlayerDCModel.photo_id == player.photo_id,
            PlayerDCModel.round_id == player.round_id,
        )
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        players_all = players.fetchall()
        if players_all:
            return True
        return False

    async def get_players_by_round_id(self, round_id: int) -> int:
        query = select(func.count(PlayerDCModel.id)).where(
            PlayerDCModel.round_id == round_id
        )
        async with self.app.database._engine.connect() as connection:
            counts: CursorResult = await connection.execute(query)
        count = counts.fetchone()
        return int(count[0])

    async def get_round_by_group_id(self, group_id: int) -> int | None:
        query = (
            select(GameDCModel.id)
            .where(GameDCModel.chat_id == group_id)
            .order_by(desc(GameDCModel.created_at))
            .limit(1)
        )
        async with self.app.database._engine.connect() as connection:
            game_ids: CursorResult = await connection.execute(query)
        game_id_ = game_ids.fetchone()
        if game_id_:
            game_id = int(game_id_[0])
            query = (
                select(RoundDCModel.id)
                .where(RoundDCModel.game_id == game_id)
                .order_by(desc(RoundDCModel.id))
                .limit(1)
            )
            async with self.app.database._engine.connect() as connection:
                rounds: CursorResult = await connection.execute(query)
            round = rounds.fetchone()
            if round:
                return int(round[0])
        return None

    async def get_round_state_by_game_id(self, game_id: int) -> tuple | None:
        query = (
            select(RoundDCModel.state,
                   RoundDCModel.id)
            .where(RoundDCModel.game_id == game_id)
            .limit(1)
        )
        async with self.app.database._engine.connect() as connection:
            states_: CursorResult = await connection.execute(query)
        states = states_.fetchone()
        if states:
            return int(states[0]), int(states[1])
        else:
            return None

    async def get_last_game_id_by_chat_id(self, chat_id: int) -> int | None:
        query = select(GameDCModel.id).where(
            and_(
                GameDCModel.chat_id == chat_id,
                GameDCModel.is_end == False,
                GameDCModel.is_start == False,
            )
        )
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        games_all = games.fetchone()
        if games_all:
            return int(games_all[0])
        else:
            return None

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
        query = select(GameDCModel).where(
            and_(
                GameDCModel.chat_id == chat_id,
                GameDCModel.is_end == False,
                GameDCModel.is_start == False,
            )
        )
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        game = games.fetchone()
        if not game:
            return False
        else:
            return True

    async def is_game_was_started_in_chat(self, chat_id) -> bool | int:
        query = select(GameDCModel.id).where(
            and_(
                GameDCModel.chat_id == chat_id,
                GameDCModel.is_end == False,
                GameDCModel.is_start == True,
            )
        )
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        game = games.fetchone()
        if not game:
            return False
        else:
            return int(game[0])

    async def start_game(self, game_id) -> None:
        query = (
            update(GameDCModel)
            .values(is_start=True)
            .where(
                and_(
                    GameDCModel.id == game_id,
                    GameDCModel.is_end == False,
                    GameDCModel.is_start == False,
                )
            )
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
        query = (
            update(RoundDCModel)
            .values(state=RoundDCModel.state + 1)
            .where(RoundDCModel.game_id == game_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
