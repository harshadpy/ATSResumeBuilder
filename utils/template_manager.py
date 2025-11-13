from typing import Dict, List


def get_available_templates() -> Dict[str, Dict]:
    return {
        "professional": {
            "name": "Professional",
            "description": "Traditional, clean layout",
            "latex_path": "templates/resume_template.tex",
        },
        "modern": {
            "name": "Modern",
            "description": "Contemporary with bold headings",
            "latex_path": "templates/modern_resume.tex",
        },
        "minimal": {
            "name": "Minimal",
            "description": "Compact and content-focused",
            "latex_path": "templates/minimal_resume.tex",
        },
    }


def get_template_latex(template_id: str) -> str:
    templates = get_available_templates()
    info = templates.get(template_id) or next(iter(templates.values()))
    return info.get("latex_path", "templates/resume_template.tex")


def apply_template(data: Dict, template_id: str) -> Dict:
    """For now this is a pass-through; formatting is handled in generators."""
    return data


def format_contact_info(personal_info: Dict) -> str:
    parts = []
    for key in ["email", "phone", "linkedin", "github", "website", "location"]:
        val = personal_info.get(key)
        if val:
            parts.append(str(val))
    return " | ".join(parts)


def format_experience_latex(experience: List[Dict]) -> str:
    lines = []
    for job in experience:
        title = job.get("title", "")
        company = job.get("company", "")
        dates = job.get("dates", "")
        lines.append(
            f"\\textbf{{{latex_escape(title)}}} \\hfill {latex_escape(dates)}\\\n"
            f"{latex_escape(company)}\\\n\\begin{{itemize}}"
        )
        for b in job.get("responsibilities", []) or []:
            lines.append(f"  \\item {latex_escape(b)}")
        lines.append("\\end{itemize}")
    return "\n".join(lines)


def format_education_latex(education: List[str]) -> str:
    if not education:
        return ""
    lines = ["\\begin{itemize}"]
    for e in education:
        lines.append(f"  \\item {latex_escape(e)}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def format_skills_latex(skills: List[str]) -> str:
    return ", ".join(latex_escape(s) for s in (skills or []))


def format_projects_latex(projects: List[Dict]) -> str:
    if not projects:
        return ""
    lines = ["\\begin{itemize}"]
    for p in projects:
        name = p.get("name", "Project")
        desc = p.get("description", "")
        tech = p.get("technologies", "")
        body = f"\\textbf{{{latex_escape(name)}}}: {latex_escape(desc)}"
        if tech:
            body += f" (Tech: {latex_escape(tech)})"
        lines.append(f"  \\item {body}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def latex_escape(text: str) -> str:
    if not text:
        return ""
    rep = {
        "\\": r"\\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = []
    for ch in str(text):
        out.append(rep.get(ch, ch))
    return "".join(out)
