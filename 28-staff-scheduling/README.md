# 28. Staff Scheduling Optimizer for Nursing Units

## 🎯 The Problem

Nurse managers spend 5-10 hours weekly creating schedules manually. Must balance nurse-to-patient ratios, certifications, preferences, and minimize overtime costs.

**Impact**: 
- Saves 5-10 hours per week
- Optimizes nurse-to-patient ratios
- Minimizes overtime costs
- Respects staff preferences

## 💡 The Solution

Constraint-based optimization system that generates optimal nursing schedules balancing ratios, certifications, preferences, and costs.

## 🚀 Quick Start

```bash
cd 28-staff-scheduling
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## 📁 Project Structure

```
28-staff-scheduling/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── scheduler.py
│   └── optimizer.py
└── frontend/
```

## 📄 License

MIT License

