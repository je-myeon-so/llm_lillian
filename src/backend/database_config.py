from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from urllib.parse import quote
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# DB 접속 정보
# USER = "root"
# PWD = quote("ysy5282!")  # URL 인코딩 적용
# HOST = "localhost"  # 포트 번호 제거
# PORT = 3306
# DATABASE = "jemyeonso"

# 환경 변수에서 DB 정보 가져오기
MYSQL_USER = os.getenv("MYSQL_USER", "root")  # 기본값 설정
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ysy5282!")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "test")

# 데이터베이스 URL 설정
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 기본 클래스 생성
Base = declarative_base()

# 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
