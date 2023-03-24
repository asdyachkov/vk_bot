from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Text, Column, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from app.store.database.sqlalchemy_base import db


@dataclass
class GameDC:
    chat_id: int
    is_start: bool
    is_end: bool
    round_id: int
    created_at: Optional[DateTime] = datetime.now()


@dataclass
class PlayerDC:
    vk_id: int
    is_admin: bool
    name: str
    last_name: str
    photo_id: str
    state: int
    round_id: int
    score: int = 0


@dataclass
class RoundDC:
    state: int
    players: list["PlayerDC"]
    game_id: int


class GameDCModel(db):
    __tablename__ = "games"
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer(), nullable=False)
    is_start = Column(Boolean(), default=False, nullable=False)
    is_end = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(), nullable=False)
    rounds = relationship("RoundDCModel", backref=backref("games", uselist=False, cascade="all, delete-orphan"))


class RoundDCModel(db):
    __tablename__ = "rounds"
    id = Column(Integer(), primary_key=True)
    state = Column(Integer(), nullable=False, default=0)
    game_id = Column(Integer(), ForeignKey("games.id"))
    players = relationship("PlayerDCModel", backref=backref("rounds", uselist=True, cascade="all, delete-orphan"))


class PlayerDCModel(db):
    __tablename__ = "players"
    id = Column(Integer(), primary_key=True)
    vk_id = Column(Integer(), nullable=False)
    is_admin = Column(Boolean(), default=False, nullable=False)
    name = Column(Text(), nullable=False)
    last_name = Column(Text(), nullable=False)
    photo_id = Column(Text(), nullable=False)
    score = Column(Integer(), nullable=False, default=0)
    state = Column(Integer(), nullable=False, default=0)
    round_id = Column(Integer(), ForeignKey("rounds.id"))



