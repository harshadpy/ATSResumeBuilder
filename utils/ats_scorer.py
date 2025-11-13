from typing import Dict, List
import os
import re
import requests


def calculate_ats_score(resume_data: Dict) -> Dict:
    url = os.getenv("ATS_API_URL", "").strip()
    key = os.getenv("ATS_API_KEY", "").strip()
    if url:
        try:
            return calculate_ats_score_api(resume_data, url, key)
        except Exception:
            return calculate_ats_score_local(resume_data)
    return calculate_ats_score_local(resume_data)

def calculate_ats_score_api(resume_data: Dict, url: str, api_key: str) -> Dict:
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(url, json=resume_data, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    out = {
        "score": int(data.get("score", 0)),
        "keyword_score": int(data.get("keyword_score", 0)),
        "format_score": int(data.get("format_score", 0)),
        "suggestions": list(data.get("suggestions", [])),
    }
    return out

def calculate_ats_score_local(resume_data: Dict) -> Dict:
    """Deterministic rubric-based ATS scoring (no randomness).
    Breakdown:
    - Completeness (30): contact, summary, skills, education, experience, projects
    - Keyword relevance (40): skills richness, reuse of skills/keywords in bullets, title alignment
    - Formatting/readability (30): bullets present, action verbs, quantified impact, date consistency, links
    """
    personal = resume_data.get("personal_info", {}) or {}
    skills: List[str] = (resume_data.get("skills", []) or [])
    education = resume_data.get("education", []) or []
    experience = resume_data.get("experience", []) or []
    projects = resume_data.get("projects", []) or []

    text_blobs: List[str] = []
    if personal.get("summary"): text_blobs.append(str(personal["summary"]))
    for j in experience:
        text_blobs.append(" ".join([str(j.get("title","")), str(j.get("company","")), str(j.get("dates",""))]))
        text_blobs.extend([str(b) for b in (j.get("responsibilities", []) or [])])
    for p in projects:
        text_blobs.append(" ".join([str(p.get("name","")), str(p.get("description","")), str(p.get("technologies",""))]))
    combined_text = "\n".join(text_blobs).lower()

    # 1) Completeness (30)
    completeness = 0
    # Contact: email and at least one of phone/link
    email_ok = bool(re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", str(personal.get("email",""))))
    phone_ok = bool(re.search(r"\d{10}", str(personal.get("phone",""))))
    link_ok = any(personal.get(k) for k in ("linkedin","github","website"))
    if email_ok and (phone_ok or link_ok): completeness += 8
    if personal.get("summary"): completeness += 6
    if len(skills) >= 8: completeness += 6
    if education: completeness += 5
    if experience: completeness += 5
    if projects: completeness += 0  # optional, do not over-penalize

    # 2) Keyword relevance (40)
    kw_score = 0
    # Skills richness up to 20
    uniq_skills = {s.lower().strip() for s in skills}
    kw_score += min(20, len(uniq_skills) * 1.25)  # 16 skills -> 20 pts
    # Reuse of keywords in bullets and summary up to 15
    reuse_hits = sum(1 for s in uniq_skills if s and s in combined_text)
    kw_score += min(15, reuse_hits * 0.8)
    # Role/title signals up to 5
    title_text = " ".join([str(j.get("title","")) for j in experience]).lower()
    if any(t in title_text for t in ["engineer","developer","analyst","scientist","manager","intern"]):
        kw_score += 3
    if any(t in title_text for t in ["senior","lead","principal"]):
        kw_score += 2

    keyword_score = int(max(0, min(100, round((kw_score/40)*100))))

    # 3) Formatting/readability (30)
    fmt = 0
    # Bullets present in experience
    bullet_lines = 0
    for j in experience:
        bullet_lines += sum(1 for b in (j.get("responsibilities", []) or []) if len(str(b)) >= 20)
    if bullet_lines >= 5: fmt += 8
    elif bullet_lines >= 2: fmt += 5

    # Action verbs
    action_verbs = [
        "led","built","developed","designed","implemented","owned","improved","reduced","increased",
        "optimized","launched","created","automated","migrated","analyzed","architected","delivered","managed",
    ]
    verb_hits = sum(1 for v in action_verbs if re.search(rf"\b{re.escape(v)}\b", combined_text))
    fmt += min(8, verb_hits)

    # Quantified impact (numbers, %, x)
    quant_hits = len(re.findall(r"\b\d+\b|%|x\b", combined_text))
    if quant_hits >= 6: fmt += 7
    elif quant_hits >= 3: fmt += 5
    elif quant_hits >= 1: fmt += 3

    # Date consistency in experience
    date_ok = 0
    date_re = re.compile(r"(\b\d{4}\b|\b[A-Za-z]{3,9}\s*\d{4}\b)")
    for j in experience:
        if date_re.search(str(j.get("dates",""))):
            date_ok += 1
    if date_ok == len(experience) and len(experience) > 0:
        fmt += 5
    elif date_ok >= max(1, len(experience)//2):
        fmt += 3

    # Links present (LinkedIn/GitHub)
    if personal.get("linkedin") or personal.get("github"): fmt += 2

    format_score = int(max(0, min(100, round((fmt/30)*100))))

    # Aggregate overall (weighted)
    completeness_score = int(max(0, min(100, round((completeness/30)*100))))
    overall = int(round(0.30*completeness_score + 0.40*keyword_score + 0.30*format_score))

    # Suggestions
    suggestions: List[str] = []
    if not personal.get("summary"):
        suggestions.append("Add a concise professional summary with role-relevant keywords.")
    if len(skills) < 10:
        suggestions.append("Add more role-relevant skills (target 10–20 distinct skills).")
    if not experience:
        suggestions.append("Provide at least one experience entry with measurable, impact-focused bullets.")
    else:
        if bullet_lines < 5:
            suggestions.append("Increase bullet points per role (aim for 4–6 strong bullets).")
        if verb_hits < 4:
            suggestions.append("Start bullets with strong action verbs (e.g., Led, Built, Optimized, Delivered).")
        if quant_hits < 3:
            suggestions.append("Quantify impact with numbers, % or multipliers where possible.")
        if date_ok < len(experience):
            suggestions.append("Normalize date formats across roles (e.g., Jan 2023 – Present).")
    if not (personal.get("linkedin") or personal.get("github")):
        suggestions.append("Include a LinkedIn and/or GitHub link for recruiter context.")
    if education and isinstance(education[0], str) and "-" not in education[0] and "202" not in education[0]:
        suggestions.append("Normalize education entries with degree, institution, and graduation year.")

    breakdown = {
        "weights": {"completeness": 30, "keywords": 40, "format": 30},
        "overall_formula": "0.30*completeness + 0.40*keywords + 0.30*format",
        "completeness": {
            "points": completeness,
            "score": int(max(0, min(100, round((completeness/30)*100)))),
            "criteria": {
                "email_ok": email_ok,
                "phone_ok": phone_ok,
                "link_ok": link_ok,
                "summary_present": bool(personal.get("summary")),
                "skills_count": len(skills),
                "education_present": bool(education),
                "experience_present": bool(experience),
            },
        },
        "keywords": {
            "raw_points": kw_score,
            "score": keyword_score,
            "criteria": {
                "distinct_skills": len(uniq_skills),
                "reuse_hits": reuse_hits,
                "has_role_signal": any(t in title_text for t in ["engineer","developer","analyst","scientist","manager","intern"]),
                "has_seniority_signal": any(t in title_text for t in ["senior","lead","principal"]),
            },
        },
        "format": {
            "raw_points": fmt,
            "score": format_score,
            "criteria": {
                "bullet_lines": bullet_lines,
                "action_verb_hits": verb_hits,
                "quantified_hits": quant_hits,
                "date_entries_with_match": date_ok,
                "total_experience_entries": len(experience),
                "links_present": bool(personal.get("linkedin") or personal.get("github")),
            },
        },
    }

    return {
        "score": int(max(0, min(100, overall))),
        "keyword_score": keyword_score,
        "format_score": format_score,
        "suggestions": suggestions,
        "breakdown": breakdown,
    }
