from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy import Text, Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship, backref

from app.store.database.sqlalchemy_base import db


@dataclass
class GameDC:
    chat_id: int
    players: list["PlayerDC"]
    created_at: Optional[DateTime] = date.today()


@dataclass
class PlayerDC:
    vk_id: int
    name: str
    last_name: str
    score: "GameScoreDC"


@dataclass
class GameScoreDC:
    points: int


class GameDCModel(db):
    __tablename__ = "games"
    created_at = Column(DateTime(), nullable=False)
    chat_id = Column(Integer(), nullable=False, primary_key=True)
    players = relationship("PlayerDCModel", back_populates="games")


class PlayerDCModel(db):
    __tablename__ = "players"
    vk_id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)
    last_name = Column(Text(), nullable=False)
    game_id = Column(ForeignKey("games.chat_id"))
    games = relationship("GameDCModel", back_populates="players")
    score_id = Column(ForeignKey("scores.id"))
    scores = relationship("GameScoreDCModel", backref=backref("players", uselist=False, cascade='all, delete-orphan'))


class GameScoreDCModel(db):
    __tablename__ = "scores"
    id = Column(Integer(), primary_key=True)
    points = Column(Integer(), unique=True)


