"""
FastAPI application for Patient Portal Usage Optimizer
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from usage_analyzer import UsageAnalyzer
from campaign_manager import CampaignManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./portal_optimizer.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    """Database model for patients"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    email = Column(String)
    phone = Column(String)
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PortalUsage(Base):
    """Database model for portal usage"""
    __tablename__ = "portal_usage"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    activated = Column(Boolean, default=False)
    activation_date = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    feature_messaging = Column(Boolean, default=False)
    feature_bill_pay = Column(Boolean, default=False)
    feature_scheduling = Column(Boolean, default=False)
    login_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    """Database model for campaigns"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    target_segment = Column(String)  # inactive, low_usage, etc.
    channel = Column(String)  # email, sms, in_office
    message = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    status = Column(String)  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)


class CampaignResult(Base):
    """Database model for campaign results"""
    __tablename__ = "campaign_results"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer)
    patient_id = Column(String)
    sent = Column(Boolean, default=False)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    activated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Patient Portal Usage Optimizer",
    description="Optimize patient portal activation and engagement",
    version="1.0.0"
)

usage_analyzer = UsageAnalyzer()
campaign_manager = CampaignManager()


class PatientRequest(BaseModel):
    """Request to add patient"""
    patient_id: str
    email: str
    phone: str
    age: Optional[int] = None


class UsageUpdateRequest(BaseModel):
    """Request to update portal usage"""
    patient_id: str
    activated: Optional[bool] = None
    feature_messaging: Optional[bool] = None
    feature_bill_pay: Optional[bool] = None
    feature_scheduling: Optional[bool] = None


class CampaignRequest(BaseModel):
    """Request to create campaign"""
    name: str
    target_segment: str
    channel: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Patient Portal Usage Optimizer</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .section { margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>📱 Patient Portal Usage Optimizer</h1>
            <div class="section">
                <h2>API Endpoints</h2>
                <ul>
                    <li>POST /api/patient - Add patient</li>
                    <li>POST /api/usage - Update portal usage</li>
                    <li>GET /api/analytics - Get usage analytics</li>
                    <li>POST /api/campaign - Create campaign</li>
                    <li>GET /api/campaign/{id}/results - Get campaign results</li>
                    <li>GET /api/roi - Calculate ROI</li>
                </ul>
            </div>
        </body>
    </html>
    """)


@app.post("/api/patient")
async def add_patient(request: PatientRequest):
    """Add a new patient"""
    try:
        logger.info(f"Adding patient: {request.patient_id}")
        
        db = SessionLocal()
        
        # Check if patient exists
        existing = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Patient already exists")
        
        patient = Patient(
            patient_id=request.patient_id,
            email=request.email,
            phone=request.phone,
            age=request.age
        )
        
        db.add(patient)
        
        # Create portal usage record
        usage = PortalUsage(patient_id=request.patient_id)
        db.add(usage)
        
        db.commit()
        db.close()
        
        return {"message": "Patient added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding patient: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/usage")
async def update_usage(request: UsageUpdateRequest):
    """Update portal usage data"""
    try:
        db = SessionLocal()
        
        usage = db.query(PortalUsage).filter(
            PortalUsage.patient_id == request.patient_id
        ).first()
        
        if not usage:
            db.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        if request.activated is not None:
            usage.activated = request.activated
            if request.activated and not usage.activation_date:
                usage.activation_date = datetime.utcnow()
        
        if request.feature_messaging is not None:
            usage.feature_messaging = request.feature_messaging
        
        if request.feature_bill_pay is not None:
            usage.feature_bill_pay = request.feature_bill_pay
        
        if request.feature_scheduling is not None:
            usage.feature_scheduling = request.feature_scheduling
        
        usage.last_login = datetime.utcnow()
        usage.login_count += 1
        
        db.commit()
        db.close()
        
        return {"message": "Usage updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get portal usage analytics"""
    try:
        db = SessionLocal()
        patients = db.query(Patient).all()
        usage_records = db.query(PortalUsage).all()
        db.close()
        
        analytics = usage_analyzer.calculate_analytics(patients, usage_records)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/campaign")
async def create_campaign(request: CampaignRequest):
    """Create a new activation campaign"""
    try:
        logger.info(f"Creating campaign: {request.name}")
        
        db = SessionLocal()
        
        campaign = Campaign(
            name=request.name,
            target_segment=request.target_segment,
            channel=request.channel,
            message=request.message,
            start_date=datetime.utcnow(),
            status="active"
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Get target patients
        target_patients = campaign_manager.get_target_patients(
            request.target_segment,
            db.query(Patient).all(),
            db.query(PortalUsage).all()
        )
        
        # Create campaign results
        for patient in target_patients:
            result = CampaignResult(
                campaign_id=campaign.id,
                patient_id=patient["patient_id"],
                sent=True
            )
            db.add(result)
        
        db.commit()
        db.close()
        
        return {
            "message": "Campaign created successfully",
            "campaign_id": campaign.id,
            "patients_targeted": len(target_patients)
        }
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaign/{campaign_id}/results")
async def get_campaign_results(campaign_id: int):
    """Get campaign results"""
    try:
        db = SessionLocal()
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            db.close()
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        results = db.query(CampaignResult).filter(
            CampaignResult.campaign_id == campaign_id
        ).all()
        
        db.close()
        
        total_sent = len(results)
        total_opened = sum(1 for r in results if r.opened)
        total_clicked = sum(1 for r in results if r.clicked)
        total_activated = sum(1 for r in results if r.activated)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "total_activated": total_activated,
            "open_rate": round((total_opened / total_sent * 100) if total_sent > 0 else 0, 2),
            "click_rate": round((total_clicked / total_sent * 100) if total_sent > 0 else 0, 2),
            "activation_rate": round((total_activated / total_sent * 100) if total_sent > 0 else 0, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/roi")
async def calculate_roi():
    """Calculate ROI metrics"""
    try:
        db = SessionLocal()
        patients = db.query(Patient).count()
        usage_records = db.query(PortalUsage).all()
        db.close()
        
        activated_count = sum(1 for u in usage_records if u.activated)
        activation_rate = (activated_count / patients * 100) if patients > 0 else 0
        
        # Estimate cost savings (simplified calculation)
        # Assume each portal activation saves 2 phone calls per month
        # Each phone call takes 5 minutes of staff time
        # Staff cost: $25/hour
        monthly_savings = activated_count * 2 * 5 / 60 * 25
        annual_savings = monthly_savings * 12
        
        # Portal cost estimate: $2 per patient per month
        portal_cost = patients * 2 * 12
        
        roi = ((annual_savings - portal_cost) / portal_cost * 100) if portal_cost > 0 else 0
        
        return {
            "total_patients": patients,
            "activated_patients": activated_count,
            "activation_rate": round(activation_rate, 2),
            "estimated_annual_savings": round(annual_savings, 2),
            "estimated_portal_cost": round(portal_cost, 2),
            "roi_percentage": round(roi, 2)
        }
    except Exception as e:
        logger.error(f"Error calculating ROI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


