"""
Automated Patient No-Show Follow-Up System.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()
db_path = Path(__file__).parent.parent / "appointments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    patient_phone = Column(String)
    appointment_date = Column(DateTime)
    status = Column(String)  # scheduled, completed, no_show, cancelled
    no_show_date = Column(DateTime, nullable=True)
    follow_up_sent = Column(Boolean, default=False)
    rescheduled = Column(Boolean, default=False)
    cancellation_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class NoShowRequest(BaseModel):
    appointment_id: int
    patient_name: str
    patient_phone: str
    appointment_date: str


app = FastAPI(title="No-Show Follow-Up System", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Admin dashboard."""
    db = SessionLocal()
    no_shows = db.query(Appointment).filter(Appointment.status == "no_show").all()
    db.close()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>No-Show Follow-Up Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #007bff; color: white; }}
            button {{ background: #28a745; color: white; padding: 8px 15px; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>No-Show Follow-Up Dashboard</h1>
        <p>Total No-Shows: {len(no_shows)}</p>
        <table>
            <tr><th>Patient</th><th>Date</th><th>Status</th><th>Actions</th></tr>
    """
    for appt in no_shows:
        html += f"""
            <tr>
                <td>{appt.patient_name}</td>
                <td>{appt.appointment_date}</td>
                <td>{appt.status}</td>
                <td><button onclick="sendFollowUp({appt.id})">Send Follow-Up</button></td>
            </tr>
        """
    html += """
        </table>
        <script>
            async function sendFollowUp(id) {
                const response = await fetch(`/follow-up/${id}`, {method: 'POST'});
                alert('Follow-up sent!');
                location.reload();
            }
        </script>
    </body>
    </html>
    """
    return html


@app.post("/no-show")
async def mark_no_show(request: NoShowRequest):
    """Mark appointment as no-show."""
    db = SessionLocal()
    appt = Appointment(
        patient_name=request.patient_name,
        patient_phone=request.patient_phone,
        appointment_date=datetime.fromisoformat(request.appointment_date),
        status="no_show",
        no_show_date=datetime.now()
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    db.close()
    return {"status": "success", "appointment_id": appt.id}


@app.post("/follow-up/{appointment_id}")
async def send_follow_up(appointment_id: int):
    """Send follow-up message (simulated)."""
    db = SessionLocal()
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appt.follow_up_sent = True
    db.commit()
    db.close()
    
    logger.info(f"Follow-up sent to {appt.patient_name} at {appt.patient_phone}")
    return {"status": "success", "message": "Follow-up sent (simulated)"}


@app.get("/analytics")
async def get_analytics():
    """Get no-show analytics."""
    db = SessionLocal()
    total = db.query(Appointment).count()
    no_shows = db.query(Appointment).filter(Appointment.status == "no_show").count()
    rescheduled = db.query(Appointment).filter(Appointment.rescheduled == True).count()
    db.close()
    
    return {
        "total_appointments": total,
        "no_shows": no_shows,
        "rescheduled": rescheduled,
        "no_show_rate": (no_shows / total * 100) if total > 0 else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


