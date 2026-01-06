"""
Pain Assessment Tool for Non-Verbal Patients - PAINAD Scale.
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

from .painad_scale import PAINADScale

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "pain_assessments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="PAINAD Pain Assessment", version="1.0.0")
painad = PAINADScale()


class PAINADRequest(BaseModel):
    patient_name: str
    breathing: int  # 0-2
    negative_vocalization: int  # 0-2
    facial_expression: int  # 0-2
    body_language: int  # 0-2
    consolability: int  # 0-2


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve assessment interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PAINAD Pain Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select { width: 100%; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>PAINAD Pain Assessment Tool</h1>
        <form id="assessmentForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>Breathing (0-2):</label>
                <select name="breathing" required>
                    <option value="0">Normal</option>
                    <option value="1">Occasional labored breathing</option>
                    <option value="2">Short period of hyperventilation</option>
                </select>
            </div>
            <div class="form-group">
                <label>Negative Vocalization (0-2):</label>
                <select name="negative_vocalization" required>
                    <option value="0">None</option>
                    <option value="1">Occasional moan/groan</option>
                    <option value="2">Repeated troubled calling out</option>
                </select>
            </div>
            <div class="form-group">
                <label>Facial Expression (0-2):</label>
                <select name="facial_expression" required>
                    <option value="0">Smiling/No expression</option>
                    <option value="1">Sad/Frightened/Frown</option>
                    <option value="2">Facial grimacing</option>
                </select>
            </div>
            <div class="form-group">
                <label>Body Language (0-2):</label>
                <select name="body_language" required>
                    <option value="0">Relaxed</option>
                    <option value="1">Tense/Distressed pacing</option>
                    <option value="2">Rigid/Fists clenched</option>
                </select>
            </div>
            <div class="form-group">
                <label>Consolability (0-2):</label>
                <select name="consolability" required>
                    <option value="0">No need to console</option>
                    <option value="1">Distracted/reassured</option>
                    <option value="2">Unable to console/distract</option>
                </select>
            </div>
            <button type="submit">Calculate Pain Score</button>
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
                    '<h2>Pain Score: ' + result.score + '/10</h2>' +
                    '<p>Pain Level: ' + result.pain_level + '</p>' +
                    '<p>Interpretation: ' + result.interpretation + '</p>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/assess")
async def assess_pain(request: PAINADRequest):
    """Calculate PAINAD score."""
    score = painad.calculate_score(request.dict())
    pain_level = painad.get_pain_level(score)
    interpretation = painad.get_interpretation(score)
    
    return {
        "score": score,
        "pain_level": pain_level,
        "interpretation": interpretation
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

