from fastapi import FastAPI
import uvicorn
from router.analysis import router as api_router_analysis
from router.question_routes import router as api_router_generate

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
