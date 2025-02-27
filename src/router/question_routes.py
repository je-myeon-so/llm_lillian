from fastapi import APIRouter, HTTPException, UploadFile, File,Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.backend.database_config import get_db
from src.backend.model import Question
from pydantic import BaseModel
from src.resume_answer import extract_text_from_pdf, generate_interview_question

router = APIRouter()

class ResumeQuestionResponse(BaseModel):
    question: dict
    answer: dict

@router.post("/upload/file", response_model=ResumeQuestionResponse)
async def generate_question(username = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        resume_text = extract_text_from_pdf(file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="이력서에서 텍스트를 추출할 수 없습니다.")

        # 딕셔너리를 반환받음
        question_result = generate_interview_question(resume_text)
        questiontext = question_result.get("question", {}).get("questiontext")
        questiontype = question_result.get("question", {}).get("questiontype")

        print(questiontext)
        print(questiontype)
        question = Question(username=username, questiontext=questiontext, questionnum=1, questiontype=questiontype)
        db.add(question)
        db.commit()
        db.refresh(question)

        if "error" in question_result:
            raise HTTPException(status_code=500, detail="면접 질문 생성 실패")

        # 이미 올바른 구조로 반환
        return question_result

    except HTTPException as e:
        return JSONResponse(content={
            "status": e.status_code,
            "message": e.detail
        })
