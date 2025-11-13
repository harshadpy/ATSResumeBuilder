import os
from typing import Dict, List
import re
from datetime import datetime


def enhance_resume_content(data: Dict, target_role: str = "", enhancement_level: str = "moderate") -> tuple[Dict, list]:
    """Enhance resume content using simple local heuristics with optional API fallbacks.

    Returns: (enhanced_data, modifications_list)
    enhancement_level: one of ['conservative','moderate','aggressive']
    """
    original = data or {}
    enhanced = dict(original) if isinstance(original, dict) else {}
    enhanced.setdefault("personal_info", {})

    summary = enhanced.get("personal_info", {}).get("summary", "")
    if not summary:
        summary = generate_resume_summary(enhanced, target_role)
    # Only lightly touch a non-empty, data-driven summary
    enhanced["personal_info"]["summary"] = enhance_summary(summary, target_role, enhancement_level)

    # Enhance experience bullets
    exp_list = enhanced.get("experience", []) or []
    improved_exp = []
    for job in exp_list:
        bullets = job.get("responsibilities", []) or []
        improved_bullets = [enhance_experience_bullet(b, target_role) for b in bullets]
        j2 = dict(job)
        j2["responsibilities"] = improved_bullets
        improved_exp.append(j2)
    enhanced["experience"] = improved_exp

    # Enhance skills ordering/deduping
    enhanced["skills"] = enhance_skills(enhanced.get("skills", []), target_role)

    # Attempt API-based enhancement if keys exist (best-effort, safe fallback)
    try:
        context = {"target_role": target_role, "level": enhancement_level}
        if os.getenv("OPENAI_API_KEY"):
            enhanced = enhance_with_openai(enhanced, context)
        elif os.getenv("GEMINI_API_KEY"):
            enhanced = enhance_with_gemini(enhanced, context)
    except Exception:
        # Silently fallback to local enhancements
        pass

    modifications = _diff_resume(original, enhanced)
    return enhanced, modifications


def enhance_with_openai(content: Dict, context: Dict) -> Dict:
    """Placeholder OpenAI enhancement. Returns content unchanged if API fails."""
    # Intentionally not importing openai at module import to avoid errors when package missing
    try:
        import openai  # type: ignore
        client = openai.OpenAI()
        # Minimal noop call pattern could be implemented; here we just return content to avoid latency
        return content
    except Exception:
        return content


def enhance_with_gemini(content: Dict, context: Dict) -> Dict:
    """Placeholder Gemini enhancement. Returns content unchanged if API fails."""
    try:
        import google.generativeai as genai  # type: ignore
        _ = genai  # unused in placeholder
        return content
    except Exception:
        return content


def enhance_summary(summary: str, role: str = "", level: str = "moderate") -> str:
    if not summary:
        return summary
    base = summary.strip()
    # If already looks like a full sentence summary, keep it as-is (avoid repetitive prefixes)
    if len(base.split()) > 6 and (base.endswith(".") or ";" in base or "," in base):
        return base
    # Otherwise, add minimal context optionally
    if role:
        if level == "aggressive":
            return f"{role} known for driving measurable outcomes. {base}"
        elif level == "conservative":
            return f"{role}. {base}"
        return f"{role} — {base}"
    return base


def enhance_experience_bullet(bullet: str, role: str = "") -> str:
    if not bullet:
        return bullet
    bullet = bullet.strip().lstrip("-•* ")
    verbs = ["Led", "Optimized", "Implemented", "Automated", "Delivered", "Improved"]
    has_verb = any(bullet.lower().startswith(v.lower()) for v in verbs)
    if not has_verb:
        bullet = f"Implemented {bullet[0].lower() + bullet[1:]}"
    if role and role.lower() not in bullet.lower():
        bullet += f" for {role} workflows"
    return bullet


def enhance_skills(skills: List[str], role: str = "") -> List[str]:
    if not skills:
        return []
    # Deduplicate, case-insensitive, prioritize role-relevant skills first
    seen = set()
    unique = []
    for s in skills:
        key = (s or "").strip()
        if not key:
            continue
        low = key.lower()
        if low not in seen:
            seen.add(low)
            unique.append(key)
    if role:
        role_low = role.lower()
        unique.sort(key=lambda x: 0 if role_low in x.lower() else 1)
    return unique[:25]


