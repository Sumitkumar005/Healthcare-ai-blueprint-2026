"""
Skin Lesion Triage Assistant.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .abcde_analyzer import ABCDEAnalyzer
from .triage_engine import TriageEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Skin Lesion Triage Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "lesions.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

analyzer = ABCDEAnalyzer()
triage = TriageEngine()


class LesionRequest(BaseModel):
    patient_name: str
    lesion_location: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Skin Lesion Triage Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            .disclaimer { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
            input[type="file"] { margin: 20px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .urgent { background: #ffebee; border-left: 4px solid #f44336; }
        </style>
    </head>
    <body>
        <h1>Skin Lesion Triage Assistant</h1>
        <div class="disclaimer">
            <strong>⚠️ DISCLAIMER:</strong> This is a clinical decision support tool, NOT a diagnostic tool. 
            Always consult with a dermatologist for definitive diagnosis.
        </div>
        <form id="lesionForm">
            <div>
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div>
                <label>Lesion Location:</label>
                <input type="text" name="lesion_location" placeholder="e.g., Left arm" required>
            </div>
            <div>
                <label>Upload Lesion Photo (with size reference if possible):</label>
                <input type="file" id="photoInput" accept="image/*" required>
            </div>
            <button type="submit">Analyze Lesion</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('lesionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('photo', document.getElementById('photoInput').files[0]);
                formData.append('patient_name', document.querySelector('[name="patient_name"]').value);
                formData.append('lesion_location', document.querySelector('[name="lesion_location"]').value);
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                let html = '<div class="result">';
                html += '<h2>ABCDE Assessment</h2>';
                html += '<p><strong>Asymmetry:</strong> ' + result.abcde.asymmetry + '</p>';
                html += '<p><strong>Border:</strong> ' + result.abcde.border + '</p>';
                html += '<p><strong>Color:</strong> ' + result.abcde.color + '</p>';
                html += '<p><strong>Diameter:</strong> ' + result.abcde.diameter + '</p>';
                html += '<h3>Triage Recommendation: ' + result.triage_recommendation + '</h3>';
                html += '<p>' + result.rationale + '</p>';
                html += '</div>';
                document.getElementById('result').innerHTML = html;
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/analyze")
async def analyze_lesion(
    photo: UploadFile = File(...),
    patient_name: str = None,
    lesion_location: str = None
):
    """Analyze skin lesion using ABCDE criteria."""
    try:
        image_data = await photo.read()
        
        # Analyze ABCDE criteria
        abcde_scores = analyzer.analyze(image_data)
        
        # Calculate risk score
        risk_score = analyzer.calculate_risk_score(abcde_scores)
        
        # Get triage recommendation
        recommendation = triage.get_recommendation(risk_score)
        
        return {
            "status": "success",
            "abcde": abcde_scores,
            "risk_score": risk_score,
            "triage_recommendation": recommendation["level"],
            "rationale": recommendation["rationale"]
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

