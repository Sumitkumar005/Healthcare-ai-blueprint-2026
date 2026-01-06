# 03. Medication Reconciliation Assistant for Hospital Discharge

## 🎯 The Problem

When patients leave hospital, someone needs to reconcile home medications with new hospital prescriptions. Nurses spend **30-45 minutes per patient** doing this manually, checking for interactions, duplicate therapies, discontinued medications. High error rate, massive time sink.

**Impact**: 
- Saves 30-45 minutes per discharge
- Reduces medication errors
- Prevents adverse drug interactions

## 💡 The Solution

AI-powered medication reconciliation tool that extracts medications from photos/lists, identifies conflicts, duplications, and interactions, then generates a clean reconciled medication list ready for discharge.

## 🚀 Quick Start

```bash
cd 03-medication-reconciliation
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
03-medication-reconciliation/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── ocr_extractor.py
│   ├── medication_parser.py
│   └── reconciliation_engine.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **OCR**: Tesseract OCR
- **AI**: LLM for parsing and analysis
- **Drug Database**: OpenFDA API / RxNorm
- **Frontend**: HTML/CSS/JS

## 📊 Features

- Upload medication lists (PDF/image)
- OCR extraction
- Automatic conflict detection
- Drug interaction checking
- Duplicate identification
- Reconciled list generation

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)
