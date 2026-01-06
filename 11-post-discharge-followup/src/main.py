"""
Post-Discharge Follow-Up Automation.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .followup_engine import FollowUpEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "followups.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Post-Discharge Follow-Up", version="1.0.0")
engine_followup = FollowUpEngine()


class DischargeRequest(BaseModel):
    patient_name: str
    discharge_date: str
    diagnosis: str


class FollowUpResponse(BaseModel):
    patient_id: str
    follow_up_id: int
    responses: dict


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Post-Discharge Follow-Up Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
            .urgent { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin: 10px 0; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #007bff; color: white; }
        </style>
    </head>
    <body>
        <h1>Post-Discharge Follow-Up Dashboard</h1>
        <div id="flagged-patients"></div>
        <div id="upcoming-followups"></div>
        <script>
            async function loadDashboard() {
                const response = await fetch('/dashboard');
                const data = await response.json();
                let html = '<h2>Flagged Patients (Require Immediate Attention)</h2>';
                if (data.flagged.length > 0) {
                    data.flagged.forEach(p => {
                        html += `<div class="urgent"><strong>${p.patient_name}</strong>: ${p.concern}</div>`;
                    });
                } else {
                    html += '<p>No flagged patients.</p>';
                }
                document.getElementById('flagged-patients').innerHTML = html;
            }
            loadDashboard();
        </script>
    </body>
    </html>
    """
    return html


@app.post("/discharge")
async def register_discharge(request: DischargeRequest):
    """Register new discharge."""
    engine_followup.schedule_followups(request.patient_name, request.discharge_date)
    return {"status": "success", "message": "Follow-ups scheduled"}


@app.post("/response")
async def submit_response(response: FollowUpResponse):
    """Submit follow-up response."""
    flagged = engine_followup.process_response(response.follow_up_id, response.responses)
    return {"status": "success", "flagged": flagged}


@app.get("/dashboard")
async def get_dashboard():
    """Get dashboard data."""
    flagged = engine_followup.get_flagged_patients()
    upcoming = engine_followup.get_upcoming_followups()
    return {"flagged": flagged, "upcoming": upcoming}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