def generate_resume_summary(data: Dict, role: str = "") -> str:
    # Infer role from target_role or experience titles
    inferred_role = (role or "").strip()
    titles: List[str] = [str((j or {}).get("title", "")) for j in (data.get("experience", []) or [])]
    if not inferred_role and titles:
        # Pick the longest recent-looking title
        inferred_role = sorted(titles, key=lambda t: (len(t), t.lower()), reverse=True)[0] or "Professional"
    if not inferred_role:
        inferred_role = "Professional"

    # Estimate years from dates in experience
    def _parse_date_token(tok: str) -> datetime | None:
        tok = tok.strip()
        for fmt in ["%b %Y", "%B %Y", "%Y"]:
            try:
                return datetime.strptime(tok, fmt)
            except Exception:
                continue
        return None

    total_months = 0
    for j in (data.get("experience", []) or []):
        dates = str(j.get("dates", ""))
        # Common patterns: "Jan 2020 - Present", "2019 - 2022", "2021–Present"
        m = re.findall(r"([A-Za-z]{3,9}\s+\d{4}|\d{4})\s*[–-]\s*(Present|[A-Za-z]{3,9}\s+\d{4}|\d{4})", dates)
        if not m:
            continue
        start_s, end_s = m[0]
        start_dt = _parse_date_token(start_s) or None
        end_dt = datetime.now() if re.match(r"(?i)present", end_s) else (_parse_date_token(end_s) or None)
        if start_dt and end_dt and end_dt >= start_dt:
            diff = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
            total_months += max(0, diff)
    years = max(0, round(total_months / 12))

    # Pick top skills (dedup, prioritize ones that match role)
    raw_skills = (data.get("skills") or []) if isinstance(data.get("skills"), list) else []
    seen = set()
    skills: List[str] = []
    for s in raw_skills:
        k = (s or "").strip()
        if not k:
            continue
        low = k.lower()
        if low not in seen:
            seen.add(low)
            skills.append(k)
    role_low = inferred_role.lower()
    skills.sort(key=lambda x: 0 if role_low and role_low.split()[0] in x.lower() else 1)
    top = skills[:8]
    if top:
        if len(top) == 1:
            skills_str = top[0]
        elif len(top) == 2:
            skills_str = f"{top[0]} and {top[1]}"
        else:
            skills_str = ", ".join(top[:-1]) + f", and {top[-1]}"
        skills_sentence = f"Expertise in {skills_str}."
    else:
        skills_sentence = "Expertise across relevant tools and methods."

    # Extract up to two quantified achievements from bullets
    achievements: List[str] = []
    for j in (data.get("experience", []) or []):
        for b in (j.get("responsibilities", []) or []):
            text = str(b).strip()
            if re.search(r"\b(\d+|%|x)\b", text, re.IGNORECASE):
                # Normalize sentence casing
                achievements.append(text.rstrip(". "))
            if len(achievements) >= 2:
                break
        if len(achievements) >= 2:
            break

    ach_sentence = ""
    if achievements:
        if len(achievements) == 1:
            ach_sentence = f" Notable achievement: {achievements[0]}."
        else:
            ach_sentence = f" Notable achievements: {achievements[0]}; {achievements[1]}."

    # Compose summary
    name = (data.get("personal_info", {}).get("name") or "Candidate").strip()
    yrs = f"{years}+ years" if years > 0 else "industry"
    first_clause = f"{inferred_role} with {yrs} of experience."
    return f"{first_clause} {skills_sentence}{ach_sentence}"


def _diff_resume(before: Dict, after: Dict) -> list:
    """Produce a simple list of modifications between two resume dicts."""
    changes = []
    bpi = (before or {}).get("personal_info", {})
    api = (after or {}).get("personal_info", {})
    if bpi.get("summary") != api.get("summary"):
        changes.append("Updated professional summary")

    # Skills changes
    bskills = set((before or {}).get("skills", []) or [])
    askills = set((after or {}).get("skills", []) or [])
    added = list(askills - bskills)
    removed = list(bskills - askills)
    if added:
        changes.append(f"Added skills: {', '.join(sorted(added)[:10])}")
    if removed:
        changes.append(f"Removed duplicate/irrelevant skills: {', '.join(sorted(removed)[:10])}")

    # Experience bullets improved
    bexp = (before or {}).get("experience", []) or []
    aexp = (after or {}).get("experience", []) or []
    if aexp and bexp:
        improved = 0
        for i in range(min(len(bexp), len(aexp))):
            bb = bexp[i].get("responsibilities", []) or []
            ab = aexp[i].get("responsibilities", []) or []
            improved += sum(1 for j in range(min(len(bb), len(ab))) if bb[j] != ab[j])
        if improved:
            changes.append(f"Improved {improved} experience bullet(s)")

    return changes
