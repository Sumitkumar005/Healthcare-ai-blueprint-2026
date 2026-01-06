"""
Pressure Ulcer Risk Predictor.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .braden_scale import BradenScale
from .prevention_planner import PreventionPlanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "braden_assessments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Pressure Ulcer Risk Predictor", version="1.0.0")
braden = BradenScale()
planner = PreventionPlanner()


class BradenAssessmentRequest(BaseModel):
    patient_name: str
    sensory_perception: int  # 1-4
    moisture: int  # 1-4
    activity: int  # 1-4
    mobility: int  # 1-4
    nutrition: int  # 1-4
    friction_shear: int  # 1-4


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve assessment interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Braden Scale Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Braden Scale Pressure Ulcer Risk Assessment</h1>
        <form id="assessmentForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>Sensory Perception (1-4):</label>
                <select name="sensory_perception" required>
                    <option value="1">1 - Completely limited</option>
                    <option value="2">2 - Very limited</option>
                    <option value="3">3 - Slightly limited</option>
                    <option value="4">4 - No impairment</option>
                </select>
            </div>
            <div class="form-group">
                <label>Moisture (1-4):</label>
                <select name="moisture" required>
                    <option value="1">1 - Constantly moist</option>
                    <option value="2">2 - Very moist</option>
                    <option value="3">3 - Occasionally moist</option>
                    <option value="4">4 - Rarely moist</option>
                </select>
            </div>
            <div class="form-group">
                <label>Activity (1-4):</label>
                <select name="activity" required>
                    <option value="1">1 - Bedfast</option>
                    <option value="2">2 - Chairfast</option>
                    <option value="3">3 - Walks occasionally</option>
                    <option value="4">4 - Walks frequently</option>
                </select>
            </div>
            <div class="form-group">
                <label>Mobility (1-4):</label>
                <select name="mobility" required>
                    <option value="1">1 - Completely immobile</option>
                    <option value="2">2 - Very limited</option>
                    <option value="3">3 - Slightly limited</option>
                    <option value="4">4 - No limitations</option>
                </select>
            </div>
            <div class="form-group">
                <label>Nutrition (1-4):</label>
                <select name="nutrition" required>
                    <option value="1">1 - Very poor</option>
                    <option value="2">2 - Probably inadequate</option>
                    <option value="3">3 - Adequate</option>
                    <option value="4">4 - Excellent</option>
                </select>
            </div>
            <div class="form-group">
                <label>Friction/Shear (1-3):</label>
                <select name="friction_shear" required>
                    <option value="1">1 - Problem</option>
                    <option value="2">2 - Potential problem</option>
                    <option value="3">3 - No apparent problem</option>
                </select>
            </div>
            <button type="submit">Calculate Risk & Generate Prevention Plan</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('assessmentForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                Object.keys(data).forEach(k => {
                    if (k !== 'patient_name') data[k] = parseInt(data[k]);
                });
                const response = await fetch('/assess', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<h2>Braden Score: ' + result.score + '</h2>' +
                    '<p>Risk Level: ' + result.risk_level + '</p>' +
                    '<h3>Prevention Plan:</h3><pre>' + result.prevention_plan + '</pre>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/assess")
async def assess_risk(request: BradenAssessmentRequest):
    """Calculate Braden score and generate prevention plan."""
    score = braden.calculate(request.dict())
    risk_level = braden.get_risk_level(score)
    prevention_plan = planner.generate_plan(request.dict(), score)
    
    return {
        "score": score,
        "risk_level": risk_level,
        "prevention_plan": prevention_plan
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

