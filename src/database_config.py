from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

# DB 접속 정보
USER = "root"
PWD = quote("kim62583@@")  # URL 인코딩 적용
HOST =  "localhost" #"jemyeonsodb.cbsa6mw24cwc.ap-northeast-2.rds.amazonaws.com"
PORT = 3306
DATABASE = "test"

# DB URL 설정
DB_URL = f'mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4'

class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn