# 🤖 **AI Resume Builder & ATS Optimizer**

### *A State‑of‑the‑Art, Fully Intelligent Resume System *

---

## 🧬 Overview

Welcome to the **Smart Resume Builder** — your intelligent companion for crafting **ATS‑optimized**, cleanly structured, professionally formatted resumes.

Build an ATS-optimized resume with explainable scoring and AI‑powered enhancement.
<p align="center">
  <img width="1729" height="861" alt="image" src="https://github.com/user-attachments/assets/48f4043e-684d-48ad-9fb6-d004117fb6d0" />
</p>


---

## ⭐ Core Feature Summary

### 📤 **Upload or Manual Entry**

* Upload **PDF/DOCX**
* OCR fallback
* Table-aware parsing for structured data

### 📊 **ATS Scoring (Explainable & Deterministic)**

Overall Score Formula:

> **30% Completeness + 40% Keyword Relevance + 30% Formatting/Readability**

#### **Completeness (30 pts)**

* Contact info with email + phone or link → **8 pts**
* Professional summary → **6 pts**
* Skills count ≥ 8 → **6 pts**
* Education section → **5 pts**
* Experience section → **5 pts**

#### **Keyword Relevance (40 pts)**

* Skills richness (distinct, relevant) → **20 pts**
* Skills reused in bullets/summary → **15 pts**
* Role/title signals (Engineer, Senior, Developer) → **5 pts**

#### **Formatting & Readability (30 pts)**

* Strong bullet count → **8 pts**
* Action verbs (Led, Built, Delivered…) → **8 pts**
* Quantified impact → **7 pts**
* Consistent date formatting → **5 pts**
* Links present → **2 pts**

### 🎨 **Distinct Templates**

* **Professional**
* **Modern**
* **Minimal**

Available for both **DOCX** and **PDF**.

### 📥 **One‑Click Export**

* Reliable DOCX generation
* Multi-layer PDF fallback pipeline

### 📈 **Score Tracker**

Track ATS improvement across enhancement steps.

### 💬 **Feedback Chatbot**

Ask targeted questions:

* Improve summary
* Add missing keywords
* Rewrite bullets
* Provide role‑specific suggestions

Attach files for more context.

---

## 🔁 Workflow

1. **Upload / Enter** your data
2. **Score** to get baseline ATS breakdown
3. **Enhance** using AI + recommendations
4. **Compare** before/after improvements
5. **Generate** DOCX / PDF via chosen template
6. **Track** score changes in Score Tracker

---

## 🪜 Guided Steps

### **Step 1 — Upload or Enter Data**

### **Step 2 — AI Enhancement**

### **Step 3 — Download Resume**

---

The **AI Resume Builder & ATS Optimizer** is a fully modern, visually premium, deeply engineered application designed to create **ATS‑friendly, professional, and AI‑enhanced resumes**. Built using **Streamlit**, powered by optional **OpenAI**, styled with **custom gradient UI**, and equipped with a **full resume intelligence pipeline**.

This README is crafted to match the **high‑end UI**, **purple–blue gradient aesthetic**, and **premium feel** of your `style.css`.

---

## ✨ Core Features

### 🔍 **1. Smart Resume Parsing**

* PDF & DOCX support
* OCR fallback
* Table‑aware extraction
* Clean structured JSON output

### 🤖 **2. AI Resume Enhancement**

* Summary rewriting with action verbs
* Bullet expansion + quantification
* Keyword optimization for target roles
* Adjustable enhancement levels:

  * Conservative
  * Moderate
  * Aggressive

### 📊 **3. ATS Scoring Engine**

Includes weighted categories:

* Completeness
* Keyword relevance
* Formatting & readability
* Action verbs & quantification
* Link + date consistency

### 🎨 **4. Professional Resume Generation**

* DOCX generator (python‑docx)
* PDF generator (reportlab)
* Multiple templates: Modern, Minimal, Professional

### 📈 **5. Score Tracker**

* Tracks score change for each enhancement cycle
* Visual charts
* Historical breakdowns

