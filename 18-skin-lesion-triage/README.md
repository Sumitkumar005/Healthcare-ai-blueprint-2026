# 18. Skin Lesion Triage Assistant

## 🎯 The Problem

Primary care providers are flooded with mole and skin lesion checks. Many specialist dermatology referrals are unnecessary, while some concerning lesions get delayed. Need triage tool for prioritization.

**Impact**: 
- Reduces unnecessary referrals
- Prioritizes urgent cases
- Saves specialist time

## 💡 The Solution

Photo upload system that assesses ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution), calculates risk score, and provides triage recommendations (urgent, routine, reassurance).

## 🚀 Quick Start

```bash
cd 18-skin-lesion-triage
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
18-skin-lesion-triage/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── abcde_analyzer.py
│   └── triage_engine.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI Vision**: Hugging Face CLIP / GPT-4 Vision
- **Image Processing**: OpenCV
- **Frontend**: React
- **Database**: SQLite

## 📊 Features

- Photo upload with size reference
- ABCDE criteria assessment
- Risk score calculation
- Triage recommendation
- Referral letter generation
- Lesion tracking over time

## ⚠️ Important Disclaimer

**This is a clinical decision support tool, NOT a diagnostic tool.** Always consult with a dermatologist for definitive diagnosis.

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

