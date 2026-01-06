"""
Antibiotic Stewardship Decision Support.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .recommendation_engine import RecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "antibiotic_stewardship.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Antibiotic Stewardship Decision Support", version="1.0.0")
recommender = RecommendationEngine()


class AntibioticRequest(BaseModel):
    infection_site: str  # UTI, pneumonia, skin, etc.
    patient_age: int
    allergies: list
    renal_function: str  # normal, impaired
    severity: str  # mild, moderate, severe
    recent_antibiotics: list


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Antibiotic Stewardship Decision Support</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Antibiotic Stewardship Decision Support</h1>
        <form id="requestForm">
            <div class="form-group">
                <label>Infection Site:</label>
                <select name="infection_site" required>
                    <option value="uti">UTI</option>
                    <option value="pneumonia">Pneumonia</option>
                    <option value="skin">Skin/Soft Tissue</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Patient Age:</label>
                <input type="number" name="patient_age" required>
            </div>
            <div class="form-group">
                <label>Severity:</label>
                <select name="severity" required>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                </select>
            </div>
            <div class="form-group">
                <label>Renal Function:</label>
                <select name="renal_function" required>
                    <option value="normal">Normal</option>
                    <option value="impaired">Impaired</option>
                </select>
            </div>
            <button type="submit">Get Recommendation</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('requestForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.patient_age = parseInt(data.patient_age);
                data.allergies = [];
                data.recent_antibiotics = [];
                const response = await fetch('/recommend', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<h2>Recommendation</h2>' +
                    '<p><strong>Antibiotic:</strong> ' + result.antibiotic + '</p>' +
                    '<p><strong>Dosing:</strong> ' + result.dosing + '</p>' +
                    '<p><strong>Duration:</strong> ' + result.duration + '</p>' +
                    '<p><strong>Rationale:</strong> ' + result.rationale + '</p>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/recommend")
async def get_recommendation(request: AntibioticRequest):
    """Get antibiotic recommendation."""
    recommendation = recommender.recommend(request.dict())
    return recommendation


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

