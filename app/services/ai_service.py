"""
AI calls using Groq API (free tier).
Model: llama3-8b-8192 — fast, free, works great for resume tasks.
Groq API is OpenAI-compatible so it's very simple to use.
"""
import requests
import json
import re
from app.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.3-70b-versatile"

def _ask(prompt: str) -> str:
    """Call Groq API using OpenAI-compatible format."""
    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise Exception(f"Groq API error {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_cover_letter(name, role, job_title, company, skills, years, job_description, tone) -> str:
    prompt = f"""Write a {tone.lower()} cover letter.
Name: {name}
Current role: {role or 'Not specified'}
Applying for: {job_title} at {company}
Years of experience: {years or 'Not specified'}
Key skills: {skills or 'Not specified'}
{f'Job description: {job_description}' if job_description else ''}
Rules:
- 3-4 paragraphs, complete and ready to send
- Start with: Dear Hiring Manager,
- End with: Sincerely, {name}
- Tone: {tone}
- Return ONLY the letter text, no explanation"""
    return _ask(prompt)


def rewrite_bullets(bullets: str, job_title: str, company: str = "") -> str:
    prompt = f"""Rewrite these resume bullet points for a {job_title} role.
Original:
{bullets}
Rules:
- Start each bullet with a strong action verb
- Add quantifiable metrics where possible
- Keep ATS-friendly language
- Return ONLY the rewritten bullets, one per line starting with -
- No explanation, no preamble"""
    return _ask(prompt)


def job_match_analysis(resume_text: str, job_description: str) -> dict:
    prompt = f"""Analyze how well this resume matches the job description.
RESUME:
{resume_text[:2000]}
JOB DESCRIPTION:
{job_description[:1500]}
Return ONLY a valid JSON object with no markdown formatting:
{{"match_score": 75, "matched_keywords": ["python", "react"], "missing_keywords": ["docker", "kubernetes"], "suggestions": ["Add Docker experience to your skills section", "Mention CI/CD pipeline experience"]}}"""
    text = _ask(prompt)
    text = re.sub(r"```json|```", "", text).strip()
    # Find JSON object in response
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group()
    return json.loads(text)


def generate_summary(name: str, role: str, experience: list, skills: list) -> str:
    exp_text = "; ".join([
        f"{e.get('title', '')} at {e.get('company', '')}"
        for e in experience if e.get('title')
    ]) or "various roles"
    skills_text = ", ".join(skills) if skills else "programming and development"
    prompt = f"""Write a 2-3 sentence professional resume summary.
Person: {name or 'the candidate'}
Role: {role or 'Software Professional'}
Experience: {exp_text}
Skills: {skills_text}
Rules:
- No first-person pronouns (no I, my, me)
- ATS-friendly keywords
- Highlight value and expertise
- Return ONLY the summary text, nothing else, no quotes"""
    return _ask(prompt)
