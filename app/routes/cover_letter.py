from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resume import CoverLetterRecord
from app.schemas.resume import CoverLetterRequest, CoverLetterResponse, CoverLetterOut
from app.services.auth_service import get_current_user, get_current_user_optional
from app.services.ai_service import generate_cover_letter
from app.config import settings

router = APIRouter(prefix="/cover-letter", tags=["Cover Letter"])

@router.post("/generate", response_model=CoverLetterResponse)
async def generate(req: CoverLetterRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    if not settings.groq_api_key or settings.groq_api_key == "paste-your-key-here":
        raise HTTPException(503, "GROQ_API_KEY not configured in .env file.")
    try:
        letter = generate_cover_letter(req.name, req.role, req.job_title, req.company,
                                        req.skills, req.years, req.job_description, req.tone)
    except Exception as e:
        raise HTTPException(500, f"AI generation failed: {str(e)}")
    record_id = None
    if current_user:
        record = CoverLetterRecord(user_id=current_user.id, company=req.company, role=req.job_title, content=letter)
        db.add(record); db.commit(); db.refresh(record)
        record_id = record.id
    return CoverLetterResponse(id=record_id, letter=letter, word_count=len(letter.split()))

@router.get("/", response_model=list[CoverLetterOut])
def list_cover_letters(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(CoverLetterRecord).filter(CoverLetterRecord.user_id == current_user.id)\
             .order_by(CoverLetterRecord.created_at.desc()).all()

@router.delete("/{cl_id}")
def delete_cover_letter(cl_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cl = db.query(CoverLetterRecord).filter(CoverLetterRecord.id == cl_id,
         CoverLetterRecord.user_id == current_user.id).first()
    if not cl: raise HTTPException(404, "Cover letter not found.")
    db.delete(cl); db.commit()
    return {"message": "Deleted"}
