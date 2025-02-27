from src.backend.database_config import Base, engine
from src.backend.model import Question, UserAnswer, Feedback

def create_all_tables():
    # 데이터베이스에 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료!")

if __name__ == "__main__":
    create_all_tables()