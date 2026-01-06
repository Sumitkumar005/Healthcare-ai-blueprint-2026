"""
Chronic Disease Self-Management Coach.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .checkin_engine import CheckInEngine
from .trend_analyzer import TrendAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "chronic_disease.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Chronic Disease Coach", version="1.0.0")
checkin_engine = CheckInEngine()
trend_analyzer = TrendAnalyzer()


class CheckInRequest(BaseModel):
    patient_name: str
    disease_type: str  # diabetes, chf, copd
    data: dict  # Disease-specific data


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chronic Disease Coach</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Chronic Disease Self-Management Coach</h1>
        <form id="checkinForm">
            <div class="form-group">
                <label>Disease Type:</label>
                <select name="disease_type" required>
                    <option value="diabetes">Diabetes</option>
                    <option value="chf">Heart Failure (CHF)</option>
                    <option value="copd">COPD</option>
                </select>
            </div>
            <div id="diseaseFields"></div>
            <button type="submit">Submit Check-In</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('checkinForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                const response = await fetch('/checkin', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({patient_name: 'John Doe', disease_type: data.disease_type, data: data})
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/checkin")
async def submit_checkin(request: CheckInRequest):
    """Submit daily check-in."""
    result = checkin_engine.process_checkin(request.dict())
    trends = trend_analyzer.analyze_trends(request.patient_name, request.disease_type)
    alerts = trend_analyzer.check_alerts(request.patient_name, request.disease_type)
    
    return {
        "status": "success",
        "checkin_result": result,
        "trends": trends,
        "alerts": alerts
    }


@app.get("/trends")
async def get_trends(patient: str, disease_type: str):
    """Get trend analysis."""
    return trend_analyzer.analyze_trends(patient, disease_type)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

