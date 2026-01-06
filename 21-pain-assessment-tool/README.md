# 21. Pain Assessment Tool for Non-Verbal Patients

## 🎯 The Problem

Patients with dementia or cognitive impairment can't self-report pain. PAINAD (Pain Assessment in Advanced Dementia) scale is subjective and inconsistently applied. Need structured assessment with trending.

**Impact**: 
- Improves pain detection in non-verbal patients
- Enables trend tracking over time
- Better pain management outcomes

## 💡 The Solution

Digital PAINAD scale assessment tool with automatic score calculation, trend tracking, and intervention correlation.

## 🚀 Quick Start

```bash
cd 21-pain-assessment-tool
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
21-pain-assessment-tool/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   └── painad_scale.py
└── database/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Digital PAINAD assessment (5 categories, 0-2 each)
- Automatic score calculation (0-10)
- Pain level interpretation
- Trend tracking
- Intervention correlation

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

