# 12. Lab Results Explainer for Patients

## 🎯 The Problem

Patients receive lab results they don't understand, panic-Google symptoms, and clog clinic phone lines with calls. Need plain-language explanations with appropriate context.

**Impact**: 
- Reduces patient anxiety
- Fewer unnecessary calls
- Better patient education

## 💡 The Solution

AI-powered tool that parses lab results, generates plain-language explanations, highlights abnormal values with context, and suggests questions for provider discussion.

## 🚀 Quick Start

```bash
cd 12-lab-results-explainer
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
12-lab-results-explainer/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── lab_parser.py
│   └── explanation_generator.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **OCR**: For PDF lab results
- **AI**: LLM for explanations
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Upload lab results (PDF/image)
- Extract lab values
- Plain-language explanations
- Abnormal value highlighting
- Question suggestions

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

