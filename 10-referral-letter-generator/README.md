# 10. Referral Letter Auto-Generator

## 🎯 The Problem

Writing referral letters takes 15-30 minutes per patient. Delays occur when referrals are backlogged. Most letters follow similar format but require customization.

**Impact**: 
- Saves 15-30 minutes per referral
- Ensures consistent, professional format
- Faster specialist access for patients

## 💡 The Solution

AI-powered referral letter generator with specialty-specific templates. Simply input patient information and referral reason, and generate professional referral letters ready for submission.

## 🚀 Quick Start

```bash
cd 10-referral-letter-generator
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
10-referral-letter-generator/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   └── letter_generator.py
└── templates/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI**: Groq/OpenRouter LLM
- **PDF**: ReportLab
- **Templates**: Jinja2

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)


