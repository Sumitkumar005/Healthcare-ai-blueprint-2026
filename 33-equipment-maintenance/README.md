# 33. Medical Equipment Maintenance Tracker

![Demo](demo.gif)

## 🎯 The Problem

Smaller facilities track equipment calibration and maintenance manually on paper or spreadsheets. High risk of missing required maintenance leading to safety issues and regulatory violations.

**Impact**: 
- Prevents missed maintenance schedules
- Automated alerts for upcoming maintenance
- Compliance reporting for inspections
- Reduces safety risks and regulatory violations

## 💡 The Solution

Comprehensive equipment inventory and maintenance tracking system with automated scheduling, alerts, and compliance reporting.

## 🏗️ Architecture

```
Equipment Inventory → Maintenance Scheduling → Automated Alerts → Compliance Reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+

### Installation

```bash
# Navigate to project directory
cd 33-equipment-maintenance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the FastAPI server
uvicorn src.main:app --reload

# Open browser to http://localhost:8000
```

## 📋 Features

### Core Functionality

1. **Equipment Inventory**
   - Equipment type, serial number, location
   - Purchase date and maintenance frequency
   - Service provider assignment

2. **Maintenance Scheduling**
   - Automatic scheduling based on frequency
   - Work order generation
   - Service history tracking

3. **Automated Alerts**
   - 30-day, 14-day, 7-day warnings
   - Overdue notifications
   - Email/dashboard alerts

4. **Compliance Reporting**
   - List of all equipment due for maintenance
   - Overdue items tracking
   - Complete maintenance history
   - Export for inspections

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Alerts**: Email notification system (simulated)
- **Export**: PDF compliance reports

## 📁 Project Structure

```
33-equipment-maintenance/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── equipment_manager.py # Equipment inventory management
│   └── maintenance_scheduler.py  # Maintenance scheduling logic
└── frontend/
    └── index.html
```

## 🔑 API Endpoints

### POST `/api/equipment`
Add new equipment to inventory.

### GET `/api/equipment`
Get all equipment with maintenance status.

### POST `/api/maintenance`
Log maintenance completion.

### GET `/api/alerts`
Get upcoming and overdue maintenance alerts.

### GET `/api/compliance-report`
Generate compliance report.

## 📝 License

MIT License - See LICENSE file in repository root.

---

**Built with ❤️ for healthcare facilities**