### 💬 **6. Integrated Feedback Chatbot**

* AI suggestions based on current resume
* File drop for context
* OpenAI‑powered when API key available

---

## 🖼️ UI & Aesthetic Highlights

Designed with a **custom premium UI**, featuring:

* Gradient backgrounds
* Smooth animations
* Soft shadows (neumorphism)
* Rounded modern components
* Sidebar with hover interactions
* Animated headers
* Glass-like cards

Every part of UI is intentionally styled to feel like a **SaaS‑level polished product**.

---

## 🏗️ Project Structure

A complete breakdown of how the project is organized.

---

## 📁 **Directory Layout**

```
ai-resume-builder/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── setup.sh                        # Quick setup script
├── .env.example                    # Template for environment variables
├── .env                            # Actual API keys (user-created)
├── .gitignore                      # Git ignore rules
├── Dockerfile                      # Docker configuration (optional)
│
├── README.md                       # Full documentation (this file)
├── QUICKSTART.md                   # Fast usage guide
└── PROJECT_STRUCTURE.md            # Detailed internal structure
│
├── .streamlit/
│   └── config.toml                 # Streamlit UI + theme configuration
│
├── utils/                          # Utility modules
│   ├── __init__.py                 # Makes utils a Python package
│   ├── parser.py                   # Resume parsing engine
│   ├── ats_scorer.py               # ATS engine (API + local fallback)
│   ├── ai_enhancer.py              # AI enhancement (OpenAI + Gemini)
│   ├── template_manager.py         # DOCX/PDF/Latex template system
│   └── file_generator.py           # Document generation
│
└── outputs/                        # Auto-created generated files
    ├── resume.docx
    ├── resume.pdf
    └── resume.tex
```

---

## 📄 **Core Application Files**

### `app.py`

* Manages Streamlit UI
* All pages and navigation
* Session state handlers

**Pages included:**

1. Home – Overview
2. Upload Resume – PDF/DOCX parsing
3. Manual Entry – Build from scratch
4. Enhancement – AI improvement
5. Generate Resume – DOCX/PDF Export
6. Comparison – Before/After analysis
7. Score Tracker – History + charts
8. Feedback Chatbot – AI Q&A

### `requirements.txt`

```
streamlit==1.31.0
PyPDF2==3.0.1
python-docx==1.1.0
openai==1.12.0
google-generativeai==0.3.2
requests==2.31.0
docx2pdf==0.1.8
python-dotenv==1.0.0
```

---

## 🧩 Utility Modules

### `utils/parser.py`

Handles *all* parsing operations.

**Key Functions:**

* `extract_text_from_pdf()`
* `extract_text_from_docx()`
* `parse_resume()` → Converts raw text to structured dict
* Extractors: email, phone, skills, education, experience

---

### `utils/ats_scorer.py`

Handles ATS scoring using:

* External ATS API (if key exists)
* Local algorithm fallback

**Score Weightage:**

* Personal Info: 20
* Skills: 25
* Education: 15
* Experience: 30
* Projects: 10

---

### `utils/ai_enhancer.py`

Enhancement pipeline with priority:
**OpenAI → Gemini → Fallback local enhancer**

**Enhances:**

* Summary
* Skills
* Bullet points
* Experience
* Projects

**Enhancement Levels:**

* Conservative
* Moderate
* Aggressive

---

### `utils/template_manager.py`

Handles resume templates:

* DOCX Templates
* LaTeX Templates
* Formatting helpers for each section

Templates:

1. Professional
2. Modern
3. Minimal

---

### `utils/file_generator.py`

**Responsible for exporting:**

* DOCX
* PDF
* LaTeX-based PDFs
* docx2pdf + LibreOffice fallback

Also cleans up temporary files.

---

## ⚙️ Configuration Files

### `.env.example`

```
OPENAI_API_KEY=
GEMINI_API_KEY=
ATS_API_KEY=
```

### `.streamlit/config.toml`

Controls theme + file upload limits.

### `.gitignore`

Protects:

* Secrets
* Generated files
* Cache directories

