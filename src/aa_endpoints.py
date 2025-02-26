from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from answer_analyzer import analyze_text_with_gpt, generate_follow_up

app = FastAPI()

class AnalysisRequest(BaseModel):
    text: str
    context: str = ""

@app.post("/api/sessions/{sessionId}/feedbacks/generate")
def analyze_text_with_gpt_endpoint(request: AnalysisRequest):
    mail = {
    "success": True,
    "message": "피드백이 성공적으로 생성되었습니다"
    }
    print(mail)
    return analyze_text_with_gpt(request.text, request.context)

@app.post("/generate_follow_up")
def generate_follow_up_endpoint(request: AnalysisRequest):
    return {"follow_up_question": generate_follow_up(request.text, request.context)}
