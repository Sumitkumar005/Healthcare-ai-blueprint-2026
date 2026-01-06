# 01. Voice-to-Clinical-Note Converter for Home Care Nurses

## 🎯 The Problem

Independent nurses (home health aides) see 15-20 patients daily. Each visit requires transmission notes for the care team. Nurses record voice memos in their car between patients but spend **2-3 hours every evening typing them up**.

**Impact**: 
- Saves 2-3 hours daily per nurse
- Faster documentation turnaround
- More accurate, structured notes

## 💡 The Solution

Web-based voice recording system that transcribes audio to text using AI, then automatically formats into professional nursing transmission note structure. Supports multiple note templates (visit notes, wound care, medication administration).

## 🏗️ Architecture

```
Voice Recording → Whisper Transcription → LLM Structuring → Clinical Note → Export
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free API key from Groq (for Whisper and LLM)

### Installation

```bash
cd 01-voice-to-clinical-note
pip install -r requirements.txt
cp .env.example .env
# Add GROQ_API_KEY to .env
python src/main.py
# Open http://localhost:8000
```

## 📁 Project Structure

```
01-voice-to-clinical-note/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py
│   ├── transcriber.py
│   └── note_generator.py
├── frontend/
│   └── index.html
└── templates/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI Transcription**: Groq Whisper API (free)
- **AI Structuring**: Groq/OpenRouter LLM
- **Frontend**: HTML/CSS/JS with MediaRecorder API
- **Storage**: In-memory session storage

## 🎥 Demo

1. Click "Start Recording"
2. Speak your clinical note (max 5 minutes)
3. Click "Stop Recording"
4. System transcribes and structures the note
5. Review and edit if needed
6. Export as text or download

## 📊 Example Output

**Voice Input**: "Patient John Doe, visited today at 2 PM. Blood pressure 130 over 80, heart rate 72. Patient reports feeling better. Wound healing well. Changed dressing. Patient tolerated well. Plan to continue current care plan."

**Structured Output**:
```
PATIENT NAME: John Doe
VISIT DATE/TIME: [Current Date] 2:00 PM

VITAL SIGNS:
- Blood Pressure: 130/80
- Heart Rate: 72 bpm

ASSESSMENT:
Patient reports feeling better. Wound healing well.

CARE PROVIDED:
Changed dressing.

PATIENT RESPONSE:
Patient tolerated well.

PLAN:
Continue current care plan.

NURSE SIGNATURE: [Your Name]
```

## 🔒 Privacy & Security

- Audio is processed server-side and not stored permanently
- Notes are stored in browser session only
- Never use real patient data without HIPAA compliance

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

