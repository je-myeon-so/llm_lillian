from sqlalchemy import Column, String
from src.backend.database_config import Base

class User(Base):
    __tablename__ = "user"
    name = Column(String(50), primary_key=True, nullable=False)
    password = Column(String(50), nullable=False)
