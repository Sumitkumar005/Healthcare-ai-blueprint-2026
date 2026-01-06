"""
Delirium Detection Tool - CAM Assessment.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .cam_assessment import CAMAssessment
from .intervention_planner import InterventionPlanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "delirium_assessments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Delirium Detection Tool", version="1.0.0")
cam = CAMAssessment()
planner = InterventionPlanner()


class CAMRequest(BaseModel):
    patient_name: str
    acute_onset: bool
    fluctuating_course: bool
    inattention: bool
    disorganized_thinking: bool
    altered_consciousness: bool


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve assessment interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CAM Delirium Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .positive { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>CAM Delirium Assessment</h1>
        <form id="camForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>1. Acute onset and fluctuating course?</label>
                <select name="acute_onset" required>
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>2. Inattention?</label>
                <select name="inattention" required>
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>3. Disorganized thinking?</label>
                <select name="disorganized_thinking" required>
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <div class="form-group">
                <label>4. Altered level of consciousness?</label>
                <select name="altered_consciousness" required>
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <button type="submit">Assess for Delirium</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('camForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.acute_onset = data.acute_onset === 'true';
                data.fluctuating_course = data.acute_onset; // Simplified
                data.inattention = data.inattention === 'true';
                data.disorganized_thinking = data.disorganized_thinking === 'true';
                data.altered_consciousness = data.altered_consciousness === 'true';
                const response = await fetch('/assess', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                let html = '<h2>CAM Assessment Result</h2>';
                if (result.delirium_positive) {
                    html += '<div class="positive"><strong>DELIRIUM POSITIVE</strong><br>' + result.interventions + '</div>';
                } else {
                    html += '<p>No delirium detected. Continue monitoring.</p>';
                }
                document.getElementById('result').innerHTML = html;
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/assess")
async def assess_delirium(request: CAMRequest):
    """Assess for delirium."""
    is_positive = cam.assess(request.dict())
    interventions = planner.generate_interventions(request.dict(), is_positive)
    
    return {
        "delirium_positive": is_positive,
        "interventions": interventions
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

