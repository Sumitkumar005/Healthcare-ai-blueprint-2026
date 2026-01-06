"""
Medication Reminder System.
"""

import logging
from datetime import datetime, time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .reminder_engine import ReminderEngine
from .adherence_tracker import AdherenceTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "medications.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Medication Reminder System", version="1.0.0")
reminder_engine = ReminderEngine()
adherence_tracker = AdherenceTracker()


class MedicationRequest(BaseModel):
    patient_name: str
    medication_name: str
    dose: str
    frequency: str
    times: list  # List of times (e.g., ["08:00", "20:00"])


class ConfirmationRequest(BaseModel):
    patient_name: str
    medication_name: str
    scheduled_time: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medication Reminder System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            .medication-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            button { background: #28a745; color: white; padding: 8px 15px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Medication Reminder System</h1>
        <div id="medications"></div>
        <div id="adherence"></div>
        <script>
            async function loadMedications() {
                const response = await fetch('/medications?patient=John Doe');
                const data = await response.json();
                let html = '<h2>Your Medications</h2>';
                data.forEach(med => {
                    html += `<div class="medication-card">
                        <h3>${med.medication_name}</h3>
                        <p>Dose: ${med.dose}</p>
                        <p>Times: ${med.times.join(', ')}</p>
                        <button onclick="confirmDose('${med.medication_name}')">I Took This</button>
                    </div>`;
                });
                document.getElementById('medications').innerHTML = html;
            }
            async function confirmDose(medName) {
                await fetch('/confirm', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({patient_name: 'John Doe', medication_name: medName, scheduled_time: new Date().toISOString()})
                });
                alert('Medication confirmed!');
                loadMedications();
            }
            loadMedications();
        </script>
    </body>
    </html>
    """
    return html


@app.post("/medications")
async def add_medication(request: MedicationRequest):
    """Add medication schedule."""
    reminder_engine.add_medication(request.dict())
    return {"status": "success"}


@app.get("/medications")
async def get_medications(patient: str):
    """Get patient medications."""
    return reminder_engine.get_medications(patient)


@app.post("/confirm")
async def confirm_medication(request: ConfirmationRequest):
    """Confirm medication taken."""
    adherence_tracker.record_confirmation(request.dict())
    return {"status": "success"}


@app.get("/adherence")
async def get_adherence(patient: str):
    """Get adherence rate."""
    rate = adherence_tracker.calculate_adherence(patient)
    return {"patient": patient, "adherence_rate": rate}


@app.get("/provider-dashboard")
async def provider_dashboard():
    """Get provider dashboard with all patients."""
    return adherence_tracker.get_provider_dashboard()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

