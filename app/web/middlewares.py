import json
import typing

from aiohttp.web_exceptions import HTTPException, HTTPUnprocessableEntity
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request


HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status="bad_request",
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        return error_json_response(
            http_status=e.status,
            status=HTTP_ERROR_CODES[e.status],
            message=str(e),
        )
    except Exception as e:
        request.app.logger.error("Exception", exc_info=e)
        return error_json_response(
            http_status=500, status="internal server error", message=str(e)
        )


@middleware
async def auth_middleware(request: "Request", handler):
    if request.path == '/admin.login':
        response = await handler(request)
        return response
    else:
        session = await get_session(request)
        try:
            if session._mapping['is_autorized_admin']['is_autorized'] and await request.app.store.admin.is_admin_by_email(session._mapping['is_autorized_admin']['email']):
                response = await handler(request)
                return response
            else:
                return error_json_response(
                    http_status=403,
                    status=HTTP_ERROR_CODES[403],
                    message='No valid cookie',
                )
        except Exception as e:
            return error_json_response(
                http_status=401,
                status=HTTP_ERROR_CODES[401],
                message=str(e),
            )


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
