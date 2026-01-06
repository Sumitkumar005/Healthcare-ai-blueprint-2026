"""
Drug Interaction Checker.
"""

import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .medication_extractor import MedicationExtractor
from .interaction_checker import InteractionChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Drug Interaction Checker", version="1.0.0")
extractor = MedicationExtractor()
checker = InteractionChecker()


class MedicationListRequest(BaseModel):
    medications: list  # List of medication names


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drug Interaction Checker</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            textarea { width: 100%; height: 150px; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .severe { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
            .moderate { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 10px 0; }
            .minor { background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 15px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Drug Interaction Checker</h1>
        <form id="checkForm">
            <textarea id="medications" placeholder="Enter medications (one per line):&#10;Lisinopril&#10;Metformin&#10;Aspirin"></textarea>
            <button type="submit">Check Interactions</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('checkForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = document.getElementById('medications').value;
                const medications = text.split('\\n').filter(m => m.trim());
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({medications: medications})
                });
                const result = await response.json();
                let html = '';
                result.interactions.forEach(interaction => {
                    const severityClass = interaction.severity.toLowerCase();
                    html += `<div class="${severityClass}">
                        <strong>${interaction.medication1} + ${interaction.medication2}</strong><br>
                        Severity: ${interaction.severity}<br>
                        ${interaction.explanation}
                    </div>`;
                });
                document.getElementById('result').innerHTML = html || '<p>No interactions found.</p>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/check")
async def check_interactions(request: MedicationListRequest):
    """Check for drug interactions."""
    try:
        interactions = checker.check_all(request.medications)
        return {"status": "success", "interactions": interactions}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

