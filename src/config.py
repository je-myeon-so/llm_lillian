import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from urllib.parse import quote


# Load API key from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MYSQL_USER = os.getenv("MYSQL_USER", "admin")  # 기본값 설정
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "l1HpWHZYwvWCBAQfILo9")
MYSQL_HOST = os.getenv("MYSQL_HOST", "jemyeonsodb.cbsa6mw24cwc.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "jemyeonso")


DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{quote(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 기본 클래스 생성
Base = declarative_base()

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set it in the .env file.")

# 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
