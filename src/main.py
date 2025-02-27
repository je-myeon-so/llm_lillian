from fastapi import FastAPI
import uvicorn
from src.backend.database_config import engine
from src.backend.model import Question, UserAnswer, Feedback, User
from src.router.analysis import router as api_router_analysis
from src.router.question_routes import router as api_router_generate
from src.stt.stt import router as api_router_stt
from src.router.interview import router as api_router_interview

# 데이터베이스 테이블 생성
User.metadata.create_all(bind=engine)
Question.metadata.create_all(bind=engine)
UserAnswer.metadata.create_all(bind=engine)
Feedback.metadata.create_all(bind=engine)

app = FastAPI(
    title="Interview Analysis API",
    description="API for analyzing interview answers and generating follow-up questions.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Qualification Analysis API"}

app.include_router(api_router_analysis, prefix="/api")
app.include_router(api_router_generate, prefix="/api")

app.include_router(api_router_stt, prefix="/api/stt")
app.include_router(api_router_interview, prefix="/api/interview")