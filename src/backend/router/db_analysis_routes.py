from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.answer_analyzer import analyze_text_with_gpt, generate_follow_up
from src.backend.database_config import get_db
from src.backend.model import UserAnswer, Feedback, Question

router = APIRouter()


class AnswerRequest(BaseModel):
    question: str
    answer: str


class FollowUpRequest(BaseModel):
    question: str
    answer: str


@router.post("/db/answers/{answerId}/feedback")
async def analyze_answer_db(answerId: int, request: AnswerRequest, db: Session = Depends(get_db)):
    job_role = '개발자'
    try:
        # DB에서 답변 조회
        db_answer = db.query(UserAnswer).filter(UserAnswer.answerid == answerId).first()
        if not db_answer:
            # 답변이 없으면 새로 생성
            db_answer = UserAnswer(
                answerid=answerId,
                questionid=1,  # 임시 값, 실제로는 클라이언트에서 받거나 관계를 통해 얻어야 함
                username="testuser",  # 임시 값
                answertext=request.answer
            )
            db.add(db_answer)
            db.commit()
            db.refresh(db_answer)

        result = analyze_text_with_gpt(request.question, request.answer, job_role)

        # 피드백 저장
        if "analysis" in result:
            for analysis in result["analysis"]:
                feedback = Feedback(
                    answerid=answerId,
                    questionid=db_answer.questionid,
                    username=db_answer.username,
                    errortext=analysis.get("error_text"),
                    errortype=analysis.get("error_type"),
                    feedback=analysis.get("feedback"),
                    suggestion=analysis.get("suggestion")
                )
                db.add(feedback)
            db.commit()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/db/questions/{questionid}/follow-up")
async def generate_follow_up_db(questionid: int, request: FollowUpRequest, db: Session = Depends(get_db)):
    job_role = '개발자'
    try:
        result = generate_follow_up(request.answer, request.question, job_role)

        # 결과로 새 질문 저장
        if "question" in result:
            new_question = Question(
                username="testuser",  # 임시 값
                questiontext=result["question"].get("question_text", ""),
                questiontype="꼬리질문",
                questionnum=2  # 임시 값
            )
            db.add(new_question)
            db.commit()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))