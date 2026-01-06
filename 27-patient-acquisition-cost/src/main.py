"""
FastAPI application for Patient Acquisition Cost Tracker
"""
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from cac_calculator import CACCalculator
from analytics_engine import AnalyticsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./patient_acquisition.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    """Database model for patients"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    acquisition_source = Column(String)  # Google, Facebook, Referral, etc.
    acquisition_date = Column(DateTime, default=datetime.utcnow)
    lifetime_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketingSpend(Base):
    """Database model for marketing spend"""
    __tablename__ = "marketing_spend"
    
    id = Column(Integer, primary_key=True)
    channel = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Acquisition Cost Tracker", version="1.0.0")

cac_calculator = CACCalculator()
analytics_engine = AnalyticsEngine()


class PatientRequest(BaseModel):
    """Request to add a patient"""
    patient_id: str
    acquisition_source: str


class SpendRequest(BaseModel):
    """Request to add marketing spend"""
    channel: str
    amount: float


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Patient Acquisition Cost Tracker</h1><p>Use API endpoints</p>")


@app.post("/api/patient")
async def add_patient(request: PatientRequest):
    """Add a new patient with acquisition source"""
    try:
        db = SessionLocal()
        patient = Patient(
            patient_id=request.patient_id,
            acquisition_source=request.acquisition_source
        )
        db.add(patient)
        db.commit()
        db.close()
        return {"message": "Patient added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/spend")
async def add_spend(request: SpendRequest):
    """Add marketing spend"""
    try:
        db = SessionLocal()
        spend = MarketingSpend(
            channel=request.channel,
            amount=request.amount
        )
        db.add(spend)
        db.commit()
        db.close()
        return {"message": "Spend recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get CAC, LTV, and ROI analytics"""
    try:
        db = SessionLocal()
        patients = db.query(Patient).all()
        spends = db.query(MarketingSpend).all()
        db.close()
        
        analytics = analytics_engine.calculate_metrics(patients, spends)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

