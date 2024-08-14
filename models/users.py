from sqlalchemy import Column, Integer, String
from config.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False)
    nickname = Column(String(length=255), nullable=True)