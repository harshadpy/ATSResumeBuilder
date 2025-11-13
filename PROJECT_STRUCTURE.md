# Complete Project Structure

## Directory Layout

```
ai-resume-builder/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── setup.sh                        # Quick setup script
├── .env.example                    # Environment variables template
├── .env                           # Your actual API keys (create this)
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker configuration (optional)
│
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick start guide
└── PROJECT_STRUCTURE.md           # This file
│
├── .streamlit/
│   └── config.toml               # Streamlit configuration
│
├── utils/                        # Utility modules package
│   ├── __init__.py              # Package initializer
│   ├── parser.py                # Resume parsing logic
│   ├── ats_scorer.py            # ATS scoring (with API fallback)
│   ├── ai_enhancer.py           # AI enhancement (OpenAI + Gemini)
│   ├── template_manager.py      # Template management
│   └── file_generator.py        # Document generation (DOCX/PDF)
│
└── outputs/                      # Generated files (auto-created)
    ├── resume.docx
    ├── resume.pdf
    └── resume.tex
```

## File Descriptions

### Core Application Files

#### `app.py`
- Main Streamlit application
- Multi-page interface
- Session state management
- User interaction handling

**Pages:**
1. Home - Welcome and overview
2. Upload Resume - Parse existing resumes
3. Manual Entry - Enter details from scratch
4. Enhancement - AI-powered optimization
5. Generate Resume - Export to DOCX/PDF
6. Comparison - Before/after analysis

#### `requirements.txt`
```
streamlit==1.31.0           # Web framework
PyPDF2==3.0.1              # PDF parsing
python-docx==1.1.0         # DOCX handling
openai==1.12.0             # OpenAI API
google-generativeai==0.3.2  # Gemini API
requests==2.31.0           # HTTP requests
docx2pdf==0.1.8           # PDF conversion
python-dotenv==1.0.0       # Environment variables
```

### Utility Modules

#### `utils/parser.py`
**Functions:**
- `extract_text_from_pdf(file)` - Extract text from PDF
- `extract_text_from_docx(file)` - Extract text from Word
- `parse_resume(text)` - Parse text into structured data
- `extract_email(text)` - Find email addresses
- `extract_phone(text)` - Find phone numbers
- `extract_skills(text)` - Identify skills
- `extract_education(text)` - Parse education
- `extract_experience(text)` - Parse work history

**Returns:** Structured dictionary with all resume components

#### `utils/ats_scorer.py`
**Functions:**
- `calculate_ats_score(resume_data)` - Main scoring function
- `calculate_ats_score_api(resume_data)` - External API scoring
- `calculate_ats_score_local(resume_data)` - Local algorithm

**Scoring Criteria:**
- Personal Info: 20 points
- Skills: 25 points
- Education: 15 points
- Experience: 30 points
- Projects: 10 points

**Priority:** ATS API → Local Algorithm (fallback)

#### `utils/ai_enhancer.py`
**Functions:**
- `enhance_resume_content(data, role, level)` - Main enhancement
- `enhance_with_openai(content, context)` - OpenAI enhancement
- `enhance_with_gemini(content, context)` - Gemini enhancement
- `enhance_summary(summary, role, level)` - Optimize summary
- `enhance_experience_bullet(bullet, role)` - Improve bullets
- `enhance_skills(skills, role)` - Optimize skills list
- `generate_resume_summary(data, role)` - Generate summary

**Priority:** OpenAI → Gemini (fallback)

**Enhancement Levels:**
- Conservative: Minimal changes
- Moderate: Balanced optimization
- Aggressive: Maximum enhancement

#### `utils/template_manager.py`
**Functions:**
- `get_available_templates()` - List templates
- `apply_template(data, template_id)` - Apply template
- `get_template_latex(template_id)` - Get LaTeX code
- `format_contact_info(personal_info)` - Format contact
- `format_experience_latex(experience)` - Format experience
- `format_education_latex(education)` - Format education
- `format_skills_latex(skills)` - Format skills
- `format_projects_latex(projects)` - Format projects

**Templates:**
1. Professional - Traditional, clean
2. Modern - Contemporary styling
3. Minimal - Compact, content-focused

#### `utils/file_generator.py`
**Functions:**
- `generate_docx(data, template)` - Create Word document
- `generate_pdf(data, template)` - Create PDF
- `generate_pdf_latex(data, template)` - PDF via LaTeX
- `generate_pdf_from_docx(data, template)` - PDF via conversion
- `cleanup_temp_files()` - Clean temporary files

