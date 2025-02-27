from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from urllib.parse import quote

# DB 접속 정보
USER = "root"
PWD = quote("ysy5282!")  # URL 인코딩 적용
HOST = "localhost"  # 포트 번호 제거
PORT = 3306
DATABASE = "jemyeonso"

# DB URL 설정
DB_URL = f'mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4'

# SQLAlchemy 엔진 설정
ENGINE = create_engine(DB_URL, pool_recycle=500, echo=True)

# 세션 팩토리 생성
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=ENGINE))

# ORM의 기본 클래스 생성
Base = declarative_base()
