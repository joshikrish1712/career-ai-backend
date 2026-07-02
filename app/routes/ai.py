from fastapi import APIRouter, HTTPException, Depends
from app.schemas.resume import JobMatchRequest, JobMatchResult, BulletRewriteRequest, BulletRewriteResult
from app.services.ai_service import job_match_analysis, rewrite_bullets, generate_summary
from app.services.auth_service import get_current_user_optional
from app.config import settings
import traceback
import requests

router = APIRouter(prefix="/ai", tags=["AI"])

def _check_key():
    if not settings.groq_api_key or settings.groq_api_key == "paste-your-key-here":
        raise HTTPException(503, "GROQ_API_KEY not configured in .env file.")

# ── Test endpoint: open http://127.0.0.1:8000/ai/test in browser ──
@router.get("/test")
def test_groq():
    key = settings.groq_api_key
    if not key or key == "paste-your-key-here":
        return {"status": "error", "message": "No GROQ_API_KEY set in .env file"}
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": "Say hello in one word."}], "max_tokens": 10},
            timeout=10,
        )
        if resp.status_code == 200:
            text = resp.json()["choices"][0]["message"]["content"].strip()
            return {"status": "ok", "model": "llama3-8b-8192", "response": text}
        else:
            return {"status": "error", "http_code": resp.status_code, "detail": resp.text[:300]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/generate-summary")
async def summary(body: dict, _=Depends(get_current_user_optional)):
    _check_key()
    try:
        name       = str(body.get("name", "") or "Professional")
        role       = str(body.get("role", "") or "Professional")
        experience = body.get("experience", []) or []
        skills     = body.get("skills", []) or []
        skills     = [str(s) for s in skills if s and str(s).strip()]
        text = generate_summary(name, role, experience, skills)
        return {"summary": text}
    except Exception as e:
        print("\n===== SUMMARY ERROR =====")
        print(traceback.format_exc())
        print("=========================\n")
        raise HTTPException(500, f"Failed: {str(e)}")

@router.post("/job-match", response_model=JobMatchResult)
async def job_match(req: JobMatchRequest, _=Depends(get_current_user_optional)):
    _check_key()
    try:
        result = job_match_analysis(req.resume_text, req.job_description)
        return JobMatchResult(**result)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@router.post("/rewrite-bullets", response_model=BulletRewriteResult)
async def rewrite(req: BulletRewriteRequest, _=Depends(get_current_user_optional)):
    _check_key()
    try:
        rewritten = rewrite_bullets(req.bullets, req.job_title, req.company or "")
        return BulletRewriteResult(rewritten=rewritten)
    except Exception as e:
        raise HTTPException(500, f"Rewrite failed: {str(e)}")
