from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from answer_analyzer import analyze_text_with_gpt
from answer_analyzer import generate_follow_up

router = APIRouter()

class AnswerRequest(BaseModel):
    question: str
    answer: str

class FollowUpRequest(BaseModel):
    question: str
    answer: str

@router.post("/answers/{answerId}/feedback")
async def analyze_answer_api(request: AnswerRequest):
    job_role = '개발자'
    try:
        result = analyze_text_with_gpt(request.question, request.answer, job_role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/questions/{questionid}/follow-up")
async def generate_follow_up_api(request: FollowUpRequest):
    job_role = '개발자'
    try:
        result = generate_follow_up(request.answer, request.question, job_role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))