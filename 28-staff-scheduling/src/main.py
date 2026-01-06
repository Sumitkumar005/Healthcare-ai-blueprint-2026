"""
FastAPI application for Staff Scheduling Optimizer
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from scheduler import ScheduleOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./staff_scheduling.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StaffMember(Base):
    """Database model for staff"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    certifications = Column(String)  # JSON string
    availability = Column(String)  # JSON string
    fte_status = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Schedule(Base):
    """Database model for schedules"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer)
    shift_date = Column(DateTime)
    shift_type = Column(String)  # Day, Night, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Staff Scheduling Optimizer", version="1.0.0")
optimizer = ScheduleOptimizer()


class StaffRequest(BaseModel):
    """Request to add staff"""
    name: str
    certifications: List[str]
    availability: dict
    fte_status: float


class ScheduleRequest(BaseModel):
    """Request to generate schedule"""
    start_date: str
    end_date: str
    patient_census: int
    acuity_level: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Staff Scheduling Optimizer</h1><p>Use API endpoints</p>")


@app.post("/api/staff")
async def add_staff(request: StaffRequest):
    """Add staff member"""
    try:
        import json
        db = SessionLocal()
        staff = StaffMember(
            name=request.name,
            certifications=json.dumps(request.certifications),
            availability=json.dumps(request.availability),
            fte_status=request.fte_status
        )
        db.add(staff)
        db.commit()
        db.close()
        return {"message": "Staff added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/schedule/generate")
async def generate_schedule(request: ScheduleRequest):
    """Generate optimized schedule"""
    try:
        db = SessionLocal()
        staff_members = db.query(StaffMember).all()
        db.close()
        
        schedule = optimizer.generate_schedule(
            staff_members=staff_members,
            start_date=datetime.fromisoformat(request.start_date),
            end_date=datetime.fromisoformat(request.end_date),
            patient_census=request.patient_census,
            acuity_level=request.acuity_level
        )
        
        return {"schedule": schedule, "message": "Schedule generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