---

## ⚒️ Setup Files

### `setup.sh`

Automates:

1. Dependency installation
2. Folder creation
3. Environment initialization
4. `.env` creation prompt

### `Dockerfile`

Builds a portable image with:

* Python 3.11
* LaTeX packages
* Streamlit runtime

---

## 🔄 Application Data Flow

```
Upload → Parse → ATS Score → AI Enhancer → Template → DOCX/PDF → Compare
```

---

## 🔗 API Integration Flow

### For Enhancement

```
OpenAI → Gemini → Fallback
```

### For ATS Scoring

```
ATS API → Local Algorithm
```

---

## 🧠 Session State Variables

* `resume_data`
* `original_score`
* `enhanced_score`
* `enhanced_content`
* `score_history`

---

## 📤 Output Files

Generated to `/outputs/`:

* resume.docx
* resume.pdf
* resume.tex (temporary)

---

## 🔐 Environment Variables

Required:

* `OPENAI_API_KEY`

Optional:

* `GEMINI_API_KEY`
* `ATS_API_KEY`

---

## 📦 Dependency Purpose Table

| Package             | Purpose                |
| ------------------- | ---------------------- |
| streamlit           | UI framework           |
| PyPDF2              | PDF parsing            |
| python-docx         | DOCX creation          |
| openai              | OpenAI API             |
| google-generativeai | Gemini API             |
| requests            | HTTP API calls         |
| docx2pdf            | PDF fallback converter |
| python-dotenv       | Load `.env`            |

---

## ☁️ Deployment Options

### Streamlit Cloud

* Push repo
* Add Secrets
* Deploy

### Render

* Configure Docker/Build
* Add env variables
* Deploy

---

## 🔐 Security Rules

Do **NOT** commit:

* `.env`
* API keys
* Generated user files

---

## 🛠 Customization Points

You can modify:

* Templates
* Scoring
* AI prompts
* UI theme
* Streamlit behavior

---

## 🚀 Performance Optimizations

* Fallback layers
* Minimal API calls
* Smart parsing
* Cached session state

---

## 🧪 Testing Checklist

* [ ] PDF Upload
* [ ] DOCX Upload
* [ ] Manual Entry
* [ ] ATS Score
* [ ] AI Enhance
* [ ] DOCX/PDF Export
* [ ] Template Switching
* [ ] Score Tracker
* [ ] Chatbot

---

This section has now been fully integrated into your README with a **clean, structured, aesthetic, and professional format**.

## 🛠️ Installation

```bash
git clone <your-repo-url>
cd ai-resume-builder
pip install -r requirements.txt
```

### Optional: Add OpenAI API Key

```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

App opens at:

```
http://localhost:8501
```

---

## 🔧 AI Enhancement Examples

### Before:

* Worked on backend APIs.

### After (AI Enhanced):

* Engineered RESTful APIs using Flask, improving system performance by **32%** and supporting **15,000+ monthly users**.

---

## 🔍 ATS Score Breakdown

Your ATS score is calculated using:

* **30%** Completeness
* **40%** Keyword relevance
* **30%** Formatting & readability

Common insights include:

* Missing technical keywords
* Weak bullet structure
* Lack of quantification
* Inconsistent date formats
* Missing links (GitHub/LinkedIn)

---

## 🌟 Why This Project Stands Out

* Full resume intelligence pipeline: input → parse → enhance → score → export
* Modern premium UI (unusual for Streamlit apps)
* Dual‑engine AI (OpenAI + deterministic fallback)
* Production‑ready architecture
* Competitive portfolio / internship project

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome! Templates, improvements, bug fixes — everything helps.

---

## 👨‍💻 Author

**HarshadPy** — AI + Software Developer
Building next‑gen intelligent tools.

---

## ⭐ Additional Add‑Ons Available

(You can ask and I’ll add them to this README inside the canvas!)

* Dark mode version
* SaaS‑level feature cards
* Animated banners
* Architecture diagram
* GIF demo
* Badge collection
* Deployment section

---
