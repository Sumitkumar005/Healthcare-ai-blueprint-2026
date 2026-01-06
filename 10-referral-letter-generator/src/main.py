"""
Referral Letter Auto-Generator.
"""

import logging
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .letter_generator import ReferralLetterGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Referral Letter Generator", version="1.0.0")
generator = ReferralLetterGenerator()


class ReferralRequest(BaseModel):
    patient_name: str
    patient_dob: str
    specialist_type: str
    referral_reason: str
    patient_history: str
    examination_findings: Optional[str] = None
    test_results: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Referral Letter Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; }
            textarea { height: 100px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Referral Letter Generator</h1>
        <form id="referralForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>Date of Birth:</label>
                <input type="text" name="patient_dob" placeholder="YYYY-MM-DD" required>
            </div>
            <div class="form-group">
                <label>Specialist Type:</label>
                <select name="specialist_type" required>
                    <option>Cardiology</option>
                    <option>Orthopedics</option>
                    <option>Neurology</option>
                    <option>Dermatology</option>
                    <option>Gastroenterology</option>
                </select>
            </div>
            <div class="form-group">
                <label>Referral Reason:</label>
                <textarea name="referral_reason" required></textarea>
            </div>
            <div class="form-group">
                <label>Patient History:</label>
                <textarea name="patient_history" required></textarea>
            </div>
            <button type="submit">Generate Referral Letter</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('referralForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + result.letter + '</pre>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/generate")
async def generate_referral(request: ReferralRequest):
    """Generate referral letter."""
    try:
        letter = generator.generate(request.dict())
        return {"status": "success", "letter": letter}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


