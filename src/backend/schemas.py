from pydantic import BaseModel
from typing import Optional, List


# User 스키마
class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    class Config:
        orm_mode = True


# Question 스키마
class QuestionBase(BaseModel):
    questiontext: str
    questiontype: Optional[str] = None
    questionnum: Optional[int] = None


class QuestionCreate(QuestionBase):
    username: str


class Question(QuestionBase):
    questionid: int
    username: str

    class Config:
        orm_mode = True


# UserAnswer 스키마
class UserAnswerBase(BaseModel):
    answertext: str


class UserAnswerCreate(UserAnswerBase):
    questionid: int
    username: str


class UserAnswer(UserAnswerBase):
    answerid: int
    questionid: int
    username: str

    class Config:
        orm_mode = True


# Feedback 스키마
class FeedbackBase(BaseModel):
    errortext: Optional[str] = None
    errortype: Optional[str] = None
    feedback: Optional[str] = None
    suggestion: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    answerid: int
    questionid: int
    username: str


class Feedback(FeedbackBase):
    feedbackid: int
    answerid: int
    questionid: int
    username: str

    class Config:
        orm_mode = True