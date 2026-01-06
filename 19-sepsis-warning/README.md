# 19. Sepsis Early Warning System for Nursing Homes

## 🎯 The Problem

Sepsis kills 270,000 Americans annually. Early detection in nursing homes is critical but often missed. Quick SOFA (qSOFA) and SIRS criteria help identify at-risk patients but require consistent monitoring.

**Impact**: 
- Early sepsis detection
- Saves lives
- Reduces ICU admissions

## 💡 The Solution

Routine vital sign entry system that automatically calculates qSOFA and SIRS scores, tracks trends, and alerts for concerning patterns indicating sepsis risk.

## 🚀 Quick Start

```bash
cd 19-sepsis-warning
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
19-sepsis-warning/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── qsofa_calculator.py
│   └── sirs_calculator.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite
- **Analytics**: Time series analysis
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Vital sign entry
- qSOFA score calculation
- SIRS criteria calculation
- Trend analysis
- Alert system

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

