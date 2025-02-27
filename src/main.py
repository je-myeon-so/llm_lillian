from fastapi import FastAPI
from routes import question_routes 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()



app.include_router(question_routes.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}

