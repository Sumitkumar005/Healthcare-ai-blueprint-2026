# 04. Pre-Visit Patient Assessment Automation

## 🎯 The Problem

Nurses call patients 24-48 hours before scheduled visits to confirm appointment and ask screening questions. This takes **5-10 minutes per patient** and yields inconsistent documentation.

**Impact**: 
- Saves 5-10 minutes per patient
- Standardized screening
- Early flagging of concerning responses

## 💡 The Solution

Automated conversational interface that asks standardized screening questions, flags concerning responses, and generates pre-visit summaries for providers.

## 🚀 Quick Start

```bash
cd 04-pre-visit-assessment
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
04-pre-visit-assessment/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── assessment_engine.py
│   └── question_generator.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI**: LLM for conversational flow
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS chat interface

## 📊 Features

- Automated screening questions
- Adaptive questioning
- Critical response flagging
- Pre-visit summary generation

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)
