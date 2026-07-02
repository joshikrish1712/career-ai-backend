from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    name            = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, server_default=func.now())
    resumes         = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    cover_letters   = relationship("CoverLetterRecord", back_populates="user", cascade="all, delete-orphan")
