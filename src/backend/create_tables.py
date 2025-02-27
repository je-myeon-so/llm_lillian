from database_config import Base, ENGINE


# 데이터베이스에 테이블 생성
Base.metadata.create_all(bind=ENGINE)

#print("✅ 테이블 생성 완료!")
