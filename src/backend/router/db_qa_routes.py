from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from src.backend.database_config import get_db
from src.backend.model import Question, UserAnswer, User

# API 라우터 초기화
router = APIRouter()


# 질문 데이터 모델
class QuestionData(BaseModel):
    questiontext: str
    questiontype: str


# 답변 데이터 모델
class AnswerData(BaseModel):
    answertext: str


# 질문-답변 요청 데이터 모델
class QuestionAnswerRequest(BaseModel):
    question: QuestionData
    answer: AnswerData
    username: str  # 사용자 이름 필드 추가


# 질문-답변 응답 데이터 모델
class QuestionAnswerResponse(BaseModel):
    questionid: int
    answerid: int
    success: bool
    message: str


@router.post("/answers", response_model=QuestionAnswerResponse)
def save_question_answer(request: QuestionAnswerRequest, db: Session = Depends(get_db)):
    """
    질문과 답변을 함께 저장하는 API

    Args:
        request (QuestionAnswerRequest): 질문과 답변 데이터 및 사용자 정보
        db (Session): 데이터베이스 세션

    Returns:
        QuestionAnswerResponse: 저장 결과 및 생성된 ID 정보

    Raises:
        HTTPException: 데이터 저장 중 오류 발생 시 500 오류
    """
    try:
        # 1. 사용자 확인
        user = db.query(User).filter(User.name == request.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다")

        # 2. 질문 데이터 저장
        new_question = Question(
            username=request.username,  # 요청에서 받은 username 사용
            questiontext=request.question.questiontext,
            questiontype=request.question.questiontype,
            questionnum=1  # 기본값 설정 또는 적절한 로직으로 결정
        )
        db.add(new_question)
        db.flush()  # ID 생성을 위해 flush (commit은 아직)

        # 3. 답변 데이터 저장
        new_answer = UserAnswer(
            questionid=new_question.questionid,  # 위에서 생성된 질문 ID 참조
            username=request.username,  # 요청에서 받은 username 사용
            answertext=request.answer.answertext
        )
        db.add(new_answer)

        # 4. 모든 변경사항 커밋
        db.commit()
        db.refresh(new_question)
        db.refresh(new_answer)

        # 5. 응답 생성
        return QuestionAnswerResponse(
            questionid=new_question.questionid,
            answerid=new_answer.answerid,
            success=True,
            message="질문과 답변이 성공적으로 저장되었습니다."
        )

    except HTTPException as e:
        # HTTP 예외는 그대로 전달
        raise e
    except Exception as e:
        # 오류 발생 시 트랜잭션 롤백
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"질문과 답변 저장 중 오류 발생: {str(e)}"
        )