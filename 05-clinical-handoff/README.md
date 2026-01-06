# 05. Clinical Handoff Summarizer for Shift Changes

## 🎯 The Problem

Every shift change, outgoing nurses brief incoming nurses on each patient's status. Takes **30-60 minutes**, information gets lost. Usually done verbally with scattered notes.

**Impact**: 
- Saves 30-60 minutes per shift change
- Ensures complete information transfer
- Reduces medical errors

## 💡 The Solution

Voice recording system that captures shift updates, transcribes them, organizes by patient, highlights critical information, and generates structured handoff reports.

## 🚀 Quick Start

```bash
cd 05-clinical-handoff
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
05-clinical-handoff/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── transcriber.py
│   └── handoff_generator.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI**: Whisper for transcription, LLM for structuring
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Voice recording for shift updates
- Automatic transcription
- Patient organization
- Critical item highlighting
- Structured handoff reports

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)
