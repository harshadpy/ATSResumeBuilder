import os
import json
from typing import Dict

# Optional imports; used only if OPENAI_API_KEY present
try:
    # New SDK (>=1.0)
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore
try:
    # Legacy SDK (<1.0)
    import openai  # type: ignore
except Exception:
    openai = None  # type: ignore


DEFAULT_PROMPT_TEMPLATE = """
You are an expert career coach and resume reviewer. Given the candidate resume data (JSON) and the ATS scoring results,
generate a comprehensive, prioritized set of actionable recommendations to improve the resume for ATS and human reviewers.
Return a JSON object with keys:
- "summary": single-line summary of the main opportunities (string)
- "recommendations": 8-12 items, each object with:
    - "id": short machine-friendly id (kebab-case)
    - "title": short title
    - "detail": specific instruction (1-3 sentences) with examples when helpful
    - "impact_estimate": "low"|"medium"|"high"
    - "category": one of ["keywords","content","formatting","achievements","sections","consistency"]
- "keywords_to_add": 8-20 role-aligned keywords to incorporate
- "fields_changed_suggestion": list of resume fields to edit (e.g., ["summary","experience[].responsibilities","skills"]) 
Assume the target role: {target_role}

Resume JSON:
{resume_json}

ATS JSON:
{ats_json}

Instructions:
- Prioritize by expected ATS & recruiter impact.
- If ATS keyword score is low, include at least 3 keyword-focused items.
- Use clear, ATS-safe language and avoid fluff.
- Output VALID JSON ONLY with the exact keys above; no prose outside JSON.
"""


def _heuristic_recommendations(resume: Dict, ats: Dict, target_role: str = "") -> Dict:
    """Deterministic fallback: simple heuristics to produce suggestions."""
    recs = []
    keywords = []

    keyword_score = (ats or {}).get("keyword_score", 0)
    format_score = (ats or {}).get("format_score", 0)

    summary = (
        "Focus on adding role-specific keywords and quantifiable achievements." if keyword_score < 60
        else "Add quantifiable impact and tweak format for readability."
    )

    if keyword_score < 70:
        recs.append({
            "id": "keywords",
            "title": "Add role-specific keywords",
            "detail": "Compare a target job description and add 6–12 matching keywords into summary, skills, and experience bullets.",
            "impact_estimate": "high"
        })
        keywords = list({str(s).lower() for s in (resume.get("skills", []) or [])})[:10]

    recs.append({
        "id": "quantify",
        "title": "Quantify achievements",
        "detail": "Convert responsibilities into achievement-style bullets using metrics (%, number, time saved).",
        "impact_estimate": "high" if (resume.get("experience") or []) else "medium",
    })

    if format_score < 70:
        recs.append({
            "id": "format",
            "title": "Improve formatting for ATS",
            "detail": "Ensure consistent headings and use plain text bullets. Avoid images, headers/footers for ATS.",
            "impact_estimate": "medium"
        })

    fields = ["experience[].responsibilities", "personal_info.summary", "skills"]
    return {
        "summary": summary,
        "recommendations": recs,
        "keywords_to_add": keywords,
        "fields_changed_suggestion": fields,
        "provider": "fallback"
    }


def generate_recommendations(
    resume: Dict,
    ats: Dict,
    target_role: str = "",
    use_openai: bool = True,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
) -> Dict:
    """
    Generate resume improvement recommendations. Uses OpenAI if OPENAI_API_KEY set and openai is importable.
    Otherwise returns deterministic heuristics.

    Returns a dict with keys: summary, recommendations (list), keywords_to_add (list), fields_changed_suggestion (list).
    """
    resume_json = json.dumps(resume or {}, ensure_ascii=False, indent=2)
    ats_json = json.dumps(ats or {}, ensure_ascii=False, indent=2)

    if not os.getenv("OPENAI_API_KEY") or not use_openai:
        return _heuristic_recommendations(resume or {}, ats or {}, target_role)

    # Allow environment override for model name
    model_to_use = os.getenv("OPENAI_MODEL") or model

    prompt = DEFAULT_PROMPT_TEMPLATE.format(
        target_role=(target_role or "unspecified"),
        resume_json=resume_json,
        ats_json=ats_json,
    )

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        text = None
        # Prefer new client
        if OpenAI is not None:
            # Instantiate without kwargs to avoid environments where Client.__init__ may receive unexpected proxy kwargs
            # Ensure API key is set via environment variable
            if api_key and not os.getenv("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = api_key
            client = OpenAI()

            # 1) Try Responses API with structured JSON schema for reliable parsing
            try:
                schema = {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "detail": {"type": "string"},
                                    "impact_estimate": {"type": "string"},
                                    "category": {"type": "string"}
                                },
                                "required": ["id", "title", "detail", "impact_estimate"]
                            }
                        },
                        "keywords_to_add": {"type": "array", "items": {"type": "string"}},
                        "fields_changed_suggestion": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["summary", "recommendations", "keywords_to_add", "fields_changed_suggestion"]
                }

                r = client.responses.create(
                    model=model_to_use,
                    input=prompt,
                    temperature=0.3,
                    max_output_tokens=max_tokens,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {"name": "ResumeRecommendations", "schema": schema}
                    },
                )
                # Try helper property first, then fallback to manual extraction
                text = getattr(r, "output_text", None)
                if not text:
                    # Manual extraction of first text segment
                    try:
                        outputs = getattr(r, "output", []) or []
                        if outputs:
                            first = outputs[0]
                            content = getattr(first, "content", []) or []
                            if content and getattr(content[0], "type", "") == "output_text":
                                text = getattr(content[0].text, "value", None)
                    except Exception:
                        pass
                if text:
                    text = text.strip()
                else:
                    # If Responses API returned nothing, fall back to chat.completions
                    raise RuntimeError("Empty Responses API output")
            except Exception:
                # 2) Fallback to Chat Completions API
                resp = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": "You are a helpful resume reviewer."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,
                )
                text = (resp.choices[0].message.content or "").strip()
        # Fallback to legacy API
        elif openai is not None:
            openai.api_key = api_key  # type: ignore[attr-defined]
            response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "You are a helpful resume reviewer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            text = response.choices[0].message.content.strip()
        else:
            fb = _heuristic_recommendations(resume or {}, ats or {}, target_role)
            fb["error"] = "OpenAI SDK not available"
            return fb

        try:
            obj = json.loads(text or "{}")
            if isinstance(obj, dict):
                obj.setdefault("provider", "openai")
            return obj
        except Exception:
            import re
            m = re.search(r'(\{.*\})', text, re.DOTALL)
            if m:
                try:
                    obj = json.loads(m.group(1))
                    if isinstance(obj, dict):
                        obj.setdefault("provider", "openai")
                    return obj
                except Exception:
                    pass
            fb = _heuristic_recommendations(resume or {}, ats or {}, target_role)
            fb["error"] = "Invalid JSON from OpenAI response"
            return fb
    except Exception as e:
        fb = _heuristic_recommendations(resume or {}, ats or {}, target_role)
        try:
            fb["error"] = str(e)
        except Exception:
            fb["error"] = "OpenAI call failed"
        return fb
