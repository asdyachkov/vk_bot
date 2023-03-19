from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Text, Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class GameDC:
    id: int
    created_at: datetime
    chat_id: int
    players: list["PlayerDC"]


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
    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime(), nullable=False)
    chat_id = Column(Integer(), nullable=False)
    players = relationship("PlayerDCModel", back_populates="games")


class PlayerDCModel(db):
    __tablename__ = "players"
    vk_id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)
    last_name = Column(Text(), nullable=False)
    game_id = Column(ForeignKey("games.id"))
    games = relationship("GameDCModel", back_populates="players")
    score = Column(ForeignKey("scores.points"))
    scores = relationship("GameScoreDCModel", back_populates="players", cascade="all, delete-orphan", passive_deletes=True)


class GameScoreDCModel(db):
    __tablename__ = "scores"
    id = Column(Integer(), primary_key=True)
    points = Column(Integer(), unique=True)
    players = relationship("PlayerDCModel", back_populates="scores")
