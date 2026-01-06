# 20. Antibiotic Stewardship Decision Support

## 🎯 The Problem

Overuse of broad-spectrum antibiotics drives antimicrobial resistance. Clinicians need guidance to choose narrow-spectrum antibiotics when appropriate, but lack time to research local resistance patterns.

**Impact**: 
- Reduces antibiotic resistance
- Better patient outcomes
- Cost savings

## 💡 The Solution

AI-powered decision support tool that recommends appropriate antibiotics based on infection site, patient factors, severity, and local resistance patterns.

## 🚀 Quick Start

```bash
cd 20-antibiotic-stewardship
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
20-antibiotic-stewardship/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── recommendation_engine.py
│   └── guidelines_db.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI**: LLM for recommendations
- **Database**: SQLite for resistance patterns
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Infection site selection
- Patient factor consideration
- Severity assessment
- Narrow-spectrum recommendations
- Dosing guidance
- Rationale explanation

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

