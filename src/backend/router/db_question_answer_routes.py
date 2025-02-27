from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from src.backend.database_config import get_db
from src.backend.model import Question, UserAnswer

# API 라우터 초기화
router = APIRouter()


# 응답 스키마 정의
class QuestionResponse(BaseModel):
    question: Dict


class AnswerResponse(BaseModel):
    answer: Dict


class QuestionAnswerAllResponse(BaseModel):
    question: Dict
    answer: Dict


# 1. 특정 질문 조회 API
@router.get("/questions/{questionid}/original", response_model=QuestionResponse)
def get_question(questionid: int, db: Session = Depends(get_db)):
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 응답 생성
    return QuestionResponse(
        question={
            "questionid": question.questionid,
            "questiontext": question.questiontext,
            "questionnum": question.questionnum,
            "questiontype": question.questiontype
        }
    )


# 2. 특정 답변 조회 API
@router.get("/answers/{answerid}/original", response_model=AnswerResponse)
def get_answer(answerid: int, db: Session = Depends(get_db)):
    # 데이터베이스에서 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.answerid == answerid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="답변을 찾을 수 없습니다")

    # 응답 생성
    return AnswerResponse(
        answer={
            "answerid": answer.answerid,
            "answerText": answer.answertext
        }
    )


# 3. 특정 질문과 해당 질문의 답변 함께 조회 API
@router.get("/questions/{questionid}/original/all", response_model=QuestionAnswerAllResponse)
def get_question_with_answer(questionid: int, db: Session = Depends(get_db)):
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 해당 질문에 대한 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.questionid == questionid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="해당 질문에 대한 답변을 찾을 수 없습니다")

    # 응답 생성
    return QuestionAnswerAllResponse(
        question={
            "questionId": question.questionid,
            "questionText": question.questiontext,
            "questionNum": question.questionnum,
            "questiontype": question.questiontype
        },
        answer={
            "answerId": answer.answerid,
            "answerText": answer.answertext
        }
    )