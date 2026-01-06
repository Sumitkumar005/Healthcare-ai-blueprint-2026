# 08. Automated Patient No-Show Follow-Up

## 🎯 The Problem

Staff manually call no-shows to reschedule, taking 5-10 minutes per occurrence. High-volume practices have **10-20 no-shows daily**, consuming hours of staff time.

**Impact**: 
- Saves 2-3 hours daily for high-volume practices
- Improves rescheduling rates
- Reduces revenue loss from missed appointments

## 💡 The Solution

An automated system that detects no-shows, sends follow-up messages, captures rescheduling preferences, and logs all interactions. Includes analytics dashboard for no-show patterns.

## 🏗️ Architecture

```
No-Show Detection → Automated Message → Patient Response → Rescheduling → Analytics
```

## 🚀 Quick Start

```bash
cd 08-patient-no-show-followup
pip install -r requirements.txt
python src/main.py
# Open http://localhost:8000
```

## 📁 Project Structure

```
08-patient-no-show-followup/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── database.py
│   └── messaging.py
├── tests/
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite
- **Frontend**: HTML/CSS/JS
- **Analytics**: Chart.js

## 📊 Features

- Automated no-show detection
- Follow-up messaging (simulated)
- Rescheduling interface
- No-show analytics dashboard
- Interaction logging

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)


