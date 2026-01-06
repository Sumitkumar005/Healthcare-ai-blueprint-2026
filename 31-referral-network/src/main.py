"""
FastAPI application for Referral Network Performance Tracker
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from performance_tracker import ReferralPerformanceTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./referral_network.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Referral(Base):
    """Database model for referrals"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    specialist_name = Column(String)
    specialty = Column(String)
    referral_date = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    wait_time_days = Column(Integer, nullable=True)
    satisfaction_rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Referral Network Performance Tracker", version="1.0.0")
tracker = ReferralPerformanceTracker()


class ReferralRequest(BaseModel):
    """Request to add referral"""
    patient_id: str
    specialist_name: str
    specialty: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Referral Network Performance Tracker</h1><p>Use API endpoints</p>")


@app.post("/api/referral")
async def add_referral(request: ReferralRequest):
    """Add referral"""
    try:
        db = SessionLocal()
        referral = Referral(
            patient_id=request.patient_id,
            specialist_name=request.specialist_name,
            specialty=request.specialty
        )
        db.add(referral)
        db.commit()
        db.close()
        return {"message": "Referral added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_performance():
    """Get specialist performance metrics"""
    try:
        db = SessionLocal()
        referrals = db.query(Referral).all()
        db.close()
        
        performance = tracker.calculate_performance(referrals)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

