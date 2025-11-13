import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

# Load environment variables from .env (robust to working directory)
load_dotenv(find_dotenv(), override=False)

# Page config
st.set_page_config(
    page_title="AI Resume Builder & ATS Optimizer",
    page_icon="📄",
    layout="wide"
)

#with open('style.css') as f:
    #st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {}
if 'original_score' not in st.session_state:
    st.session_state.original_score = None
if 'enhanced_score' not in st.session_state:
    st.session_state.enhanced_score = None
if 'enhanced_content' not in st.session_state:
    st.session_state.enhanced_content = None
if 'score_history' not in st.session_state:
    st.session_state.score_history = []
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""
if 'reset_chat_input' not in st.session_state:
    st.session_state.reset_chat_input = False

# Import modules
from utils.parser import parse_resume, extract_text_from_pdf, extract_text_from_docx
from utils.ats_scorer import calculate_ats_score
from utils.ai_enhancer import enhance_resume_content
from utils.template_manager import get_available_templates, apply_template
from utils.file_generator import generate_docx, generate_pdf
from utils.openai_recommender import generate_recommendations

# Sidebar
st.sidebar.title("📄 AI Resume Builder")
st.sidebar.markdown("---")

# Show OpenAI API detection status
_openai_present = bool(os.getenv("OPENAI_API_KEY"))
status_msg = "OpenAI API: detected" if _openai_present else "OpenAI API: not detected"
status_fn = st.sidebar.success if _openai_present else st.sidebar.warning
status_fn(status_msg)
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Upload Resume", "Manual Entry", "Enhancement", "Generate Resume", "Comparison", "Score Tracker", "Feedback Chatbot"]
)

