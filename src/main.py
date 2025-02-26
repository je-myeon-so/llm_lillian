from fastapi import FastAPI
from routes import question_routes 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(question_routes.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}

