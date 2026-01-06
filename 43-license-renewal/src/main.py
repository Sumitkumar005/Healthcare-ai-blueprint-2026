"""
FastAPI application for Medical License Renewal Tracker
"""
import logging
from typing import Optional
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from renewal_manager import RenewalManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./license_renewal.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class License(Base):
    """Database model for licenses"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(String)
    license_type = Column(String)  # medical_license, dea, board_certification, etc.
    state = Column(String, nullable=True)
    license_number = Column(String)
    issue_date = Column(Date)
    expiration_date = Column(Date)
    renewal_requirements = Column(String, nullable=True)  # JSON string
    cme_required = Column(Float, default=0.0)
    cme_completed = Column(Float, default=0.0)
    status = Column(String, default="active")  # active, expired, pending_renewal
    created_at = Column(DateTime, default=datetime.utcnow)


class CMECredit(Base):
    """Database model for CME credits"""
    __tablename__ = "cme_credits"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(String)
    course_name = Column(String)
    credits = Column(Float)
    completion_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical License Renewal Tracker", version="1.0.0")
renewal_manager = RenewalManager()


class LicenseRequest(BaseModel):
    """Request to add license"""
    provider_id: str
    license_type: str
    state: Optional[str] = None
    license_number: str
    expiration_date: str
    cme_required: float = 0.0


class CMERequest(BaseModel):
    """Request to add CME credit"""
    provider_id: str
    course_name: str
    credits: float
    completion_date: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Medical License Renewal Tracker</h1><p>Use API endpoints</p>")


@app.post("/api/license")
async def add_license(request: LicenseRequest):
    """Add license"""
    try:
        db = SessionLocal()
        license_obj = License(
            provider_id=request.provider_id,
            license_type=request.license_type,
            state=request.state,
            license_number=request.license_number,
            expiration_date=datetime.fromisoformat(request.expiration_date).date(),
            cme_required=request.cme_required
        )
        db.add(license_obj)
        db.commit()
        db.close()
        return {"message": "License added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cme")
async def add_cme(request: CMERequest):
    """Add CME credit"""
    try:
        db = SessionLocal()
        cme = CMECredit(
            provider_id=request.provider_id,
            course_name=request.course_name,
            credits=request.credits,
            completion_date=datetime.fromisoformat(request.completion_date).date()
        )
        db.add(cme)
        
        # Update license CME completed
        licenses = db.query(License).filter(License.provider_id == request.provider_id).all()
        for lic in licenses:
            total_cme = sum(
                c.credits for c in db.query(CMECredit).filter(
                    CMECredit.provider_id == request.provider_id
                ).all()
            )
            lic.cme_completed = total_cme
        
        db.commit()
        db.close()
        return {"message": "CME credit added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_renewal_alerts():
    """Get renewal alerts"""
    try:
        db = SessionLocal()
        licenses = db.query(License).all()
        db.close()
        
        alerts = []
        today = date.today()
        
        for lic in licenses:
            if lic.expiration_date:
                days_until = (lic.expiration_date - today).days
                if days_until <= 90:
                    alerts.append({
                        "provider_id": lic.provider_id,
                        "license_type": lic.license_type,
                        "state": lic.state,
                        "expiration_date": lic.expiration_date.isoformat(),
                        "days_until": days_until,
                        "alert_level": "High" if days_until <= 30 else "Medium" if days_until <= 60 else "Low",
                        "cme_status": f"{lic.cme_completed}/{lic.cme_required}" if lic.cme_required > 0 else "N/A"
                    })
        
        return {"alerts": alerts, "total": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/provider/{provider_id}/status")
async def get_provider_status(provider_id: str):
    """Get license status for provider"""
    try:
        db = SessionLocal()
        licenses = db.query(License).filter(License.provider_id == provider_id).all()
        cme_credits = db.query(CMECredit).filter(CMECredit.provider_id == provider_id).all()
        db.close()
        
        total_cme = sum(c.credits for c in cme_credits)
        
        return {
            "provider_id": provider_id,
            "licenses": [
                {
                    "license_type": lic.license_type,
                    "state": lic.state,
                    "expiration_date": lic.expiration_date.isoformat(),
                    "status": lic.status,
                    "cme_required": lic.cme_required,
                    "cme_completed": lic.cme_completed
                }
                for lic in licenses
            ],
            "total_cme_credits": total_cme
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


