"""
FastAPI application for Patient Reminder Optimization Engine
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from optimizer import ReminderOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./reminder_optimization.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Reminder(Base):
    """Database model for reminders"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    appointment_id = Column(String)
    channel = Column(String)  # sms, email, phone
    timing_hours = Column(Integer)  # Hours before appointment
    sent = Column(Boolean, default=False)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)
    cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Reminder Optimization Engine", version="1.0.0")
optimizer = ReminderOptimizer()


class ReminderRequest(BaseModel):
    """Request to send reminder"""
    patient_id: str
    appointment_id: str
    channel: str
    timing_hours: int


class ReminderResponseRequest(BaseModel):
    """Request to log reminder response"""
    reminder_id: int
    opened: Optional[bool] = None
    clicked: Optional[bool] = None
    confirmed: Optional[bool] = None
    cancelled: Optional[bool] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Patient Reminder Optimization Engine</h1><p>Use API endpoints</p>")


@app.post("/api/reminder")
async def send_reminder(request: ReminderRequest):
    """Send reminder"""
    try:
        db = SessionLocal()
        reminder = Reminder(
            patient_id=request.patient_id,
            appointment_id=request.appointment_id,
            channel=request.channel,
            timing_hours=request.timing_hours,
            sent=True
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        db.close()
        
        return {
            "message": "Reminder sent",
            "reminder_id": reminder.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reminder/response")
async def log_response(request: ReminderResponseRequest):
    """Log reminder response"""
    try:
        db = SessionLocal()
        reminder = db.query(Reminder).filter(Reminder.id == request.reminder_id).first()
        if not reminder:
            db.close()
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        if request.opened is not None:
            reminder.opened = request.opened
        if request.clicked is not None:
            reminder.clicked = request.clicked
        if request.confirmed is not None:
            reminder.confirmed = request.confirmed
        if request.cancelled is not None:
            reminder.cancelled = request.cancelled
        
        db.commit()
        db.close()
        
        return {"message": "Response logged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/optimization/{patient_id}")
async def get_optimal_strategy(patient_id: str):
    """Get optimal reminder strategy for patient"""
    try:
        db = SessionLocal()
        reminders = db.query(Reminder).filter(Reminder.patient_id == patient_id).all()
        db.close()
        
        strategy = optimizer.calculate_optimal_strategy(reminders)
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get reminder analytics"""
    try:
        db = SessionLocal()
        reminders = db.query(Reminder).all()
        db.close()
        
        return optimizer.calculate_analytics(reminders)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


