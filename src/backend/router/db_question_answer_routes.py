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


# 1. 특정 일반질문 조회 API
@router.get("/questions/{questionid}/original", response_model=QuestionResponse)
def get_original_question(questionid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 일반질문 정보를 조회하는 API

    Args:
        questionid (int): 조회할 질문 ID
        db (Session): 데이터베이스 세션

    Returns:
        QuestionResponse: 질문 정보
    """
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 일반질문인지 확인
    if question.questiontype != "일반질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 일반질문이 아닙니다")

    # 질문 응답 생성
    question_data = {
        "questionid": question.questionid,
        "questiontext": question.questiontext,
        "questionnum": question.questionnum,
        "questiontype": question.questiontype
    }

    return QuestionResponse(question=question_data)


# 2. 특정 꼬리질문 조회 API
@router.get("/questions/{questionid}/follow-up", response_model=QuestionResponse)
def get_followup_question(questionid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 꼬리질문 정보를 조회하는 API

    Args:
        questionid (int): 조회할 질문 ID
        db (Session): 데이터베이스 세션

    Returns:
        QuestionResponse: 질문 정보
    """
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 꼬리질문인지 확인
    if question.questiontype != "꼬리질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 꼬리질문이 아닙니다")

    # 질문 응답 생성
    question_data = {
        "questionid": question.questionid,
        "questiontext": question.questiontext,
        "questionnum": question.questionnum,
        "questiontype": question.questiontype
    }

    return QuestionResponse(question=question_data)


# 3. 특정 일반질문과 답변 함께 조회 API
@router.get("/questions/{questionid}/original/all", response_model=QuestionAnswerAllResponse)
def get_original_question_with_answer(questionid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 일반질문과 그에 대한 답변을 함께 조회하는 API

    Args:
        questionid (int): 조회할 질문 ID
        db (Session): 데이터베이스 세션

    Returns:
        QuestionAnswerAllResponse: 질문과 답변 정보
    """
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 일반질문인지 확인
    if question.questiontype != "일반질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 일반질문이 아닙니다")

    # 해당 질문에 대한 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.questionid == questionid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="해당 질문에 대한 답변을 찾을 수 없습니다")

    # 응답 데이터 생성
    question_data = {
        "questionId": question.questionid,
        "questionText": question.questiontext,
        "questionNum": question.questionnum,
        "questiontype": question.questiontype
    }

    answer_data = {
        "answerId": answer.answerid,
        "answerText": answer.answertext
    }

    return QuestionAnswerAllResponse(
        question=question_data,
        answer=answer_data
    )


# 4. 특정 꼬리질문과 답변 함께 조회 API
@router.get("/questions/{questionid}/follow-up/all", response_model=QuestionAnswerAllResponse)
def get_followup_question_with_answer(questionid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 꼬리질문과 그에 대한 답변을 함께 조회하는 API

    Args:
        questionid (int): 조회할 질문 ID
        db (Session): 데이터베이스 세션

    Returns:
        QuestionAnswerAllResponse: 질문과 답변 정보
    """
    # 데이터베이스에서 질문 조회
    question = db.query(Question).filter(Question.questionid == questionid).first()

    # 질문이 존재하지 않으면 404 오류
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다")

    # 꼬리질문인지 확인
    if question.questiontype != "꼬리질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 꼬리질문이 아닙니다")

    # 해당 질문에 대한 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.questionid == questionid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="해당 질문에 대한 답변을 찾을 수 없습니다")

    # 응답 데이터 생성
    question_data = {
        "questionId": question.questionid,
        "questionText": question.questiontext,
        "questionNum": question.questionnum,
        "questiontype": question.questiontype
    }

    answer_data = {
        "answerId": answer.answerid,
        "answerText": answer.answertext
    }

    return QuestionAnswerAllResponse(
        question=question_data,
        answer=answer_data
    )


# 5. 특정 일반질문의 답변 조회 API
@router.get("/answers/{answerid}/original", response_model=AnswerResponse)
def get_original_answer(answerid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 일반질문에 대한 답변 정보를 조회하는 API

    Args:
        answerid (int): 조회할 답변 ID
        db (Session): 데이터베이스 세션

    Returns:
        AnswerResponse: 답변 정보
    """
    # 데이터베이스에서 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.answerid == answerid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="답변을 찾을 수 없습니다")

    # 연관된 질문 조회하여 일반질문인지 확인
    question = db.query(Question).filter(Question.questionid == answer.questionid).first()
    if not question or question.questiontype != "일반질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 일반질문에 대한 답변이 아닙니다")

    # 답변 데이터 생성
    answer_data = {
        "answerid": answer.answerid,
        "answerText": answer.answertext
    }

    return AnswerResponse(answer=answer_data)


# 6. 특정 꼬리질문의 답변 조회 API
@router.get("/answers/{answerid}/follow-up", response_model=AnswerResponse)
def get_followup_answer(answerid: int, db: Session = Depends(get_db)):
    """
    특정 ID의 꼬리질문에 대한 답변 정보를 조회하는 API

    Args:
        answerid (int): 조회할 답변 ID
        db (Session): 데이터베이스 세션

    Returns:
        AnswerResponse: 답변 정보
    """
    # 데이터베이스에서 답변 조회
    answer = db.query(UserAnswer).filter(UserAnswer.answerid == answerid).first()

    # 답변이 존재하지 않으면 404 오류
    if not answer:
        raise HTTPException(status_code=404, detail="답변을 찾을 수 없습니다")

    # 연관된 질문 조회하여 꼬리질문인지 확인
    question = db.query(Question).filter(Question.questionid == answer.questionid).first()
    if not question or question.questiontype != "꼬리질문":
        raise HTTPException(status_code=400, detail="요청한 ID는 꼬리질문에 대한 답변이 아닙니다")

    # 답변 데이터 생성
    answer_data = {
        "answerid": answer.answerid,
        "answerText": answer.answertext
    }

    return AnswerResponse(answer=answer_data)