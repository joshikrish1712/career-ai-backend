from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name       = Column(String, nullable=False, default="Untitled Resume")
    template   = Column(String, default="modern")
    ats_score  = Column(Float, nullable=True)
    data       = Column(Text, default="{}")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user       = relationship("User", back_populates="resumes")

class CoverLetterRecord(Base):
    __tablename__ = "cover_letters"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company    = Column(String)
    role       = Column(String)
    content    = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    user       = relationship("User", back_populates="cover_letters")
