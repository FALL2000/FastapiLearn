from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), nullable=False)
    email = Column(String(length=10), unique=True, nullable=False)
    nickname = Column(String(length=50), nullable=True)

    items = relationship("Item", back_populates="owner")