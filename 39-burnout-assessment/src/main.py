"""
FastAPI application for Provider Burnout Risk Assessment
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from burnout_calculator import BurnoutRiskCalculator
from intervention_engine import InterventionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./burnout_assessment.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProviderWorkload(Base):
    """Database model for provider workload"""
    __tablename__ = "provider_workload"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    patient_volume = Column(Integer)
    appointment_hours = Column(Float)
    inbox_messages = Column(Integer)
    after_hours_work = Column(Float)
    vacation_days_used = Column(Integer)
    patient_complexity = Column(Float)
    burnout_risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Provider Burnout Risk Assessment", version="1.0.0")
risk_calculator = BurnoutRiskCalculator()
intervention_engine = InterventionEngine()


class WorkloadRequest(BaseModel):
    """Request to add workload data"""
    provider_id: str
    patient_volume: int
    appointment_hours: float
    inbox_messages: int
    after_hours_work: float
    vacation_days_used: int
    patient_complexity: float = 1.0


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Provider Burnout Risk Assessment</h1><p>Use API endpoints</p>")


@app.post("/api/workload")
async def add_workload(request: WorkloadRequest):
    """Add provider workload data"""
    try:
        # Calculate burnout risk
        risk_score = risk_calculator.calculate_risk(
            patient_volume=request.patient_volume,
            appointment_hours=request.appointment_hours,
            inbox_messages=request.inbox_messages,
            after_hours_work=request.after_hours_work,
            vacation_days_used=request.vacation_days_used,
            patient_complexity=request.patient_complexity
        )
        
        # Get interventions
        interventions = intervention_engine.get_interventions(risk_score)
        
        db = SessionLocal()
        workload = ProviderWorkload(
            provider_id=request.provider_id,
            patient_volume=request.patient_volume,
            appointment_hours=request.appointment_hours,
            inbox_messages=request.inbox_messages,
            after_hours_work=request.after_hours_work,
            vacation_days_used=request.vacation_days_used,
            patient_complexity=request.patient_complexity,
            burnout_risk_score=risk_score
        )
        db.add(workload)
        db.commit()
        db.close()
        
        return {
            "provider_id": request.provider_id,
            "burnout_risk_score": round(risk_score, 2),
            "risk_level": "High" if risk_score >= 70 else "Medium" if risk_score >= 40 else "Low",
            "interventions": interventions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/provider/{provider_id}/risk")
async def get_provider_risk(provider_id: str):
    """Get current risk for provider"""
    try:
        db = SessionLocal()
        workloads = db.query(ProviderWorkload).filter(
            ProviderWorkload.provider_id == provider_id
        ).order_by(ProviderWorkload.date.desc()).limit(10).all()
        db.close()
        
        if not workloads:
            raise HTTPException(status_code=404, detail="No workload data found")
        
        latest = workloads[0]
        interventions = intervention_engine.get_interventions(latest.burnout_risk_score)
        
        return {
            "provider_id": provider_id,
            "current_risk_score": round(latest.burnout_risk_score, 2) if latest.burnout_risk_score else None,
            "risk_level": "High" if latest.burnout_risk_score and latest.burnout_risk_score >= 70 else "Medium" if latest.burnout_risk_score and latest.burnout_risk_score >= 40 else "Low",
            "interventions": interventions,
            "trend": "increasing" if len(workloads) > 1 and workloads[0].burnout_risk_score > workloads[-1].burnout_risk_score else "stable"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


