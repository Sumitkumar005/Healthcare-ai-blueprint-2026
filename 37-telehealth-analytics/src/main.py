"""
FastAPI application for Telehealth Utilization Analytics
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from analytics_engine import TelehealthAnalytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./telehealth_analytics.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Visit(Base):
    """Database model for visits"""
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True)
    visit_id = Column(String, unique=True)
    patient_id = Column(String)
    provider_id = Column(String)
    visit_type = Column(String)  # new_patient, follow_up, urgent
    modality = Column(String)  # telehealth, in_person
    visit_date = Column(DateTime)
    duration_minutes = Column(Integer)
    no_show = Column(Boolean, default=False)
    patient_satisfaction = Column(Float, nullable=True)
    revenue = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telehealth Utilization Analytics", version="1.0.0")
analytics = TelehealthAnalytics()


class VisitRequest(BaseModel):
    """Request to add visit"""
    visit_id: str
    patient_id: str
    provider_id: str
    visit_type: str
    modality: str
    visit_date: str
    duration_minutes: int
    no_show: bool = False
    patient_satisfaction: Optional[float] = None
    revenue: float


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Telehealth Utilization Analytics</h1><p>Use API endpoints</p>")


@app.post("/api/visit")
async def add_visit(request: VisitRequest):
    """Add visit data"""
    try:
        db = SessionLocal()
        visit = Visit(
            visit_id=request.visit_id,
            patient_id=request.patient_id,
            provider_id=request.provider_id,
            visit_type=request.visit_type,
            modality=request.modality,
            visit_date=datetime.fromisoformat(request.visit_date),
            duration_minutes=request.duration_minutes,
            no_show=request.no_show,
            patient_satisfaction=request.patient_satisfaction,
            revenue=request.revenue
        )
        db.add(visit)
        db.commit()
        db.close()
        return {"message": "Visit added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get telehealth utilization analytics"""
    try:
        db = SessionLocal()
        visits = db.query(Visit).all()
        db.close()
        
        return analytics.calculate_metrics(visits)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


