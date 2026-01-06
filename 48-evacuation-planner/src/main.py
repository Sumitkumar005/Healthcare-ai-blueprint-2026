"""
FastAPI application for Healthcare Facility Evacuation Planner
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from evacuation_planner import EvacuationPlanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./evacuation_planner.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    """Database model for patients"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    room_number = Column(String)
    mobility_level = Column(String)  # ambulatory, wheelchair, stretcher
    acuity_level = Column(String)  # low, medium, high
    special_equipment = Column(String, nullable=True)  # oxygen, monitors, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class EvacuationRoute(Base):
    """Database model for evacuation routes"""
    __tablename__ = "evacuation_routes"
    
    id = Column(Integer, primary_key=True)
    route_id = Column(String, unique=True)
    from_room = Column(String)
    to_exit = Column(String)
    route_path = Column(Text)  # JSON string
    priority = Column(Integer)  # 1 = highest
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Facility Evacuation Planner", version="1.0.0")
planner = EvacuationPlanner()


class PatientRequest(BaseModel):
    """Request to add patient"""
    patient_id: str
    room_number: str
    mobility_level: str
    acuity_level: str
    special_equipment: Optional[str] = None


class EvacuationRequest(BaseModel):
    """Request to generate evacuation plan"""
    floor: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Healthcare Facility Evacuation Planner</h1><p>Use API endpoints</p>")


@app.post("/api/patient")
async def add_patient(request: PatientRequest):
    """Add patient for evacuation planning"""
    try:
        db = SessionLocal()
        patient = Patient(
            patient_id=request.patient_id,
            room_number=request.room_number,
            mobility_level=request.mobility_level,
            acuity_level=request.acuity_level,
            special_equipment=request.special_equipment
        )
        db.add(patient)
        db.commit()
        db.close()
        return {"message": "Patient added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evacuation/plan")
async def generate_evacuation_plan(request: EvacuationRequest):
    """Generate evacuation plan"""
    try:
        db = SessionLocal()
        patients = db.query(Patient).all()
        db.close()
        
        plan = planner.generate_plan(patients, request.floor)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


