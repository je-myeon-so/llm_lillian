from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from src.backend.model import Question, UserAnswer, Feedback
from src.backend.schemas import UserBase
from src.resume_answer import extract_text_from_pdf, generate_interview_question
from src.answer_analyzer import analyze_text_with_gpt, generate_follow_up
from src.config import get_db
from openai import OpenAI
from sqlalchemy.orm import Session
import os
import shutil

router = APIRouter()

client = OpenAI()

UPLOAD_DIR = "uploads"  # 업로드할 폴더
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 폴더 없으면 생성

@router.get("/question/{questionnum}")
async def get_question(username: str, questionnum: int, db: Session = Depends(get_db)):
    try:
        # DB에서 답변 조회
        db_answer = db.query(Question).filter(Question.username == username).filter(
            Question.questionnum == questionnum).first()

        result = {
            "question": db_answer.questiontext,
            "questionnum": db_answer.questionnum
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question/{questionnum}/answer")
async def answer_question(questionnum: int, username = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".wav"):  # 파일 확장자 확인
        raise HTTPException(status_code=400, detail="WAV 파일만 지원됩니다.")

    # 파일 저장 경로 설정
    file_path = os.path.join(UPLOAD_DIR, f"{username}_{questionnum}.wav")

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # OpenAI Whisper API 호출
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"
            )

        print(username)
        print(questionnum)
        print(transcription.text)


        question = db.query(Question).filter(Question.username == username).filter(Question.questionnum == questionnum).first()

        useranswer = UserAnswer(questionid=question.questionid, username=username, answertext=transcription.text)
        db.add(useranswer)
        db.commit()
        db.refresh(useranswer)

        if questionnum == 3:
            for i in range(1, 4):
                question = db.query(Question).filter(Question.username == username).filter(Question.questionnum == i).first()
                answer = db.query(UserAnswer).filter(UserAnswer.questionid == question.questionid).first()

                result = analyze_text_with_gpt(text=answer.answertext, question=question.questiontext, job_role='개발자')

                for item in result.get("analysis", []):
                    print(item)
                    errortext = item.get("error_text", "")
                    errortype = item.get("error_type", "")
                    feedbacktext = item.get("feedback", "")
                    suggestion = item.get("suggestion", "")

                    feedback = Feedback(answerid=answer.answerid, questionid=question.questionid, username=username, errortext=errortext, errortype=errortype, feedback=feedbacktext, suggestion=suggestion)
                    db.add(feedback)
                    db.commit()
                    db.refresh(feedback)

            return {"question": {
                "question_text": "면접 질문을 더 받아보시겠습니까?",
                "question_type": "면접 종료"
            }}

        result = generate_follow_up(answer=transcription.text, question=question.questiontext, job_role='개발자')
        questiontext = result.get('question', {}).get('question_text', '')
        questiontype = result.get('question', {}).get('questiontype', '')


        print(result)
        print(questiontext)

        question = Question(username=username, questiontext=questiontext, questionnum=questionnum + 1, questiontype=questiontype)
        db.add(question)
        db.commit()
        db.refresh(question)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
