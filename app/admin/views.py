import hashlib

from aiohttp_apispec import request_schema
from aiohttp_session import new_session, get_session

from app.admin.schemes import AdminSchema, AdminLoginSchema
from app.web.app import View
from app.web.middlewares import HTTP_ERROR_CODES
from app.web.utils import json_response, error_json_response


class AdminAddView(View):
    @request_schema(AdminSchema)
    async def post(self):
        is_admin_exist = await self.request.app.store.admin.is_admin_exist(self.data['email'], self.data['vk_id'])
        if not is_admin_exist:
            admin = await self.request.app.store.admin.create_admin(self.data['email'], self.data['password'], self.data['vk_id'])
            if admin:
                if not await get_session(self.request):
                    session = await new_session(request=self.request)
                else:
                    session = await get_session(self.request)
                session['is_autorized_admin'] = {'id': admin.id, 'email': admin.email, 'vk_id': admin.vk_id, 'is_autorized': True}
                return json_response(data={'id': admin.id, 'email': admin.email})
            else:
                return error_json_response(message="The user is not found", http_status=403, status=HTTP_ERROR_CODES[403])
        else:
            return error_json_response(message="User already exist", http_status=403, status=HTTP_ERROR_CODES[403])


class AdminLoginView(View):
    @request_schema(AdminLoginSchema)
    async def post(self):
        salt = await self.request.app.store.admin.get_salt_by_email(self.data['email'])
        if salt:
            salt = salt.encode(encoding='UTF-8').decode('unicode_escape').encode("raw_unicode_escape")[2:-1]
            salt_local = self.request.app.config.admin.salt.encode(encoding='UTF-8')
            password = str(hashlib.pbkdf2_hmac('sha256',hashlib.pbkdf2_hmac('sha256', self.data['password'].encode(encoding='UTF-8'), salt,100000), salt_local, 100000))
            admin = await self.request.app.store.admin.get_admin_auth(self.data['email'], str(password))
            if admin:
                if not await get_session(self.request):
                    session = await new_session(request=self.request)
                else:
                    session = await get_session(self.request)
                session['is_autorized_admin'] = {'id': admin.id, 'email': admin.email, 'vk_id': admin.vk_id, 'is_autorized': True}
                return json_response(data={'id': admin.id, 'email': admin.email})
            else:
                return error_json_response(message="The user is not found", http_status=403, status=HTTP_ERROR_CODES[403])
        else:
            return error_json_response(message="The user is not found", http_status=403, status=HTTP_ERROR_CODES[403])
