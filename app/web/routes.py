from aiohttp.web_app import Application


def setup_routes(app: Application):
    from app.game.routes import setup_routes as game_setup_routes
    from app.users.routes import setup_routes as user_setup_routes
    from app.admin.routes import setup_routes as admin_setup_routes

    game_setup_routes(app)
    user_setup_routes(app)
    admin_setup_routes(app)
