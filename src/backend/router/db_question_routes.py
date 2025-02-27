from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.resume_answer import extract_text_from_pdf, generate_interview_question
from src.backend.database_config import get_db
from src.backend.model import Question

router = APIRouter()


class ResumeQuestionResponse(BaseModel):
    question: dict
    answer: dict


@router.post("/db/questions/{questionid}/answers", response_model=ResumeQuestionResponse)
async def generate_question_db(questionid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        resume_text = extract_text_from_pdf(file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="이력서에서 텍스트를 추출할 수 없습니다.")

        # 딕셔너리를 반환받음
        question_result = generate_interview_question(resume_text)
        if "error" in question_result:
            raise HTTPException(status_code=500, detail="면접 질문 생성 실패")

        # 데이터베이스에 질문 저장
        db_question = Question(
            questionid=questionid,
            username="testuser",  # 실제 사용 시 사용자 인증 로직 필요
            questiontext=question_result["question"]["questiontext"],
            questiontype=question_result["question"]["questiontype"],
            questionnum=1  # 기본값 설정
        )

        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        # 이미 올바른 구조로 반환
        return question_result

    except HTTPException as e:
        return JSONResponse(content={
            "status": e.status_code,
            "message": e.detail
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))