"""
Medication Reconciliation Assistant - Main application.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .ocr_extractor import MedicationOCRExtractor
from .medication_parser import MedicationParser
from .reconciliation_engine import ReconciliationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Medication Reconciliation Assistant", version="1.0.0")

ocr_extractor = MedicationOCRExtractor()
parser = MedicationParser()
reconciler = ReconciliationEngine()


class MedicationListRequest(BaseModel):
    """Request for manual medication list entry."""
    home_medications: str
    hospital_medications: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medication Reconciliation</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            textarea { width: 100%; height: 150px; padding: 8px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .result-section { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .conflict { color: #dc3545; font-weight: bold; }
            .warning { color: #ffc107; }
        </style>
    </head>
    <body>
        <h1>Medication Reconciliation Assistant</h1>
        <div>
            <h2>Upload Medication Lists</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Home Medications (Image/PDF):</label>
                    <input type="file" name="home_meds" accept="image/*,application/pdf">
                </div>
                <div class="form-group">
                    <label>Hospital Discharge Medications (Image/PDF):</label>
                    <input type="file" name="hospital_meds" accept="image/*,application/pdf">
                </div>
                <button type="submit">Process Medications</button>
            </form>
        </div>
        <div>
            <h2>Or Enter Manually</h2>
            <form id="manualForm">
                <div class="form-group">
                    <label>Home Medications (one per line):</label>
                    <textarea name="home_medications" placeholder="Lisinopril 10mg daily&#10;Metformin 500mg twice daily"></textarea>
                </div>
                <div class="form-group">
                    <label>Hospital Discharge Medications:</label>
                    <textarea name="hospital_medications" placeholder="Lisinopril 10mg daily&#10;Metformin 1000mg twice daily&#10;Aspirin 81mg daily"></textarea>
                </div>
                <button type="submit">Reconcile Medications</button>
            </form>
        </div>
        <div id="result"></div>
        <script>
            document.getElementById('manualForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                const response = await fetch('/reconcile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                displayResult(result);
            });
            
            function displayResult(result) {
                let html = '<div class="result-section"><h2>Reconciled Medication List</h2>';
                html += '<h3>Continue:</h3><ul>';
                result.reconciled.continue.forEach(m => html += '<li>' + m + '</li>');
                html += '</ul>';
                html += '<h3>Discontinue:</h3><ul>';
                result.reconciled.discontinue.forEach(m => html += '<li class="conflict">' + m + '</li>');
                html += '</ul>';
                html += '<h3>Start New:</h3><ul>';
                result.reconciled.start_new.forEach(m => html += '<li>' + m + '</li>');
                html += '</ul>';
                if (result.conflicts.length > 0) {
                    html += '<h3 class="warning">Conflicts/Interactions:</h3><ul>';
                    result.conflicts.forEach(c => html += '<li class="conflict">' + c + '</li>');
                    html += '</ul>';
                }
                html += '</div>';
                document.getElementById('result').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return html


@app.post("/reconcile")
async def reconcile_medications(request: MedicationListRequest):
    """Reconcile medication lists."""
    try:
        # Parse medications
        home_meds = parser.parse_list(request.home_medications)
        hospital_meds = parser.parse_list(request.hospital_medications)
        
        # Reconcile
        reconciled = reconciler.reconcile(home_meds, hospital_meds)
        
        # Check for conflicts
        conflicts = reconciler.check_interactions(reconciled['continue'] + reconciled['start_new'])
        
        return {
            "status": "success",
            "reconciled": reconciled,
            "conflicts": conflicts
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_medication_lists(
    home_meds: UploadFile = File(...),
    hospital_meds: UploadFile = File(...)
):
    """Process uploaded medication lists."""
    try:
        # Extract text from images
        home_text = await ocr_extractor.extract(home_meds)
        hospital_text = await ocr_extractor.extract(hospital_meds)
        
        # Parse and reconcile
        home_meds_list = parser.parse_list(home_text)
        hospital_meds_list = parser.parse_list(hospital_text)
        
        reconciled = reconciler.reconcile(home_meds_list, hospital_meds_list)
        conflicts = reconciler.check_interactions(reconciled['continue'] + reconciled['start_new'])
        
        return {
            "status": "success",
            "reconciled": reconciled,
            "conflicts": conflicts
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
