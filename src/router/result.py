from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from src.backend.model import Question, UserAnswer, Feedback
from src.backend.schemas import UserBase, FeedbackCreate
from src.resume_answer import extract_text_from_pdf, generate_interview_question
from src.answer_analyzer import analyze_text_with_gpt, generate_follow_up
from src.config import get_db
from openai import OpenAI
from sqlalchemy.orm import Session
import os
import shutil

router = APIRouter()

@router.get("/answer/{questionnum}/feedback")
async def get_feedback(questionnum: int, username: str, db: Session = Depends(get_db)):
    try:
        question = db.query(Question).filter(Question.username == username).filter(Question.questionnum == questionnum).first()
        answer = db.query(UserAnswer).filter(UserAnswer.username == username).filter(UserAnswer.questionid == question.questionid).first()
        feedback = db.query(Feedback).filter(Feedback.answerid == answer.answerid).all()

        analysis_result = {
            "analysis": [
                {
                    "error_text": item.errortext,
                    "error_type": item.errortype,
                    "feedback": item.feedback,
                    "suggestion": item.suggestion
                }
                for item in feedback
            ]
        }

        return {
            "original_answer": answer.answertext,
            "analysis_result": analysis_result
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))