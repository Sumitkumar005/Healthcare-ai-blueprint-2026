"""
Wound Photo Documentation with Auto-Classification.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .wound_classifier import WoundClassifier
from .size_measurement import SizeMeasurement
from .description_generator import DescriptionGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Wound Photo Documentation", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = WoundClassifier()
size_measurement = SizeMeasurement()
description_gen = DescriptionGenerator()


class WoundAnalysisRequest(BaseModel):
    patient_name: str
    visit_date: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wound Photo Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            input[type="file"] { margin: 20px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            #preview { max-width: 500px; margin: 20px 0; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Wound Photo Documentation</h1>
        <form id="woundForm">
            <div>
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div>
                <label>Visit Date:</label>
                <input type="date" name="visit_date" required>
            </div>
            <div>
                <label>Upload Wound Photo:</label>
                <input type="file" id="photoInput" accept="image/*" required>
            </div>
            <button type="submit">Analyze Wound</button>
        </form>
        <img id="preview" style="display:none;">
        <div id="result"></div>
        <script>
            document.getElementById('photoInput').addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        document.getElementById('preview').src = e.target.result;
                        document.getElementById('preview').style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
            document.getElementById('woundForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('photo', document.getElementById('photoInput').files[0]);
                formData.append('patient_name', document.querySelector('[name="patient_name"]').value);
                formData.append('visit_date', document.querySelector('[name="visit_date"]').value);
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<div class="result">' +
                    '<h3>Wound Classification: ' + result.wound_type + '</h3>' +
                    '<p><strong>Description:</strong> ' + result.description + '</p>' +
                    '<p><strong>Size:</strong> ' + (result.size || 'Not measured') + '</p>' +
                    '</div>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/analyze")
async def analyze_wound(
    photo: UploadFile = File(...),
    patient_name: str = None,
    visit_date: str = None
):
    """Analyze wound photo."""
    try:
        image_data = await photo.read()
        
        # Classify wound
        wound_type = classifier.classify(image_data)
        
        # Measure size (if reference object present)
        size = size_measurement.measure(image_data)
        
        # Generate description
        description = description_gen.generate(wound_type, size)
        
        return {
            "status": "success",
            "wound_type": wound_type,
            "size": size,
            "description": description
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

