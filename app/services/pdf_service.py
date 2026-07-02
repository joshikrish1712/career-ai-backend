import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

TEMPLATES = {
    "modern":    colors.HexColor("#1B4FD8"),
    "classic":   colors.HexColor("#1a1a1a"),
    "minimal":   colors.HexColor("#059669"),
    "executive": colors.HexColor("#7C3AED"),
}

def _st(accent):
    return {
        "name":     ParagraphStyle("name",     fontSize=20, fontName="Helvetica-Bold", textColor=accent, spaceAfter=2, leading=24),
        "contact":  ParagraphStyle("contact",  fontSize=9,  fontName="Helvetica",      textColor=colors.HexColor("#6B7280"), spaceAfter=4),
        "section":  ParagraphStyle("section",  fontSize=9,  fontName="Helvetica-Bold", textColor=accent, spaceBefore=10, spaceAfter=3),
        "job":      ParagraphStyle("job",      fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#111827"), spaceAfter=1),
        "company":  ParagraphStyle("company",  fontSize=9,  fontName="Helvetica",      textColor=colors.HexColor("#6B7280"), spaceAfter=2),
        "body":     ParagraphStyle("body",     fontSize=9,  fontName="Helvetica",      textColor=colors.HexColor("#374151"), leading=13, spaceAfter=3),
        "bullet":   ParagraphStyle("bullet",   fontSize=9,  fontName="Helvetica",      textColor=colors.HexColor("#374151"), leading=13, leftIndent=12, spaceAfter=1),
        "date":     ParagraphStyle("date",     fontSize=8,  fontName="Helvetica",      textColor=colors.HexColor("#9CA3AF"), alignment=2),
    }

def generate_pdf(resume_data: dict, template_name: str = "modern") -> bytes:
    accent = TEMPLATES.get(template_name, TEMPLATES["modern"])
    st     = _st(accent)
    personal   = resume_data.get("personal", {})
    experience = resume_data.get("experience", [])
    education  = resume_data.get("education", [])
    skills_raw = resume_data.get("skills", [])
    summary    = resume_data.get("summary", "")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    story = []

    # Header
    story.append(Paragraph(personal.get("name") or "Your Name", st["name"]))
    contact_parts = [personal.get("email",""), personal.get("phone",""), personal.get("location",""), personal.get("linkedin","")]
    contact_line  = "  ·  ".join(p for p in contact_parts if p)
    if contact_line:
        story.append(Paragraph(contact_line, st["contact"]))
    story.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=6))

    # Summary
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", st["section"]))
        story.append(Paragraph(summary, st["body"]))
        story.append(Spacer(1, 4))

    # Experience
    exp_items = [e for e in experience if e.get("title") or e.get("company")]
    if exp_items:
        story.append(Paragraph("WORK EXPERIENCE", st["section"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=4))
        for exp in exp_items:
            date_str = exp.get("start","")
            if exp.get("end"): date_str += f" – {exp['end']}"
            t = Table([[Paragraph(exp.get("title",""), st["job"]), Paragraph(date_str, st["date"])]],
                      colWidths=[PAGE_W - 2*MARGIN - 4*cm, 4*cm])
            t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
            story.append(t)
            if exp.get("company"): story.append(Paragraph(exp["company"], st["company"]))
            if exp.get("desc"):
                for line in exp["desc"].split("\n"):
                    if line.strip(): story.append(Paragraph(f"• {line.strip()}", st["bullet"]))
            story.append(Spacer(1, 4))

    # Education
    edu_items = [e for e in education if e.get("degree") or e.get("school")]
    if edu_items:
        story.append(Paragraph("EDUCATION", st["section"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=4))
        for ed in edu_items:
            story.append(Paragraph(ed.get("degree",""), st["job"]))
            school_line = ed.get("school","")
            if ed.get("year"): school_line += f"  ·  {ed['year']}"
            if school_line: story.append(Paragraph(school_line, st["company"]))
            story.append(Spacer(1, 4))

    # Skills
    if skills_raw:
        story.append(Paragraph("TECHNICAL SKILLS", st["section"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=4))
        
        # Check if structured or simple format
        if skills_raw and isinstance(skills_raw[0], dict):
            for item in skills_raw:
                cat = item.get("category", "").strip()
                lst = item.get("list", "").strip()
                if cat or lst:
                    line = f"<b>{cat}:</b> {lst}" if cat else lst
                    story.append(Paragraph(line, st["body"]))
        else:
            skills = [s for s in skills_raw if s]
            if skills:
                story.append(Paragraph("  ·  ".join(skills), st["body"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()
