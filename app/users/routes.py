import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.users.views import GetUsersByPeerId

    app.router.add_view("/users.get_peer_id", GetUsersByPeerId)
