import hashlib
import os

from sqlalchemy import select, insert, CursorResult, and_, or_

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor


class AdminAccessor(BaseAccessor):
    async def create_admin(self, email: str, password: str, vk_id: int) -> Admin | None:
        salt_local = self.app.config.admin.salt.encode(encoding='UTF-8')
        salt = os.urandom(32)
        password = str(hashlib.pbkdf2_hmac('sha256', hashlib.pbkdf2_hmac('sha256', password.encode(encoding='UTF-8'), salt, 100000), salt_local, 100000))
        query = insert(AdminModel).returning(AdminModel.id).values(email=email, password=password, vk_id=vk_id, salt=str(salt))
        async with self.app.database._engine.connect() as connection:
            id_ = await connection.execute(query)
            await connection.commit()
        added_id = id_.fetchone()
        if added_id:
            return Admin(
                id=added_id[0],
                email=email,
                vk_id=vk_id
            )
        return None

    async def is_admin_exist(self, email: str, vk_id: int) -> bool:
        query = select(AdminModel).where(or_(AdminModel.vk_id == vk_id, AdminModel.email == email))
        async with self.app.database._engine.connect() as connection:
            user_: CursorResult = await connection.execute(query)
        user = user_.fetchone()
        if user:
            return True
        return False

    async def is_admin_by_vk_id(self, vk_id: int) -> bool:
        query = select(AdminModel).where(AdminModel.vk_id == vk_id)
        async with self.app.database._engine.connect() as connection:
            user_: CursorResult = await connection.execute(query)
        user = user_.fetchone()
        if user:
            return True
        return False

    async def is_admin_by_email(self, email: str) -> Admin | None:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database._engine.connect() as connection:
            user_: CursorResult = await connection.execute(query)
        user = user_.fetchone()
        if user:
            return Admin(
                id=user[0],
                email=user[1],
                vk_id=user[4]
            )
        return None

    async def get_admin_auth(self, email: str, password: str) -> Admin | None:
        query = select(AdminModel).where(and_(AdminModel.email == email, AdminModel.password == password))
        async with self.app.database._engine.connect() as connection:
            user_: CursorResult = await connection.execute(query)
        user = user_.fetchone()
        if user:
            return Admin(
                id=user[0],
                email=user[1],
                vk_id=user[4]
            )
        return None

    async def get_salt_by_email(self, email: str) -> str | None:
        query = select(AdminModel.salt).where(AdminModel.email == email)
        async with self.app.database._engine.connect() as connection:
            salt_: CursorResult = await connection.execute(query)
        salt = salt_.fetchone()
        if salt:
            return salt[0]
        return None
