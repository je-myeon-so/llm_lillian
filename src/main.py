from fastapi import FastAPI

app = FastAPI(
    title="Job Qualification Analysis API",
    description="이력서 분석 및 면접 피드백을 제공하는 API",
    version="1.0.0"
)

# 기본 라우트
@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Qualification Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
