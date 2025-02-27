from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from src.router.analysis import router as api_router_analysis
from src.router.question_routes import router as api_router_generate

app = FastAPI(
    title="Interview Analysis API",
    description="API for analyzing interview answers and generating follow-up questions.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Qualification Analysis API"}

# Serve the favicon.ico to prevent 404 errors
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")  # Make sure this file exists in your project directory

# Include routers
app.include_router(api_router_analysis, prefix="/api")
app.include_router(api_router_generate, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
