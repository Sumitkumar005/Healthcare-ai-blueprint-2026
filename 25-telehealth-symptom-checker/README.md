# 25. Telehealth Pre-Visit Symptom Checker

![Demo](demo.gif)

## 🎯 The Problem

First 5-10 minutes of telehealth visits are wasted on extracting basic history. Patients are unprepared and visits run inefficiently. Need structured pre-visit data collection to optimize visit time and improve documentation quality.

**Impact**: 
- Saves 5-10 minutes per telehealth visit
- Improves visit efficiency and patient satisfaction
- Better documentation with structured HPI
- Early detection of red flag symptoms

## 💡 The Solution

An AI-powered pre-visit symptom questionnaire that collects structured patient history before telehealth appointments. The system uses adaptive questioning based on chief complaint, detects red flag symptoms, and generates a comprehensive HPI summary for providers.

## 🏗️ Architecture

```
Patient Questionnaire → Adaptive AI Questions → Red Flag Detection → HPI Summary → Provider Dashboard
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free API key from Groq or OpenRouter

### Installation

```bash
# Navigate to project directory
cd 25-telehealth-symptom-checker

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

### Running the Application

```bash
# Start the FastAPI server
uvicorn src.main:app --reload

# Open browser to http://localhost:8000
```

## 📋 Features

### Core Functionality

1. **Pre-Visit Questionnaire**
   - Chief complaint capture
   - Symptom onset and duration
   - Associated symptoms
   - Severity scale (1-10)
   - Aggravating/alleviating factors
   - Current medications and allergies
   - Relevant medical history

2. **Adaptive Questioning**
   - AI-powered follow-up questions based on chief complaint
   - Context-aware question flow
   - Personalized to patient's specific condition

3. **Red Flag Detection**
   - Automatic detection of concerning symptoms
   - Immediate alerts for urgent cases
   - Provider notification system

4. **HPI Summary Generation**
   - Structured History of Present Illness
   - Professional medical documentation format
   - Ready for chart integration

5. **Provider Dashboard**
   - View all pre-visit summaries
   - Filter by appointment date/time
   - Red flag alerts highlighted
   - Export summaries for documentation

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **AI**: Groq/OpenRouter LLM for adaptive questioning and summary generation
- **Database**: SQLite for patient responses
- **Alerts**: Email notification system (simulated)

## 📁 Project Structure

```
25-telehealth-symptom-checker/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── questionnaire_engine.py  # Adaptive questioning logic
│   └── hpi_generator.py     # HPI summary generation
├── frontend/
│   ├── index.html
│   ├── questionnaire.js
│   └── styles.css
└── tests/
    └── test_questionnaire.py
```

## 🔑 API Endpoints

### POST `/api/questionnaire/start`
Start a new questionnaire session.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "appointment_id": "A67890",
  "chief_complaint": "Chest pain"
}
```

**Response:**
```json
{
  "session_id": "session_abc123",
  "questions": ["When did the chest pain start?"]
}
```

### POST `/api/questionnaire/answer`
Submit answer to current question.

**Request Body:**
```json
{
  "session_id": "session_abc123",
  "question_id": "q1",
  "answer": "Started 2 hours ago"
}
```

### GET `/api/questionnaire/summary/{session_id}`
Get generated HPI summary for a session.

### GET `/api/provider/dashboard`
Get all pre-visit summaries for provider review.

## 🎨 Usage Example

1. **Patient receives pre-visit invitation** (24 hours before appointment)
2. **Patient completes questionnaire** with adaptive questions
3. **System detects red flags** and alerts provider if needed
4. **HPI summary generated** automatically
5. **Provider reviews summary** before visit starts
6. **Visit time optimized** - provider has full context upfront

## ⚠️ Important Notes

- **Not a diagnostic tool** - This is a documentation and efficiency tool
- **Red flags require immediate clinical review** - System alerts but doesn't replace clinical judgment
- **HIPAA Compliance** - All patient data should be encrypted in transit and at rest
- **Production Deployment** - Add authentication, encryption, and audit logging

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 📝 License

MIT License - See LICENSE file in repository root.

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md in repository root.

---

**Built with ❤️ for healthcare providers**



