"""
Nutrition Risk Screening Tool - MST/MUST.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .nutrition_screening import NutritionScreening

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "nutrition_screening.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Nutrition Risk Screening", version="1.0.0")
screening = NutritionScreening()


class MSTRequest(BaseModel):
    patient_name: str
    weight_loss: bool  # Recent weight loss
    reduced_appetite: bool  # Reduced appetite


class MUSTRequest(BaseModel):
    patient_name: str
    bmi: float
    weight_loss_percent: float
    acute_disease: bool


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve screening interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nutrition Risk Screening</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .tabs { display: flex; margin-bottom: 20px; }
            .tab { padding: 10px 20px; background: #f0f0f0; cursor: pointer; }
            .tab.active { background: #007bff; color: white; }
        </style>
    </head>
    <body>
        <h1>Nutrition Risk Screening</h1>
        <div class="tabs">
            <div class="tab active" onclick="showTab('mst')">MST</div>
            <div class="tab" onclick="showTab('must')">MUST</div>
        </div>
        <div id="mst-form">
            <h2>Malnutrition Screening Tool (MST)</h2>
            <form id="mstForm">
                <div class="form-group">
                    <label>Patient Name:</label>
                    <input type="text" name="patient_name" required>
                </div>
                <div class="form-group">
                    <label>Recent Weight Loss?</label>
                    <select name="weight_loss" required>
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Reduced Appetite?</label>
                    <select name="reduced_appetite" required>
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
                <button type="submit">Calculate MST Score</button>
            </form>
        </div>
        <div id="must-form" style="display:none;">
            <h2>MUST (Malnutrition Universal Screening Tool)</h2>
            <form id="mustForm">
                <div class="form-group">
                    <label>Patient Name:</label>
                    <input type="text" name="patient_name" required>
                </div>
                <div class="form-group">
                    <label>BMI:</label>
                    <input type="number" step="0.1" name="bmi" required>
                </div>
                <div class="form-group">
                    <label>Weight Loss %:</label>
                    <input type="number" step="0.1" name="weight_loss_percent" required>
                </div>
                <div class="form-group">
                    <label>Acute Disease Effect?</label>
                    <select name="acute_disease" required>
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
                <button type="submit">Calculate MUST Score</button>
            </form>
        </div>
        <div id="result"></div>
        <script>
            function showTab(tab) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.getElementById('mst-form').style.display = tab === 'mst' ? 'block' : 'none';
                document.getElementById('must-form').style.display = tab === 'must' ? 'block' : 'none';
                event.target.classList.add('active');
            }
            document.getElementById('mstForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.weight_loss = data.weight_loss === 'true';
                data.reduced_appetite = data.reduced_appetite === 'true';
                const response = await fetch('/mst', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<h2>MST Score: ' + result.score + '</h2>' +
                    '<p>Risk Level: ' + result.risk_level + '</p>' +
                    '<p>Recommendation: ' + result.recommendation + '</p>';
            });
            document.getElementById('mustForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.bmi = parseFloat(data.bmi);
                data.weight_loss_percent = parseFloat(data.weight_loss_percent);
                data.acute_disease = data.acute_disease === 'true';
                const response = await fetch('/must', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<h2>MUST Score: ' + result.score + '</h2>' +
                    '<p>Risk Level: ' + result.risk_level + '</p>' +
                    '<p>Recommendation: ' + result.recommendation + '</p>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/mst")
async def assess_mst(request: MSTRequest):
    """Calculate MST score."""
    score = screening.calculate_mst(request.weight_loss, request.reduced_appetite)
    risk_level = screening.get_mst_risk(score)
    recommendation = screening.get_mst_recommendation(score)
    
    return {
        "score": score,
        "risk_level": risk_level,
        "recommendation": recommendation
    }


@app.post("/must")
async def assess_must(request: MUSTRequest):
    """Calculate MUST score."""
    score = screening.calculate_must(request.bmi, request.weight_loss_percent, request.acute_disease)
    risk_level = screening.get_must_risk(score)
    recommendation = screening.get_must_recommendation(score)
    
    return {
        "score": score,
        "risk_level": risk_level,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

