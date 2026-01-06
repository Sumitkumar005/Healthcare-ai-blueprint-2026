# 06. Insurance Prior Authorization Auto-Generator

![Demo](demo.gif)

## 🎯 The Problem

Certain treatments require insurance prior authorization. Clinicians spend hours filling out forms and writing medical justification. **30-40% get denied first time** due to incomplete documentation, requiring resubmission and delaying patient care.

**Impact**: 
- Saves 2-3 hours per prior auth request
- Reduces denial rates from 30-40% to <10%
- Faster patient access to needed treatments

## 💡 The Solution

An AI-powered tool that generates comprehensive prior authorization requests with evidence-based medical justification. Simply input patient information, diagnosis, and proposed treatment, and the system generates a complete, properly formatted prior auth request ready for submission.

## 🏗️ Architecture

```
User Input (Form) → FastAPI Backend → LLM (Medical Justification) → PDF Generator → Download
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free API key from Groq or OpenRouter

### Installation

```bash
# Navigate to project directory
cd 06-insurance-prior-authorization

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API key:
# GROQ_API_KEY=your_key_here
# or
# OPENROUTER_API_KEY=your_key_here
```

### Usage

```bash
# Start the backend server
python src/main.py

# Open your browser to http://localhost:8000
# Fill out the form and generate your prior auth request
```

## 📁 Project Structure

```
06-insurance-prior-authorization/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── src/
│   ├── main.py           # FastAPI application entry point
│   ├── generator.py      # Prior auth generation logic
│   └── pdf_generator.py  # PDF creation utilities
├── templates/
│   └── prior_auth.html   # Jinja2 template for prior auth
├── tests/
│   └── test_generator.py # Unit tests
└── examples/
    └── sample_output.pdf # Example generated prior auth
```

## 🛠️ Tech Stack

- **AI/ML**: Groq/OpenRouter LLM for medical justification
- **Backend**: FastAPI
- **Frontend**: HTML/CSS/JS (vanilla)
- **PDF Generation**: ReportLab
- **Templates**: Jinja2

## 🎥 Demo

1. Fill out patient demographics
2. Enter diagnosis codes (ICD-10)
3. Specify treatment requested (CPT codes)
4. Add clinical notes/rationale
5. Click "Generate Prior Auth"
6. Review and download PDF

## 📊 Example Output

**Input:**
- Patient: 65-year-old with Type 2 Diabetes
- Diagnosis: Diabetic neuropathy (E11.40)
- Treatment: Physical therapy (97110)
- Clinical Notes: Patient reports severe foot pain affecting daily activities

**Output:**
- Complete prior auth form with:
  - Medical necessity justification
  - Evidence-based reasoning
  - Supporting documentation
  - Properly formatted for insurance submission

## 🧪 Testing

```bash
# Run tests
pytest tests/
```

## 🔒 Privacy & Security

**Important**: 
- This tool uses synthetic/mock data for examples
- Never use real patient data without proper HIPAA compliance
- Implement authentication before production use
- Encrypt sensitive data in transit and at rest

## 📚 Learn More

- [ICD-10 Code Lookup](https://www.icd10data.com/)
- [CPT Code Lookup](https://www.ama-assn.org/amaone/cpt-current-procedural-terminology)
- [Prior Authorization Best Practices](https://www.cms.gov/)

## 🤝 Contributing

See main repository [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)