# Main content
if page == "Home":
    st.title("🚀 AI-Powered Resume Builder & ATS Optimizer")
    st.markdown("""
    ### Welcome to the Smart Resume Builder!
    
    Build an **ATS-optimized resume** with explainable scoring and professional formatting.
    
    #### Features
    - 📤 **Upload or Manual Entry** — Parse PDF/DOCX with OCR fallback and table-aware parsing.
    - 📊 **ATS Scoring** — Deterministic rubric for Completeness, Keywords, and Format with detailed breakdowns.
    - 🤖 **AI Enhancement** — Improves summary, bullets, and skills (OpenAI when available; safe fallbacks otherwise).
    - 🎨 **Distinct Templates** — Professional, Modern, and Minimal styles for DOCX and PDF.
    - 📥 **One‑click Export** — Generate Word (.docx) and PDF (multiple fallbacks) reliably.
    - 📈 **Score Tracker** — Track ATS score changes after each enhancement.
    - 💬 **Feedback Chatbot** — Ask for targeted improvements and keyword advice; attach files for context.
    
    #### Workflow
    1) **Upload/Enter** your data
    2) **Score** to get a baseline + breakdown
    3) **Enhance** content with AI and suggestions
    4) **Compare** improvements and iterate
    5) **Generate** DOCX/PDF using your chosen template
    6) **Track** improvements over time in Score Tracker
    
    👈 Select a page from the sidebar to begin.
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1**\n\nUpload or Enter Data")
    with col2:
        st.success("**Step 2**\n\nAI Enhancement")
    with col3:
        st.warning("**Step 3**\n\nDownload Resume")

elif page == "Upload Resume":
    st.title("📤 Upload Your Resume")
    st.markdown("Upload your existing resume in PDF or Word format for analysis and enhancement.")
    
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx'],
        help="Upload a PDF or Word document"
    )
    
    if uploaded_file:
        with st.spinner("Parsing your resume..."):
            try:
                # Extract text based on file type
                if uploaded_file.name.endswith('.pdf'):
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)
                
                # Parse the resume
                resume_data = parse_resume(text)
                st.session_state.resume_data = resume_data
                
                st.success("✅ Resume parsed successfully!")
                
                # Display parsed data
                st.subheader("Extracted Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if resume_data.get('personal_info'):
                        st.markdown("**Personal Information**")
                        st.json(resume_data['personal_info'])
                    
                    if resume_data.get('skills'):
                        st.markdown("**Skills**")
                        st.write(", ".join(resume_data['skills']))
                
                with col2:
                    if resume_data.get('education'):
                        st.markdown("**Education**")
                        for edu in resume_data['education']:
                            st.write(f"- {edu}")
                    
                    if resume_data.get('experience'):
                        st.markdown("**Experience**")
                        st.write(f"{len(resume_data['experience'])} positions found")
                
                # Calculate initial ATS score
                if st.button("📊 Calculate ATS Score", type="primary"):
                    with st.spinner("Calculating ATS score..."):
                        score_data = calculate_ats_score(resume_data)
                        st.session_state.original_score = score_data
                        st.session_state.score_history.append({
                            "label": "baseline",
                            "overall": score_data['score'],
                            "keywords": score_data['keyword_score'],
                            "format": score_data['format_score'],
                            "breakdown": score_data.get('breakdown', {}),
                        })
                        
                        st.subheader("ATS Score Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Score", f"{score_data['score']}/100")
                        with col2:
                            st.metric("Keyword Match", f"{score_data['keyword_score']}/100")
                        with col3:
                            st.metric("Format Score", f"{score_data['format_score']}/100")
                        
                        if score_data.get('suggestions'):
                            st.markdown("**Improvement Suggestions:**")
                            for suggestion in score_data['suggestions']:
                                st.write(f"- {suggestion}")
                        
                        st.info("💡 Proceed to the Enhancement page to improve your resume!")
                
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")

elif page == "Manual Entry":
    st.title("✍️ Enter Resume Details Manually")
    st.markdown("Fill in your details below to create a resume from scratch.")
    
    with st.form("resume_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email*", placeholder="john.doe@email.com")
            phone = st.text_input("Phone", placeholder="+1 234 567 8900")
        with col2:
            linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/johndoe")
            github = st.text_input("GitHub", placeholder="github.com/johndoe")
            website = st.text_input("Website", placeholder="johndoe.com")
        
        location = st.text_input("Location", placeholder="San Francisco, CA")
        summary = st.text_area("Professional Summary", placeholder="Brief overview of your professional background...", height=100)
        
        st.subheader("Education")
        num_education = st.number_input("Number of education entries", min_value=1, max_value=5, value=1)
        education_entries = []
        for i in range(num_education):
            with st.expander(f"Education {i+1}"):
                degree = st.text_input(f"Degree/Certification {i+1}", key=f"degree_{i}")
                institution = st.text_input(f"Institution {i+1}", key=f"institution_{i}")
                edu_dates = st.text_input(f"Dates {i+1}", placeholder="2018 - 2022", key=f"edu_dates_{i}")
                gpa = st.text_input(f"GPA (optional) {i+1}", key=f"gpa_{i}")
                if degree and institution:
                    education_entries.append({
                        "degree": degree,
                        "institution": institution,
                        "dates": edu_dates,
                        "gpa": gpa
                    })
        
        st.subheader("Skills")
        skills = st.text_area(
            "Skills (comma-separated)",
            placeholder="Python, Machine Learning, Data Analysis, SQL, TensorFlow",
            height=100
        )
        
        st.subheader("Work Experience")
        num_experience = st.number_input("Number of work experiences", min_value=1, max_value=10, value=2)
        experience_entries = []
        for i in range(num_experience):
            with st.expander(f"Experience {i+1}"):
                job_title = st.text_input(f"Job Title {i+1}", key=f"job_title_{i}")
                company = st.text_input(f"Company {i+1}", key=f"company_{i}")
                exp_dates = st.text_input(f"Dates {i+1}", placeholder="Jan 2022 - Present", key=f"exp_dates_{i}")
                responsibilities = st.text_area(
                    f"Responsibilities & Achievements {i+1}",
                    placeholder="- Led team of 5 developers\n- Increased efficiency by 40%",
                    key=f"responsibilities_{i}",
                    height=150
                )
                if job_title and company:
                    experience_entries.append({
                        "title": job_title,
                        "company": company,
                        "dates": exp_dates,
                        "responsibilities": responsibilities.split('\n') if responsibilities else []
                    })
        
        st.subheader("Projects")
        num_projects = st.number_input("Number of projects", min_value=0, max_value=10, value=2)
        project_entries = []
        for i in range(num_projects):
            with st.expander(f"Project {i+1}"):
                project_name = st.text_input(f"Project Name {i+1}", key=f"project_name_{i}")
                project_desc = st.text_area(
                    f"Description {i+1}",
                    placeholder="Brief description of the project and your role",
                    key=f"project_desc_{i}",
                    height=100
                )
                project_tech = st.text_input(f"Technologies Used {i+1}", key=f"project_tech_{i}")
                if project_name:
                    project_entries.append({
                        "name": project_name,
                        "description": project_desc,
                        "technologies": project_tech
                    })
        
        submitted = st.form_submit_button("💾 Save Resume Data", type="primary")
        
        if submitted:
            if not name or not email:
                st.error("Please fill in required fields (Name and Email)")
            else:
                resume_data = {
                    "personal_info": {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "linkedin": linkedin,
                        "github": github,
                        "website": website,
                        "location": location,
                        "summary": summary
                    },
                    "education": education_entries,
                    "skills": [s.strip() for s in skills.split(',') if s.strip()],
                    "experience": experience_entries,
                    "projects": project_entries
                }
                
                st.session_state.resume_data = resume_data
                st.success("✅ Resume data saved successfully!")

        # End form

    # Calculate initial ATS score (outside the form)
    if st.session_state.resume_data:
        if st.button("📊 Calculate ATS Score"):
            with st.spinner("Calculating ATS score..."):
                score_data = calculate_ats_score(st.session_state.resume_data)
                st.session_state.original_score = score_data
                st.session_state.score_history.append({
                    "label": "baseline",
                    "overall": score_data['score'],
                    "keywords": score_data['keyword_score'],
                    "format": score_data['format_score'],
                    "breakdown": score_data.get('breakdown', {}),
                })
                
                st.subheader("ATS Score Analysis")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Score", f"{score_data['score']}/100")
                with col2:
                    st.metric("Keyword Match", f"{score_data['keyword_score']}/100")
                with col3:
                    st.metric("Format Score", f"{score_data['format_score']}/100")

elif page == "Enhancement":
    st.title("🤖 AI Enhancement")
    
    if not st.session_state.resume_data:
        st.warning("⚠️ Please upload a resume or enter details manually first!")
    else:
        st.markdown("Enhance your resume content using AI for better ATS compatibility and professional presentation.")
        
        # Show current data
        with st.expander("📋 Current Resume Data"):
            st.json(st.session_state.resume_data)
        
        if st.session_state.original_score:
            st.info(f"Current ATS Score: **{st.session_state.original_score['score']}/100**")
        
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.text_input(
                "Target Job Role (optional)",
                placeholder="Software Engineer, Data Scientist, etc.",
                help="Helps AI optimize keywords for specific role"
            )
        with col2:
            enhancement_level = st.select_slider(
                "Enhancement Level",
                options=["Conservative", "Moderate", "Aggressive"],
                value="Moderate"
            )
        
        if st.button("✨ Enhance with AI", type="primary"):
            with st.spinner("AI is enhancing your resume... This may take a moment."):
                try:
                    enhanced_data, modifications = enhance_resume_content(
                        st.session_state.resume_data,
                        target_role=target_role,
                        enhancement_level=enhancement_level.lower()
                    )
                    
                    st.session_state.enhanced_content = enhanced_data
                    st.session_state["modifications"] = modifications
                    
                    # Recalculate ATS score
                    enhanced_score = calculate_ats_score(enhanced_data)
                    st.session_state.enhanced_score = enhanced_score
                    st.session_state.score_history.append({
                        "label": "enhanced",
                        "overall": enhanced_score['score'],
                        "keywords": enhanced_score['keyword_score'],
                        "format": enhanced_score['format_score'],
                        "breakdown": enhanced_score.get('breakdown', {}),
                    })

                    # Generate AI recommendations (OpenAI if key present, else deterministic)
                    recs = generate_recommendations(
                        st.session_state.enhanced_content or st.session_state.resume_data,
                        st.session_state.enhanced_score or st.session_state.original_score,
                        target_role=target_role or ""
                    )
                    st.session_state.recommendations = recs
                    
                    st.success("✅ Enhancement complete!")
                    
                    # Show improvement
                    col1, col2, col3 = st.columns(3)
                    
                    if st.session_state.original_score:
                        original = st.session_state.original_score['score']
                        enhanced = enhanced_score['score']
                        improvement = enhanced - original
                        
                        with col1:
                            st.metric("Original Score", f"{original}/100")
                        with col2:
                            st.metric("Enhanced Score", f"{enhanced}/100", delta=f"+{improvement}")
                        with col3:
                            improvement_pct = (improvement / original * 100) if original > 0 else 0
                            st.metric("Improvement", f"{improvement_pct:.1f}%")
                    
                    # Show enhanced content preview
                    st.subheader("Enhanced Content Preview")
                    
                    personal = enhanced_data.get('personal_info', {}) or {}
                    skills = enhanced_data.get('skills', []) or []
                    education = enhanced_data.get('education', []) or []
                    experience = enhanced_data.get('experience', []) or []
                    projects = enhanced_data.get('projects', []) or []

                    # Summary
                    if personal.get('summary'):
                        st.markdown("**Enhanced Professional Summary:**")
                        st.info(personal['summary'])

                    # Contact + Skills
                    colA, colB = st.columns(2)
                    with colA:
                        contact_parts = []
                        for k in ["email", "phone", "linkedin", "github", "website", "location"]:
                            v = personal.get(k)
                            if v:
                                contact_parts.append(str(v))
                        if contact_parts:
                            st.markdown("**Contact:**")
                            st.write(" | ".join(contact_parts))
                    with colB:
                        if skills:
                            st.markdown("**Skills:**")
                            st.write(" ".join([f"`{s}`" for s in skills]))

                    # Education
                    if education:
                        st.markdown("---")
                        st.markdown("**Education:**")
                        for e in education:
                            st.markdown(f"- {e}")

                    # Experience
                    if experience:
                        st.markdown("---")
                        st.markdown("**Experience:**")
                        for job in experience:
                            jt = job.get('title', '')
                            co = job.get('company', '')
                            dt = job.get('dates', '')
                            header = f"{jt} — {co} ({dt})".strip()
                            st.markdown(f"- **{header}**")
                            for b in job.get('responsibilities', []) or []:
                                st.markdown(f"  - {b}")

                    # Projects
                    if projects:
                        st.markdown("---")
                        st.markdown("**Projects:**")
                        for p in projects:
                            name = p.get('name', 'Project')
                            desc = p.get('description', '')
                            tech = p.get('technologies', '')
                            line = f"**{name}**"
                            if tech:
                                line += f" ({tech})"
                            st.markdown(f"- {line}")
                            if desc:
                                st.markdown(f"  - {desc}")
                    
                    # Show AI recommendations inline
                    if st.session_state.get("recommendations"):
                        st.markdown("---")
                        recs = st.session_state.recommendations
                        provider = recs.get("provider", "fallback")
                        st.subheader(f"🔍 AI Recommendations  ·  source: {provider}")
                        st.markdown(f"**Summary:** {recs.get('summary','')} ")
                        with st.expander("Show detailed suggestions", expanded=True):
                            for r in recs.get("recommendations", []):
                                st.markdown(f"- **{r.get('title','')}** — {r.get('detail','')} _(impact: {r.get('impact_estimate','')}, category: {r.get('category','n/a')})_")
                        if recs.get("keywords_to_add"):
                            st.markdown("**Keywords to consider adding:**")
                            st.write(", ".join(recs["keywords_to_add"]))
                        if provider == "fallback":
                            if recs.get("error"):
                                st.warning(f"OpenAI error: {recs.get('error')}")
                            st.info("No OpenAI API key detected or API unavailable. Showing deterministic fallback recommendations.")

                    st.info("💡 Proceed to 'Generate Resume' to create your final document!")
                    
                except Exception as e:
                    st.error(f"Enhancement error: {str(e)}")

elif page == "Generate Resume":
    st.title("📥 Generate Your Resume")
    
    if not st.session_state.enhanced_content and not st.session_state.resume_data:
        st.warning("⚠️ Please complete the enhancement step first!")
    else:
        content_to_use = st.session_state.enhanced_content or st.session_state.resume_data
        
        st.markdown("Choose a template and generate your professional resume.")
        
        # Template selection
        st.subheader("Choose Template")
        templates = get_available_templates()
        
        cols = st.columns(len(templates))
        selected_template = None
        
        for idx, (template_id, template_info) in enumerate(templates.items()):
            with cols[idx]:
                st.markdown(f"**{template_info['name']}**")
                st.caption(template_info['description'])
                if st.button(f"Select", key=f"template_{template_id}"):
                    selected_template = template_id
        
        if not selected_template and templates:
            selected_template = list(templates.keys())[0]
            st.info(f"Using default template: {templates[selected_template]['name']}")
        
        # Generate button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Generate Word (.docx)", type="primary"):
                with st.spinner("Generating Word document..."):
                    try:
                        docx_path = generate_docx(content_to_use, selected_template)
                        
                        with open(docx_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Word Resume",
                                data=file,
                                file_name="resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        st.success("✅ Word document generated!")
                    except Exception as e:
                        st.error(f"Error generating Word document: {str(e)}")
        
        with col2:
            if st.button("📕 Generate PDF", type="primary"):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_path = generate_pdf(content_to_use, selected_template)
                        
                        with open(pdf_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download PDF Resume",
                                data=file,
                                file_name="resume.pdf",
                                mime="application/pdf"
                            )
                        st.success("✅ PDF generated!")
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
        
        # Show final score
        if st.session_state.enhanced_score:
            st.markdown("---")
            st.subheader("Final ATS Score")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall", f"{st.session_state.enhanced_score['score']}/100")
            with col2:
                st.metric("Keywords", f"{st.session_state.enhanced_score['keyword_score']}/100")
            with col3:
                st.metric("Format", f"{st.session_state.enhanced_score['format_score']}/100")

elif page == "Comparison":
    st.title("📊 Before & After Comparison")
    
    if not st.session_state.original_score or not st.session_state.enhanced_score:
        st.warning("⚠️ Complete the enhancement process to see comparison!")
        if st.session_state.resume_data:
            st.info("You can run the missing steps from here.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📊 Compute Baseline ATS", use_container_width=True):
                    with st.spinner("Calculating ATS score..."):
                        st.session_state.original_score = calculate_ats_score(st.session_state.resume_data)
                        st.success("Baseline ATS score computed.")
                        st.session_state.score_history.append({
                            "label": "baseline",
                            "overall": st.session_state.original_score['score'],
                            "keywords": st.session_state.original_score['keyword_score'],
                            "format": st.session_state.original_score['format_score'],
                            "breakdown": st.session_state.original_score.get('breakdown', {}),
                        })
            with c2:
                if st.button("✨ Run Enhancement Now", use_container_width=True):
                    with st.spinner("Enhancing and rescoring..."):
                        enhanced_data, modifications = enhance_resume_content(
                            st.session_state.resume_data,
                            target_role="",
                            enhancement_level="moderate"
                        )
                        st.session_state.enhanced_content = enhanced_data
                        st.session_state["modifications"] = modifications
                        st.session_state.enhanced_score = calculate_ats_score(enhanced_data)
                        # Best-effort recommendations
                        recs = generate_recommendations(
                            enhanced_data,
                            st.session_state.enhanced_score or {},
                            target_role=""
                        )
                        st.session_state.recommendations = recs
                        st.success("Enhancement complete.")
                        st.session_state.score_history.append({
                            "label": "enhanced",
                            "overall": st.session_state.enhanced_score['score'],
                            "keywords": st.session_state.enhanced_score['keyword_score'],
                            "format": st.session_state.enhanced_score['format_score'],
                            "breakdown": st.session_state.enhanced_score.get('breakdown', {}),
                        })
        else:
            st.info("Please upload or enter your resume data first.")
    
    # If we now have both scores, render the comparison
    if st.session_state.original_score and st.session_state.enhanced_score:
        st.markdown("Compare your original resume with the AI-enhanced version.")
        
        # Score comparison
        st.subheader("Score Improvement")
        col1, col2, col3 = st.columns(3)
        
        original = st.session_state.original_score
        enhanced = st.session_state.enhanced_score
        
        with col1:
            st.metric(
                "Overall Score",
                f"{enhanced['score']}/100",
                delta=f"+{enhanced['score'] - original['score']}"
            )
        with col2:
            st.metric(
                "Keyword Score",
                f"{enhanced['keyword_score']}/100",
                delta=f"+{enhanced['keyword_score'] - original['keyword_score']}"
            )
        with col3:
            st.metric(
                "Format Score",
                f"{enhanced['format_score']}/100",
                delta=f"+{enhanced['format_score'] - original['format_score']}"
            )
        
        # Content comparison
        st.subheader("Content Comparison")

        orig = st.session_state.resume_data or {}
        enh = st.session_state.enhanced_content or {}
        recs = st.session_state.get("recommendations", {})
        rec_list = recs.get("recommendations", []) or []

        def show_section(title, render_original, section_key):
            st.markdown("---")
            st.markdown(f"#### {title}")
            st.markdown("**Original**")
            render_original()
            # Inline AI suggestions for this section
            if rec_list:
                section_suggestions = []
                for r in rec_list:
                    cat = (r.get('category') or '').lower()
                    txt = (r.get('detail') or '') + ' ' + (r.get('title') or '')
                    if section_key == 'summary' and ('content' in cat or 'sections' in cat or 'keywords' in cat):
                        section_suggestions.append(r)
                    elif section_key == 'skills' and ('keywords' in cat or 'content' in cat):
                        section_suggestions.append(r)
                    elif section_key == 'education' and ('sections' in cat or 'consistency' in cat):
                        section_suggestions.append(r)
                    elif section_key == 'experience' and ('achievements' in cat or 'content' in cat):
                        section_suggestions.append(r)
                    elif section_key == 'projects' and ('content' in cat or 'sections' in cat):
                        section_suggestions.append(r)
                if section_suggestions:
                    with st.expander("AI suggestions for this section", expanded=True):
                        for r in section_suggestions:
                            st.markdown(f"- **{r.get('title','')}** — {r.get('detail','')} _(impact: {r.get('impact_estimate','')})_")

        # Summary
        def _orig_summary():
            s = (orig.get('personal_info', {}) or {}).get('summary', '')
            st.text_area("Summary", s, height=120, disabled=True, key="orig_sum")

        show_section("Summary", _orig_summary, 'summary')

        # Skills
        def _orig_skills():
            skills = orig.get('skills', []) or []
            st.write(" ".join([f"`{s}`" for s in skills]) or "—")

        show_section("Skills", _orig_skills, 'skills')

        # Education
        def _orig_edu():
            edu = orig.get('education', []) or []
            for e in edu: st.markdown(f"- {e}")
            if not edu: st.write("—")

        show_section("Education", _orig_edu, 'education')

        # Experience
        def _render_jobs(data):
            jobs = data.get('experience', []) or []
            if not jobs:
                st.write("—")
                return
            for j in jobs:
                header = f"{j.get('title','')} — {j.get('company','')} ({j.get('dates','')})".strip()
                st.markdown(f"- **{header}**")
                for b in j.get('responsibilities', []) or []:
                    st.markdown(f"  - {b}")

        show_section("Experience", lambda: _render_jobs(orig), 'experience')

        # Projects
        def _render_projects(data):
            items = data.get('projects', []) or []
            if not items:
                st.write("—")
                return
            for p in items:
                name = p.get('name','Project')
                tech = p.get('technologies','')
                desc = p.get('description','')
                line = f"**{name}**"
                if tech: line += f" ({tech})"
                st.markdown(f"- {line}")
                if desc: st.markdown(f"  - {desc}")

        show_section("Projects", lambda: _render_projects(orig), 'projects')
        
        # Suggestions and modifications
        st.subheader("Improvements Made")

        if st.session_state.get("modifications"):
            st.markdown("**Changes Applied:**")
            for item in st.session_state["modifications"]:
                st.write(f"✅ {item}")

        if original.get('suggestions'):
            st.markdown("**Issues Addressed:**")
            for suggestion in original['suggestions']:
                st.write(f"🛠️ {suggestion}")

        # AI recommendations (if available)
        if st.session_state.get("recommendations"):
            st.markdown("---")
            recs = st.session_state.recommendations
            provider = recs.get("provider", "fallback")
            st.subheader(f"🔍 AI Recommendations  ·  source: {provider}")
            st.markdown(f"**Summary:** {recs.get('summary','')}")
            with st.expander("Show detailed suggestions", expanded=True):
                for r in recs.get("recommendations", []):
                    st.markdown(f"- **{r.get('title','')}** — {r.get('detail','')} _(impact: {r.get('impact_estimate','')}, category: {r.get('category','n/a')})_")
            if recs.get("keywords_to_add"):
                st.markdown("**Keywords to consider adding:**")
                st.write(", ".join(recs["keywords_to_add"]))
            if provider == "fallback":
                if recs.get("error"):
                    st.warning(f"OpenAI error: {recs.get('error')}")
                st.info("No OpenAI API key detected or API unavailable. Showing deterministic fallback recommendations.")

# Feedback Chatbot
elif page == "Feedback Chatbot":
    st.title("💬 Feedback Chatbot")
    st.caption("Ask questions about your resume, ATS score, or how to improve specific sections. You can also drop a file for context.")
    # If flagged, clear input before widget is created
    if st.session_state.get("reset_chat_input"):
        st.session_state.chat_input = ""
        st.session_state.reset_chat_input = False

    # Quick chips
    def _set_chat_input_val(v: str):
        st.session_state.chat_input = v
    chips = [
        "How can I improve my professional summary?",
        "Which keywords am I missing for a Data Scientist role?",
        "Rewrite my last job bullets to be more impact-driven.",
        "Suggest better formatting for ATS.",
    ]
    cc1, cc2, cc3, cc4 = st.columns(4)
    for i, (col, txt) in enumerate(zip([cc1, cc2, cc3, cc4], chips)):
        with col:
            st.button(txt, key=f"chip_{i}", on_click=_set_chat_input_val, args=(txt,))

    # File upload
    up = st.file_uploader("Attach resume (optional)", type=["pdf", "docx"], accept_multiple_files=False)
    attached_text = ""
    if up:
        try:
            if up.name.lower().endswith(".pdf"):
                from utils.parser import extract_text_from_pdf
                attached_text = extract_text_from_pdf(up)
            else:
                from utils.parser import extract_text_from_docx
                attached_text = extract_text_from_docx(up)
            st.success("File content loaded for context")
        except Exception as e:
            st.warning(f"Could not read file: {e}")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input
    user_msg_widget = st.text_area("Your message", key="chat_input", height=100, placeholder="Type your question or paste a section of your resume...")

    if st.button("Send", type="primary"):
        user_msg = (st.session_state.get("chat_input", "") or "").strip()
        if user_msg or attached_text:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

        # Compose context
        ctx = []
        if st.session_state.get("enhanced_content"):
            ctx.append("Enhanced resume JSON:\n" + str(st.session_state.enhanced_content))
        elif st.session_state.get("resume_data"):
            ctx.append("Resume JSON:\n" + str(st.session_state.resume_data))
        if attached_text:
            ctx.append("Attached file text:\n" + attached_text[:6000])
        ctx_text = "\n\n".join(ctx)

        answer = None
        if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            try:
                client = OpenAI()
                system = "You are a helpful, precise resume coach. Give concise, actionable feedback with examples when useful."
                prompt = f"Context (may be partial):\n{ctx_text}\n\nUser: {user_msg}"
                try:
                    r = client.responses.create(
                        model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
                        input=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.3,
                        max_output_tokens=600,
                    )
                    answer = getattr(r, "output_text", None)
                except Exception:
                    # Fallback to chat.completions
                    cr = client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.3,
                        max_tokens=600,
                    )
                    answer = (cr.choices[0].message.content or "").strip()
            except Exception as e:
                answer = f"OpenAI error: {e}"
        else:
            answer = "OpenAI API key not detected. Please set OPENAI_API_KEY to use the chatbot."

        st.session_state.chat_history.append({"role": "assistant", "content": answer or ""})
        # Clear input on next run to avoid Streamlit widget-state mutation error
        st.session_state.reset_chat_input = True
        st.rerun()

    # Render chat history
    for m in st.session_state.chat_history[-12:]:
        if m["role"] == "user":
            st.markdown(f"**You:** {m['content']}")
        else:
            st.markdown(f"**Assistant:** {m['content']}")

# Score Tracker
elif page == "Score Tracker":
    st.title("📈 Score Improvement Tracker")
    st.caption("Track how your ATS scores evolve over enhancements.")
    # Explain how scoring is computed
    st.markdown("### How scoring works")
    with st.expander("View scoring rubric", expanded=False):
        st.markdown(
            """
            - **Overall score** = 30% Completeness + 40% Keyword Relevance + 30% Formatting/Readability.
            - **Completeness (30 pts)**
              - Has contact details with email and either phone or a link (LinkedIn/GitHub) (up to 8 pts)
              - Professional summary present (6 pts)
              - Sufficient skills listed (target ≥ 8) (6 pts)
              - Education section present (5 pts)
              - Experience section present (5 pts)
            - **Keyword Relevance (40 pts)**
              - Skills richness: more distinct, relevant skills → up to 20 pts
              - Reuse of those skills/keywords in summary and bullets → up to 15 pts
              - Role/title signals (e.g., Engineer, Senior) → up to 5 pts
            - **Formatting/Readability (30 pts)**
              - Adequate number of strong bullet points in experience → up to 8 pts
              - Use of action verbs (Led, Built, Optimized, Delivered, etc.) → up to 8 pts
              - Quantified impact (numbers, %, x) → up to 7 pts
              - Consistent dates across roles → up to 5 pts
              - Links present (LinkedIn/GitHub) → up to 2 pts
            """
        )
    hist = st.session_state.get("score_history", [])
    if not hist:
        st.info("No scores yet. Compute a baseline or run an enhancement.")
    else:
        labels = [h.get("label","step") for h in hist]
        overall = [h.get("overall",0) for h in hist]
        keywords = [h.get("keywords",0) for h in hist]
        fmt = [h.get("format",0) for h in hist]
        st.bar_chart({"Overall": overall, "Keywords": keywords, "Format": fmt})
        st.markdown("### History")
        for i, h in enumerate(hist, 1):
            st.write(f"{i}. {h.get('label','step')} — Overall {h.get('overall')} | Keywords {h.get('keywords')} | Format {h.get('format')}")
            with st.expander("Show breakdown", expanded=False):
                bd = h.get('breakdown') or {}
                if not bd:
                    # Try to compute a representative breakdown for this step
                    data_src = None
                    if (h.get('label') == 'baseline') and st.session_state.get('resume_data'):
                        data_src = st.session_state.resume_data
                    elif (h.get('label') == 'enhanced') and st.session_state.get('enhanced_content'):
                        data_src = st.session_state.enhanced_content
                    if data_src:
                        try:
                            from utils.ats_scorer import calculate_ats_score
                            tmp = calculate_ats_score(data_src)
                            bd = tmp.get('breakdown', {}) or {}
                        except Exception as _:
                            bd = {}
                if bd:
                    st.json(bd)
                else:
                    st.caption("No breakdown available for this historical entry.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "AI-Powered Resume Builder uses advanced AI to create ATS-optimized resumes. "
    "Powered by OpenAI and Gemini APIs."
)