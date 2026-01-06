# 07. Meeting Notes to SOAP Note Converter

## 🎯 The Problem

Multidisciplinary team meetings discuss patient cases. Someone takes meeting notes, then each clinician has to write their own SOAP note. **Massive duplication of effort** - the same information gets rewritten multiple times in different formats.

**Impact**: 
- Saves 30-45 minutes per meeting per clinician
- Ensures consistency across disciplines
- Reduces documentation errors

## 💡 The Solution

An AI-powered tool that converts meeting notes or transcripts into discipline-specific SOAP notes. Simply paste meeting notes, and the system automatically extracts patient information and generates SOAP notes for nursing, physical therapy, occupational therapy, social work, and other disciplines.

## 🏗️ Architecture

```
Meeting Notes → AI Parser → Patient Extraction → Discipline-Specific SOAP Generation → Export
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free API key from Groq or OpenRouter

### Installation

```bash
cd 07-meeting-notes-to-soap
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API key to .env
```

### Usage

```bash
python src/main.py
# Open http://localhost:8000
```

## 📁 Project Structure

```
07-meeting-notes-to-soap/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py
│   ├── soap_generator.py
│   └── patient_extractor.py
├── tests/
└── examples/
```

## 🛠️ Tech Stack

- **AI/ML**: Groq/OpenRouter LLM
- **Backend**: FastAPI
- **Frontend**: HTML/CSS/JS

## 📊 Example

**Input (Meeting Notes):**
```
Patient: John Doe, 65M, admitted for hip replacement
PT: Patient ambulating with walker, needs strengthening
Nursing: Wound healing well, pain controlled
OT: ADL assessment pending
```

**Output (SOAP Notes):**
- **Nursing SOAP**: Subjective, Objective, Assessment, Plan sections
- **PT SOAP**: Mobility-focused assessment
- **OT SOAP**: Activities of daily living focus

## 🔒 Privacy & Security

Never use real patient data without HIPAA compliance.

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)


