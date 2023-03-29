from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Text, Column, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from app.store.database.sqlalchemy_base import db


@dataclass
class GameDC:
    chat_id: int
    is_start: bool = False
    is_end: bool = False
    created_at: Optional[DateTime] = datetime.now()


@dataclass
class PlayerDC:
    vk_id: int
    name: str
    last_name: str
    photo_id: str
    round_id: int
    state: int = 0
    is_admin: bool = False
    score: int = 0


@dataclass
class LeaderDC:
    vk_id: int
    name: str
    last_name: str
    photo_id: str
    is_admin: bool = False
    total_score: int = 0
    total_wins: int = 0


@dataclass
class RoundDC:
    game_id: int
    state: int = 0
    players: list["PlayerDC"] = list


class GameDCModel(db):
    __tablename__ = "games"
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer(), nullable=False)
    is_start = Column(Boolean(), default=False, nullable=False)
    is_end = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(), nullable=False, default=datetime.now())
    rounds = relationship(
        "RoundDCModel",
        backref="games",
        uselist=False,
        cascade="all, delete-orphan",
    )


class RoundDCModel(db):
    __tablename__ = "rounds"
    id = Column(Integer(), primary_key=True)
    state = Column(Integer(), nullable=False, default=0)
    game_id = Column(Integer(), ForeignKey("games.id", ondelete="CASCADE"))
    players = relationship(
        "PlayerDCModel",
        backref="rounds",
        uselist=True,
        cascade="all, delete-orphan",
    )


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
    is_plaid = Column(Boolean(), nullable=False, default=False)
    is_voited = Column(Boolean(), nullable=False, default=False)
    round_id = Column(Integer(), ForeignKey("rounds.id", ondelete="CASCADE"))


class LeaderDCModel(db):
    __tablename__ = "leaders"
    id = Column(Integer(), primary_key=True)
    vk_id = Column(Integer(), nullable=False)
    is_admin = Column(Boolean(), default=False, nullable=False)
    name = Column(Text(), nullable=False)
    last_name = Column(Text(), nullable=False)
    photo_id = Column(Text(), nullable=False)
    total_score = Column(Integer(), nullable=False, default=0)
    total_wins = Column(Integer(), nullable=False, default=0)
