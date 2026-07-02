from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ATSResult(BaseModel):
    score: float
    career_suggestion: str
    skills: List[str]
    sections: List[dict]
    tips: List[str]

class CoverLetterRequest(BaseModel):
    name: str
    role: Optional[str] = ""
    job_title: str
    company: str
    skills: Optional[str] = ""
    years: Optional[str] = ""
    job_description: Optional[str] = ""
    tone: str = "Professional"

class CoverLetterResponse(BaseModel):
    id: Optional[int] = None
    letter: str
    word_count: int

class CoverLetterOut(BaseModel):
    id: int
    company: Optional[str]
    role: Optional[str]
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

class ResumeCreate(BaseModel):
    name: str = "Untitled Resume"
    template: str = "modern"
    data: dict = {}

class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    template: Optional[str] = None
    data: Optional[dict] = None
    ats_score: Optional[float] = None

class ResumeOut(BaseModel):
    id: int
    name: str
    template: str
    ats_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    data: dict
    class Config:
        from_attributes = True

class ResumeListItem(BaseModel):
    id: int
    name: str
    template: str
    ats_score: Optional[float]
    updated_at: datetime
    class Config:
        from_attributes = True

class JobMatchRequest(BaseModel):
    resume_text: str
    job_description: str

class JobMatchResult(BaseModel):
    match_score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]

class BulletRewriteRequest(BaseModel):
    bullets: str
    job_title: str
    company: Optional[str] = ""

class BulletRewriteResult(BaseModel):
    rewritten: str
