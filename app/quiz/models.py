from dataclasses import dataclass

from sqlalchemy import Text, Column, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Theme:
    id: int
    title: str


@dataclass
class Question:
    id: int
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(Integer(), primary_key=True)
    title = Column(Text(), nullable=False, unique=True)
    questions = relationship("QuestionModel", back_populates="themes", cascade="all, delete-orphan", passive_deletes=True)


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(Integer(), primary_key=True)
    title = Column(Text(), nullable=False, unique=True)
    theme_id = Column(ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    answers = relationship("AnswerModel", back_populates="questions", cascade="all, delete-orphan", passive_deletes=True)
    themes = relationship("ThemeModel", back_populates="questions")


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(Integer(), primary_key=True)
    question_id = Column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text(), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    questions = relationship("QuestionModel", back_populates="answers")