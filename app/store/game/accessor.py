from sqlalchemy import select, insert, update, and_, func, delete, desc
from sqlalchemy.engine import CursorResult

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameDC,
    PlayerDC,
    GameDCModel,
    PlayerDCModel,
    RoundDC,
    RoundDCModel, LeaderDCModel, LeaderDC,
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

    async def get_two_players_photo(
        self, round_state: int, round_id: int, for_update=False
    ) -> list[PlayerDC]:
        if for_update == False:
            is_plaid = (False,)
        else:
            is_plaid = (False, True)
        query = (
            select(PlayerDCModel)
            .where(
                and_(
                    PlayerDCModel.state - round_state == -1,
                    PlayerDCModel.round_id == round_id,
                    PlayerDCModel.is_plaid.in_(is_plaid),
                )
            )
            .order_by(
                PlayerDCModel.vk_id
            )
            .limit(2)
        )
        async with self.app.database._engine.connect() as connection:
            players_ = await connection.execute(query)
            await connection.commit()
        players = players_.fetchall()
        players_out = []
        for player in players:
            if not player[5]:
                player[5] = "7542_456246318"
            players_out.append(
                PlayerDC(
                    vk_id=player[1],
                    name=player[3],
                    last_name=player[4],
                    photo_id=player[5],
                    score=player[6],
                    round_id=player[8],
                )
            )
        return players_out

    async def get_winner(self, score: int, round_id: int) -> PlayerDC:
        query = select(PlayerDCModel).where(
            and_(
                PlayerDCModel.score - score == -1,
                PlayerDCModel.round_id == round_id,
                PlayerDCModel.is_plaid == False,
            )
        )
        async with self.app.database._engine.connect() as connection:
            players_ = await connection.execute(query)
            await connection.commit()
        player = players_.fetchone()
        if not player[5]:
            player[5] = "7542_456246318"
        return PlayerDC(
            vk_id=player[1],
            name=player[3],
            last_name=player[4],
            photo_id=player[5],
            round_id=player[8],
        )

    async def get_3_best_leaders(self) -> list[LeaderDC]:
        query = select(LeaderDCModel).order_by(desc(LeaderDCModel.total_wins)).order_by(desc(LeaderDCModel.total_score)).limit(3)
        async with self.app.database._engine.connect() as connection:
            leaders_ = await connection.execute(query)
            await connection.commit()
        leaders = leaders_.fetchall()
        leaders_out = []
        for leader in leaders:
            if not leader[5]:
                leader[5] = "7542_456246318"
            leaders_out.append(
                LeaderDC(
                    vk_id=leader[1],
                    name=leader[3],
                    last_name=leader[4],
                    photo_id=leader[5],
                    total_score=leader[6],
                    total_wins=leader[7],
                )
            )
        return leaders_out

    async def get_players_not_plaid_round(
        self, score: int, round_id: int
    ) -> int:
        query = select(func.count(PlayerDCModel.id)).where(
            and_(
                PlayerDCModel.score - score == -2,
                PlayerDCModel.round_id == round_id,
                PlayerDCModel.is_plaid == False,
            )
        )
        async with self.app.database._engine.connect() as connection:
            counts: CursorResult = await connection.execute(query)
        count = counts.fetchone()
        if count:
            return int(count[0])
        else:
            return 0

    async def get_players_in_round(self, score: int, round_id: int) -> int:
        query = select(func.count(PlayerDCModel.id)).where(
            and_(
                PlayerDCModel.score - score == 0,
                PlayerDCModel.round_id == round_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            counts: CursorResult = await connection.execute(query)
        count = counts.fetchone()
        return int(count[0])

    async def get_players_in_next_round(self, score: int, round_id: int) -> int:
        query = select(func.count(PlayerDCModel.id)).where(
            and_(
                PlayerDCModel.score - score == -1,
                PlayerDCModel.round_id == round_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            counts: CursorResult = await connection.execute(query)
        count = counts.fetchone()
        return int(count[0])

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

    async def add_player(self, player: PlayerDC, is_player_added_to_leaderboard: bool) -> bool:
        if not is_player_added_to_leaderboard:
            query = (
                insert(LeaderDCModel)
                .values(
                    vk_id=player.vk_id,
                    name=player.name,
                    last_name=player.last_name,
                    photo_id=player.photo_id,
                )
            )
            async with self.app.database._engine.connect() as connection:
                await connection.execute(query)
                await connection.commit()
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
            await connection.execute(query)
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

    async def get_player_id_by_vk_id(self, round_id: int, vk_id: int) -> int:
        query = (
            select(PlayerDCModel.id)
            .where(
                and_(
                    PlayerDCModel.round_id == round_id,
                    PlayerDCModel.vk_id == vk_id,
                )
            )
            .limit(1)
        )
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        player_ids = players.fetchone()
        return int(player_ids[0])

    async def is_player_added_to_leaderboard(self, vk_id: int) -> bool:
        query = (
            select(LeaderDCModel.id)
            .where(
                LeaderDCModel.vk_id == vk_id,
            )
        )
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        player_ids = players.fetchone()
        if player_ids:
            return True
        return False

    async def get_players_id_by_list_of_vk_id(
        self, round_id: int, variants: list[PlayerDC]
    ) -> list[int]:
        query = select(PlayerDCModel.id).where(
            and_(
                PlayerDCModel.round_id == round_id,
                PlayerDCModel.vk_id.in_((variants[0].vk_id, variants[1].vk_id)),
            )
        )
        async with self.app.database._engine.connect() as connection:
            players: CursorResult = await connection.execute(query)
        player_ids = players.fetchall()
        players_out = []
        for player in player_ids:
            players_out.append(int(player[0]))
        return players_out

    async def get_round_by_group_id(self, group_id: int) -> int | None:
        query = (
            select(GameDCModel.id)
            .where(GameDCModel.chat_id == group_id)
            .order_by(desc(GameDCModel.id))
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
            select(RoundDCModel.state, RoundDCModel.id)
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

    async def sum_voites(self) -> int:
        query = select(func.sum(LeaderDCModel.total_score))
        async with self.app.database._engine.connect() as connection:
            voites: CursorResult = await connection.execute(query)
        voite = voites.fetchone()
        if voite:
            return int(voite[0])
        else:
            return 0

    async def sum_wins(self) -> int:
        query = select(func.sum(LeaderDCModel.total_wins))
        async with self.app.database._engine.connect() as connection:
            wins: CursorResult = await connection.execute(query)
        win = wins.fetchone()
        if win:
            return int(win[0])
        else:
            return 0

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

    async def start_next_level(self, game_id) -> None:
        query = (
            update(RoundDCModel)
            .values(state=RoundDCModel.state + 1)
            .where(RoundDCModel.game_id == game_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def end_game(self, game_id) -> None:
        query = (
            update(GameDCModel)
            .values(is_end=True)
            .where(GameDCModel.id == game_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def add_point_score_to_player_by_player_id(
        self, player_id: int
    ) -> None:
        query = (
            update(PlayerDCModel)
            .values(score=PlayerDCModel.score + 1)
            .where(PlayerDCModel.id == player_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def add_point_total_score_to_player_by_player_vk_id(
        self, vk_id: int
    ) -> None:
        query = (
            update(LeaderDCModel)
            .values(total_score=LeaderDCModel.total_score + 1)
            .where(LeaderDCModel.vk_id == vk_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def add_point_total_wins_to_player_by_player_vk_id(
        self, vk_id: int
    ) -> None:
        query = (
            update(LeaderDCModel)
            .values(total_wins=LeaderDCModel.total_wins + 1)
            .where(LeaderDCModel.vk_id == vk_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def increase_players_is_plaid(self, variants: list[int]) -> None:
        query = (
            update(PlayerDCModel)
            .values(is_plaid=True)
            .where(PlayerDCModel.id.in_(tuple(variants)))
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def make_user_already_voited(
        self, round_id: int, user_id: int
    ) -> None:
        query = (
            update(PlayerDCModel)
            .values(is_voited=True)
            .where(
                and_(
                    PlayerDCModel.round_id == round_id,
                    PlayerDCModel.vk_id == user_id,
                )
            )
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def is_player_already_void(self, player_id: int) -> bool:
        query = select(PlayerDCModel.is_voited).where(
            PlayerDCModel.id == player_id
        )
        async with self.app.database._engine.connect() as connection:
            games: CursorResult = await connection.execute(query)
        game = games.fetchone()
        return bool(game[0])

    async def get_winner_round(self, variants: list[int], round_id: int) -> int:
        query = (
            select(PlayerDCModel.id)
            .where(
                and_(
                    PlayerDCModel.round_id == round_id,
                    PlayerDCModel.vk_id.in_(
                        (variants[0].vk_id, variants[1].vk_id)
                    ),
                    PlayerDCModel.is_plaid == True,
                )
            )
            .order_by(desc(PlayerDCModel.score))
            .limit(1)
        )
        async with self.app.database._engine.connect() as connection:
            ids_: CursorResult = await connection.execute(query)
        id = ids_.fetchone()
        return int(id[0])

    async def increase_winner_state(self, player_id: int) -> None:
        query = (
            update(PlayerDCModel)
            .values(
                state=PlayerDCModel.state + 1,
                score=0,
                is_plaid=False,
                is_voited=False,
            )
            .where(PlayerDCModel.id == player_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def reset_players_is_voited(self, round_id: int) -> None:
        query = (
            update(PlayerDCModel)
            .values(is_voited=False)
            .where(PlayerDCModel.round_id == round_id)
        )
        async with self.app.database._engine.connect() as connection:
            await connection.execute(query)
            await connection.commit()
