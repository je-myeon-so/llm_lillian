from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.resume_answer import extract_text_from_pdf, generate_interview_question

router = APIRouter()

class ResumeQuestionResponse(BaseModel):
    question: dict
    answer: dict

@router.post("/questions/{questionid}/answers", response_model=ResumeQuestionResponse)
async def generate_question(questionid: int, file: UploadFile = File(...)):
    try:
        resume_text = extract_text_from_pdf(file.file)
        if not resume_text:
            raise HTTPException(status_code=400, detail="이력서에서 텍스트를 추출할 수 없습니다.")

        # 딕셔너리를 반환받음
        question_result = generate_interview_question(resume_text)
        if "error" in question_result:
            raise HTTPException(status_code=500, detail="면접 질문 생성 실패")

        # 이미 올바른 구조로 반환
        return question_result

    except HTTPException as e:
        return JSONResponse(content={
            "status": e.status_code,
            "message": e.detail
        })
