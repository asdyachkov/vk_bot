import typing


if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.game.views import AddGameView, GetGameByChatIdView, GetUsersByChatIdView

    app.router.add_view("/game.add_game", AddGameView)
    app.router.add_view("/game.get_last_by_chat_id", GetGameByChatIdView)
    app.router.add_view("/game.get_users_by_chat_id", GetUsersByChatIdView)
