"""
Sepsis Early Warning System.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .qsofa_calculator import QSOFACalculator
from .sirs_calculator import SIRSCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "vitals.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Sepsis Early Warning System", version="1.0.0")
qsofa = QSOFACalculator()
sirs = SIRSCalculator()


class VitalSignsRequest(BaseModel):
    patient_name: str
    temperature: float
    heart_rate: int
    respiratory_rate: int
    systolic_bp: int
    mental_status: str  # "normal" or "altered"
    wbc: float = None  # Optional


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sepsis Early Warning System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .high-risk { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Sepsis Early Warning System</h1>
        <form id="vitalsForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>Temperature (°F):</label>
                <input type="number" step="0.1" name="temperature" required>
            </div>
            <div class="form-group">
                <label>Heart Rate (bpm):</label>
                <input type="number" name="heart_rate" required>
            </div>
            <div class="form-group">
                <label>Respiratory Rate:</label>
                <input type="number" name="respiratory_rate" required>
            </div>
            <div class="form-group">
                <label>Systolic BP:</label>
                <input type="number" name="systolic_bp" required>
            </div>
            <div class="form-group">
                <label>Mental Status:</label>
                <select name="mental_status" required>
                    <option value="normal">Normal</option>
                    <option value="altered">Altered</option>
                </select>
            </div>
            <button type="submit">Calculate Risk Scores</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('vitalsForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.temperature = parseFloat(data.temperature);
                data.heart_rate = parseInt(data.heart_rate);
                data.respiratory_rate = parseInt(data.respiratory_rate);
                data.systolic_bp = parseInt(data.systolic_bp);
                const response = await fetch('/assess', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                let html = '<h2>Risk Assessment</h2>';
                html += '<p><strong>qSOFA Score:</strong> ' + result.qsofa_score + '</p>';
                html += '<p><strong>qSOFA Risk:</strong> ' + result.qsofa_risk + '</p>';
                html += '<p><strong>SIRS Score:</strong> ' + result.sirs_score + '</p>';
                html += '<p><strong>SIRS Risk:</strong> ' + result.sirs_risk + '</p>';
                if (result.overall_risk === 'High') {
                    html += '<div class="high-risk"><strong>HIGH RISK FOR SEPSIS - IMMEDIATE EVALUATION NEEDED</strong></div>';
                }
                document.getElementById('result').innerHTML = html;
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/assess")
async def assess_sepsis_risk(request: VitalSignsRequest):
    """Assess sepsis risk."""
    qsofa_score = qsofa.calculate(request.dict())
    qsofa_risk = qsofa.get_risk_level(qsofa_score)
    
    sirs_score = sirs.calculate(request.dict())
    sirs_risk = sirs.get_risk_level(sirs_score)
    
    overall_risk = "High" if qsofa_risk == "High" or sirs_risk == "High" else "Low"
    
    return {
        "qsofa_score": qsofa_score,
        "qsofa_risk": qsofa_risk,
        "sirs_score": sirs_score,
        "sirs_risk": sirs_risk,
        "overall_risk": overall_risk
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

