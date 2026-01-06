"""
Appointment Preparation Coach.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .prep_coach import AppointmentPrepCoach

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Appointment Prep Coach", version="1.0.0")
coach = AppointmentPrepCoach()


class PrepRequest(BaseModel):
    appointment_type: str
    patient_name: str
    chief_complaint: str = ""


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Appointment Prep Coach</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Appointment Preparation Coach</h1>
        <form id="prepForm">
            <div class="form-group">
                <label>Appointment Type:</label>
                <select name="appointment_type" required>
                    <option>General Checkup</option>
                    <option>Specialist Consultation</option>
                    <option>Follow-up</option>
                </select>
            </div>
            <div class="form-group">
                <label>Chief Complaint (optional):</label>
                <textarea name="chief_complaint"></textarea>
            </div>
            <button type="submit">Generate Prep Guide</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('prepForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + result.prep_guide + '</pre>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/generate")
async def generate_prep_guide(request: PrepRequest):
    """Generate appointment prep guide."""
    try:
        guide = coach.generate_prep_guide(request.dict())
        return {"status": "success", "prep_guide": guide}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