**Generation Priority:**
- LaTeX → docx2pdf → LibreOffice

### Configuration Files

#### `.env.example`
Template for environment variables:
```bash
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ATS_API_KEY=optional_key_here
```

#### `.streamlit/config.toml`
Streamlit appearance and behavior settings:
- Theme colors
- Upload limits
- Server configuration

#### `.gitignore`
Excludes from version control:
- `.env` (secrets)
- `outputs/` (generated files)
- `__pycache__/` (Python cache)
- Virtual environments

### Setup Files

#### `setup.sh`
Automated setup script:
1. Creates directories
2. Installs dependencies
3. Initializes package
4. Creates .env from template

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

#### `Dockerfile`
Optional Docker container setup:
- Python 3.11 base
- LaTeX installation
- Streamlit configuration
- Port 8501 exposure

**Usage:**
```bash
docker build -t resume-builder .
docker run -p 8501:8501 resume-builder
```

## Data Flow

```
1. Input (Upload/Manual)
   ↓
2. Parse Resume
   ↓
3. Calculate ATS Score (API/Local)
   ↓
4. AI Enhancement (OpenAI/Gemini)
   ↓
5. Apply Template
   ↓
6. Generate Document (DOCX/PDF)
   ↓
7. Download & Compare
```

## API Integration Flow

### AI Enhancement
```
User Request
   ↓
Check OPENAI_API_KEY
   ↓
Try OpenAI GPT-4o-mini
   ↓ (if fails)
Try Gemini Pro
   ↓ (if both fail)
Return original content
```

### ATS Scoring
```
Resume Data
   ↓
Check ATS_API_KEY
   ↓
Try External ATS API
   ↓ (if not available/fails)
Use Local Algorithm
   ↓
Return Score & Suggestions
```

## Session State Management

Streamlit session state variables:
- `resume_data` - Current resume information
- `original_score` - Initial ATS score
- `enhanced_score` - Post-enhancement score
- `enhanced_content` - AI-enhanced resume data

## Output Files

Generated in `outputs/` directory:

1. **resume.docx** - Word document
2. **resume.pdf** - PDF document
3. **resume.tex** - LaTeX source (temporary)
4. **resume.aux, .log** - LaTeX temp files (auto-cleaned)

## Environment Variables

Required:
- `OPENAI_API_KEY` - For AI enhancement

Optional:
- `GEMINI_API_KEY` - Fallback enhancement
- `ATS_API_KEY` - External ATS scoring

## Dependencies Explanation

| Package | Purpose |
|---------|---------|
| streamlit | Web framework |
| PyPDF2 | PDF text extraction |
| python-docx | Word document handling |
| openai | OpenAI API integration |
| google-generativeai | Gemini API integration |
| requests | HTTP requests for APIs |
| docx2pdf | PDF conversion fallback |
| python-dotenv | Environment variable management |

## Deployment Structure

### Streamlit Cloud
```
Repository
   ↓
streamlit.io dashboard
   ↓
Add secrets (API keys)
   ↓
Deploy automatically
```

### Render
```
Repository
   ↓
render.com dashboard
   ↓
Configure build/start commands
   ↓
Add environment variables
   ↓
Deploy
```

## Security Considerations

✅ **Secure:**
- API keys in `.env` (not committed)
- `.gitignore` protects secrets
- No hardcoded credentials

❌ **Never commit:**
- `.env` file
- API keys
- User uploaded files
- Generated resumes

## Customization Points

Want to customize? Edit these:

1. **Templates** - `utils/template_manager.py`
2. **Scoring Logic** - `utils/ats_scorer.py`
3. **AI Prompts** - `utils/ai_enhancer.py`
4. **UI/UX** - `app.py`
5. **Theme** - `.streamlit/config.toml`

## Performance Optimization

- Minimal API calls (only when needed)
- Session state caching
- Efficient parsing algorithms
- Async-ready structure
- Smart fallback mechanisms

## Testing Checklist

- [ ] Upload PDF resume
- [ ] Upload DOCX resume
- [ ] Manual data entry
- [ ] ATS scoring
- [ ] AI enhancement
- [ ] DOCX generation
- [ ] PDF generation
- [ ] Template switching
- [ ] Comparison view
- [ ] API fallbacks

---

**Now you have a complete understanding of the project structure! 🎉**