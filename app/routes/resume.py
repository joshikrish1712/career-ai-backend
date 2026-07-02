import json, io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ATSResult, ResumeCreate, ResumeUpdate, ResumeOut, ResumeListItem
from app.services.auth_service import get_current_user
from app.services.resume_service import extract_text, detect_skills, suggest_career, compute_ats_score
from app.services.pdf_service import generate_pdf

router  = APIRouter(prefix="/resume", tags=["Resume"])
MAX_SIZE = 5 * 1024 * 1024

@router.post("/upload", response_model=ATSResult)
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files accepted.")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "File too large. Max 5 MB.")
    try:
        text = extract_text(content)
    except Exception:
        raise HTTPException(422, "Could not parse PDF.")
    if not text.strip():
        raise HTTPException(422, "PDF appears empty or image-only.")
    skills = detect_skills(text)
    career = suggest_career(skills)
    report = compute_ats_score(text, skills)
    return ATSResult(score=report["score"], career_suggestion=career,
                     skills=skills, sections=report["sections"], tips=report["tips"])

@router.post("/", response_model=ResumeOut)
def create_resume(body: ResumeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = Resume(user_id=current_user.id, name=body.name, template=body.template, data=json.dumps(body.data))
    db.add(r); db.commit(); db.refresh(r)
    r.data = json.loads(r.data)
    return r

@router.get("/", response_model=list[ResumeListItem])
def list_resumes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).all()

@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not r: raise HTTPException(404, "Resume not found.")
    r.data = json.loads(r.data) if isinstance(r.data, str) else r.data
    return r

@router.put("/{resume_id}", response_model=ResumeOut)
def update_resume(resume_id: int, body: ResumeUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not r: raise HTTPException(404, "Resume not found.")
    if body.name is not None:      r.name = body.name
    if body.template is not None:  r.template = body.template
    if body.data is not None:      r.data = json.dumps(body.data)
    if body.ats_score is not None: r.ats_score = body.ats_score
    db.commit(); db.refresh(r)
    r.data = json.loads(r.data) if isinstance(r.data, str) else r.data
    return r

@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not r: raise HTTPException(404, "Resume not found.")
    db.delete(r); db.commit()
    return {"message": "Deleted"}

@router.get("/{resume_id}/pdf")
def download_pdf(resume_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not r: raise HTTPException(404, "Resume not found.")
    data      = json.loads(r.data) if isinstance(r.data, str) else r.data
    pdf_bytes = generate_pdf(data, r.template)
    filename  = r.name.replace(" ", "_") + ".pdf"
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})

@router.post("/{resume_id}/duplicate", response_model=ResumeOut)
def duplicate_resume(resume_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    r = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not r: raise HTTPException(404, "Resume not found.")
    copy = Resume(user_id=current_user.id, name=r.name+" (Copy)", template=r.template, ats_score=r.ats_score, data=r.data)
    db.add(copy); db.commit(); db.refresh(copy)
    copy.data = json.loads(copy.data) if isinstance(copy.data, str) else copy.data
    return copy
