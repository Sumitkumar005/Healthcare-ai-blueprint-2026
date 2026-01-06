# 17. Drug Interaction Checker for Polypharmacy Patients

## 🎯 The Problem

Elderly patients often take 10+ medications. Checking for interactions manually is slow and error-prone for field nurses who lack access to comprehensive drug databases.

**Impact**: 
- Prevents adverse drug interactions
- Saves time for nurses
- Improves patient safety

## 💡 The Solution

Medication list input (photo OCR or manual entry) that cross-references against drug interaction database, provides severity ratings, and explains interactions in plain language.

## 🚀 Quick Start

```bash
cd 17-drug-interaction-checker
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
17-drug-interaction-checker/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── medication_extractor.py
│   └── interaction_checker.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **OCR**: Tesseract for medication labels
- **Drug Database**: RxNorm/OpenFDA API
- **AI**: LLM for plain-language explanations
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Photo or manual medication entry
- Automatic interaction checking
- Severity ratings (minor, moderate, severe)
- Plain-language explanations
- Offline capability

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

