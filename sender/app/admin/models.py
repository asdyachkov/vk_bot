from sqlalchemy import Column, String, Integer, Text

from app.store.database.sqlalchemy_base import db
from dataclasses import dataclass
from typing import Optional


@dataclass
class Admin:
    id: int
    email: str
    vk_id: int
    salt: Optional[str] = None
    password: Optional[str] = None


class AdminModel(db):
    __tablename__ = "admins"
    id = Column(Integer(), primary_key=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(Text(), nullable=False)
    salt = Column(Text(), nullable=False)
    vk_id = Column(Integer, nullable=False, unique=True)
