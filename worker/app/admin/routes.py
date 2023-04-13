import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.admin.views import AdminAddView, AdminLoginView

    app.router.add_view("/admin.add", AdminAddView)
    app.router.add_view("/admin.login", AdminLoginView)
