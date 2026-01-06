# 02. Wound Photo Documentation with Auto-Classification

## 🎯 The Problem

Chronic wound care requires photo documentation at every visit to track healing progress. Nurses take photos on personal phones, manually describe wound type, size, condition in notes. Zero standardization, photos get lost, can't track trends.

**Impact**: 
- Standardized wound documentation
- Progress tracking over time
- Better wound care outcomes

## 💡 The Solution

Mobile-responsive photo capture interface with AI-powered wound classification, size measurement, standardized description generation, and progress tracking over time.

## 🚀 Quick Start

```bash
cd 02-wound-photo-documentation
pip install -r requirements.txt
python src/main.py
```

## 📁 Project Structure

```
02-wound-photo-documentation/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── wound_classifier.py
│   ├── size_measurement.py
│   └── description_generator.py
└── frontend/
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI Vision**: Hugging Face CLIP / GPT-4 Vision
- **Image Processing**: OpenCV
- **Frontend**: React
- **Storage**: IndexedDB (browser)

## 📊 Features

- Photo capture/upload
- Wound type classification
- Size measurement
- Standardized SOAP descriptions
- Progress tracking
- Comparison view

## 📄 License

MIT License - see main repository [LICENSE](../LICENSE)

---

[← Back to Projects](../README.md#-project-list)

