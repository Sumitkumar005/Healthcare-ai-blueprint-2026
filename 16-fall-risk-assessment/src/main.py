"""
Fall Risk Assessment Tool - Morse Fall Scale.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .morse_scale import MorseFallScale

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "assessments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Fall Risk Assessment", version="1.0.0")
morse_scale = MorseFallScale()


class AssessmentRequest(BaseModel):
    patient_name: str
    history_of_falling: int  # 0 or 25
    secondary_diagnosis: int  # 0 or 15
    ambulatory_aid: int  # 0, 15, or 30
    iv_heparin_lock: int  # 0 or 20
    gait: int  # 0, 10, or 20
    mental_status: int  # 0 or 15


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve assessment interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Morse Fall Scale Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Morse Fall Scale Assessment</h1>
        <form id="assessmentForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>History of Falling:</label>
                <select name="history_of_falling" required>
                    <option value="0">No</option>
                    <option value="25">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>Secondary Diagnosis:</label>
                <select name="secondary_diagnosis" required>
                    <option value="0">No</option>
                    <option value="15">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>Ambulatory Aid:</label>
                <select name="ambulatory_aid" required>
                    <option value="0">None/Bed rest/Nurse assist</option>
                    <option value="15">Crutches/Cane/Walker</option>
                    <option value="30">Furniture</option>
                </select>
            </div>
            <div class="form-group">
                <label>IV/Heparin Lock:</label>
                <select name="iv_heparin_lock" required>
                    <option value="0">No</option>
                    <option value="20">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>Gait:</label>
                <select name="gait" required>
                    <option value="0">Normal/Bed rest/Immobile</option>
                    <option value="10">Weak</option>
                    <option value="20">Impaired</option>
                </select>
            </div>
            <div class="form-group">
                <label>Mental Status:</label>
                <select name="mental_status" required>
                    <option value="0">Oriented to own ability</option>
                    <option value="15">Forgets limitations</option>
                </select>
            </div>
            <button type="submit">Calculate Risk Score</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('assessmentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                Object.keys(data).forEach(k => data[k] = parseInt(data[k]) || data[k]);
                const response = await fetch('/assess', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<h2>Risk Score: ' + result.score + '</h2>' +
                    '<p>Risk Level: ' + result.risk_level + '</p>' +
                    '<p>Recommendations: ' + result.recommendations + '</p>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/assess")
async def assess_fall_risk(request: AssessmentRequest):
    """Calculate fall risk score."""
    score = morse_scale.calculate_score(request.dict())
    risk_level = morse_scale.get_risk_level(score)
    recommendations = morse_scale.get_recommendations(score)
    
    return {
        "score": score,
        "risk_level": risk_level,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

