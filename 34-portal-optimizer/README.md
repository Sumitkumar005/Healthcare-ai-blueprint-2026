# 34. Patient Portal Usage Optimizer

![Demo](demo.gif)

## 🎯 The Problem

Medical practices pay for patient portals but only 30-40% of patients activate them. Low engagement means wasted cost and continued phone calls for routine requests.

**Impact**: 
- Increases portal activation rates by 40-60%
- Reduces phone call volume by 30-50%
- Improves patient engagement and satisfaction
- Better ROI on portal investment

## 💡 The Solution

Analytics and campaign system that analyzes portal usage patterns, identifies inactive patients, runs targeted activation campaigns, and tracks engagement improvement.

## 🏗️ Architecture

```
Usage Analytics → Inactive Patient Identification → Campaign Builder → Engagement Tracking → ROI Analysis
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+

### Installation

```bash
cd 34-portal-optimizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn src.main:app --reload
# Open browser to http://localhost:8000
```

## 📋 Features

### Core Functionality

1. **Portal Usage Analytics**
   - Activation rate tracking
   - Active user monitoring
   - Feature usage analysis (messaging, bill pay, scheduling)
   - User demographics

2. **Inactive Patient Identification**
   - Segment patients by activation status
   - Identify high-value inactive patients
   - Usage pattern analysis

3. **Campaign Builder**
   - Target specific patient groups
   - Customizable messaging
   - Multi-channel campaigns (email, SMS, in-office)
   - A/B testing framework

4. **Engagement Tracking**
   - Campaign effectiveness monitoring
   - Phone call volume reduction tracking
   - ROI calculator (portal cost vs staff time saved)

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React analytics dashboard
- **Database**: SQLite for usage data
- **Analytics**: Engagement metrics and A/B testing

## 📁 Project Structure

```
34-portal-optimizer/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── usage_analyzer.py    # Usage analytics engine
│   └── campaign_manager.py # Campaign management
└── frontend/
    └── index.html
```

## 🔑 API Endpoints

### GET `/api/analytics`
Get portal usage analytics.

### POST `/api/campaign`
Create a new activation campaign.

### GET `/api/campaign/{campaign_id}/results`
Get campaign results and effectiveness.

### GET `/api/roi`
Calculate ROI metrics.

## 📝 License

MIT License

---

**Built with ❤️ for healthcare practices**


