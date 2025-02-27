from fastapi import FastAPI
import uvicorn
from src.backend.router import question_router, analysis_router #,user_router
from src.backend.database_config import engine
from src.backend.model import Question, UserAnswer, Feedback, User
from src.backend.router.db_qa_routes import router as qa_router
from src.backend.router.db_question_answer_routes import router as qa_query_router

# 데이터베이스 테이블 생성
User.metadata.create_all(bind=engine)
Question.metadata.create_all(bind=engine)
UserAnswer.metadata.create_all(bind=engine)
Feedback.metadata.create_all(bind=engine)

app = FastAPI(
    title="Interview Analysis DB API",
    description="Database API for analyzing interview answers and generating follow-up questions.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Qualification Database API"}

# 백엔드 라우터 등록
app.include_router(question_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
#app.include_router(user_router)
app.include_router(qa_router, prefix="/questions")
app.include_router(qa_query_router)

if __name__ == "__main__":
    uvicorn.run("src.backend.main_db:app", host="0.0.0.0", port=8000, reload=True)