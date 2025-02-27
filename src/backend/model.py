from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.backend.database_config import Base


# User 모델 (기존 user.py에서 가져옴)
class User(Base):
    __tablename__ = "user"
    name = Column(String(50), primary_key=True, nullable=False)
    password = Column(String(50), nullable=False)

    # 관계 설정 (필요한 경우)
    questions = relationship("Question", back_populates="user")
    user_answers = relationship("UserAnswer", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


# Question 모델
class Question(Base):
    __tablename__ = "Question"

    questionid = Column(Integer, primary_key=True)
    username = Column(String(36), ForeignKey("user.name"))
    questiontext = Column(String(255), nullable=False)
    questionnum = Column(Integer)
    questiontype = Column(String(36))

    # 관계 설정
    user = relationship("User", back_populates="questions")
    user_answers = relationship("UserAnswer", back_populates="question")
    feedbacks = relationship("Feedback", back_populates="question")


# UserAnswer 모델
class UserAnswer(Base):
    __tablename__ = "UserAnswer"

    answerid = Column(Integer, primary_key=True)
    questionid = Column(Integer, ForeignKey("Question.questionid"))
    username = Column(String(36), ForeignKey("user.name"))
    answertext = Column(Text, nullable=False)

    # 관계 설정
    question = relationship("Question", back_populates="user_answers")
    user = relationship("User", back_populates="user_answers")
    feedbacks = relationship("Feedback", back_populates="user_answer")


# Feedback 모델
class Feedback(Base):
    __tablename__ = "Feedback"

    feedbackid = Column(Integer, primary_key=True)
    answerid = Column(Integer, ForeignKey("UserAnswer.answerid"))
    questionid = Column(Integer, ForeignKey("Question.questionid"))
    username = Column(String(36), ForeignKey("user.name"))
    errortext = Column(Text, nullable=True)
    errortype = Column(String(36), nullable=True)
    feedback = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)

    # 관계 설정
    user_answer = relationship("UserAnswer", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")
    question = relationship("Question", back_populates="feedbacks")