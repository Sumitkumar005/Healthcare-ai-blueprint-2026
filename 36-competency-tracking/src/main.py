"""
FastAPI application for Clinical Competency Tracking
"""
import logging
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from competency_manager import CompetencyManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./competency_tracking.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Nurse(Base):
    """Database model for nurses"""
    __tablename__ = "nurses"
    
    id = Column(Integer, primary_key=True)
    nurse_id = Column(String, unique=True)
    name = Column(String)
    specialty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Competency(Base):
    """Database model for competencies"""
    __tablename__ = "competencies"
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String)
    specialty = Column(String)
    required_frequency = Column(String)  # annual, biennial
    validation_method = Column(String)  # observation, simulation, test
    created_at = Column(DateTime, default=datetime.utcnow)


class CompetencyValidation(Base):
    """Database model for competency validations"""
    __tablename__ = "competency_validations"
    
    id = Column(Integer, primary_key=True)
    nurse_id = Column(String)
    competency_id = Column(Integer)
    validation_date = Column(Date)
    validator_name = Column(String)
    proficiency_level = Column(String)  # proficient, needs_improvement, not_proficient
    next_due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinical Competency Tracking", version="1.0.0")
competency_manager = CompetencyManager()


class NurseRequest(BaseModel):
    """Request to add nurse"""
    nurse_id: str
    name: str
    specialty: str


class CompetencyRequest(BaseModel):
    """Request to add competency"""
    skill_name: str
    specialty: str
    required_frequency: str
    validation_method: str


class ValidationRequest(BaseModel):
    """Request to log validation"""
    nurse_id: str
    competency_id: int
    validation_date: str
    validator_name: str
    proficiency_level: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Clinical Competency Tracking</h1><p>Use API endpoints</p>")


@app.post("/api/nurse")
async def add_nurse(request: NurseRequest):
    """Add nurse"""
    try:
        db = SessionLocal()
        nurse = Nurse(
            nurse_id=request.nurse_id,
            name=request.name,
            specialty=request.specialty
        )
        db.add(nurse)
        db.commit()
        db.close()
        return {"message": "Nurse added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/competency")
async def add_competency(request: CompetencyRequest):
    """Add competency definition"""
    try:
        db = SessionLocal()
        competency = Competency(
            skill_name=request.skill_name,
            specialty=request.specialty,
            required_frequency=request.required_frequency,
            validation_method=request.validation_method
        )
        db.add(competency)
        db.commit()
        db.close()
        return {"message": "Competency added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validation")
async def log_validation(request: ValidationRequest):
    """Log competency validation"""
    try:
        db = SessionLocal()
        
        competency = db.query(Competency).filter(Competency.id == request.competency_id).first()
        if not competency:
            db.close()
            raise HTTPException(status_code=404, detail="Competency not found")
        
        validation_date = datetime.fromisoformat(request.validation_date).date()
        next_due = competency_manager.calculate_next_due(
            competency.required_frequency,
            validation_date
        )
        
        validation = CompetencyValidation(
            nurse_id=request.nurse_id,
            competency_id=request.competency_id,
            validation_date=validation_date,
            validator_name=request.validator_name,
            proficiency_level=request.proficiency_level,
            next_due_date=next_due
        )
        
        db.add(validation)
        db.commit()
        db.close()
        
        return {
            "message": "Validation logged successfully",
            "next_due_date": next_due.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts():
    """Get competency expiration alerts"""
    try:
        db = SessionLocal()
        validations = db.query(CompetencyValidation).all()
        db.close()
        
        alerts = []
        today = date.today()
        
        for validation in validations:
            if validation.next_due_date:
                days_until = (validation.next_due_date - today).days
                if days_until <= 90:
                    alerts.append({
                        "nurse_id": validation.nurse_id,
                        "competency_id": validation.competency_id,
                        "next_due_date": validation.next_due_date.isoformat(),
                        "days_until": days_until,
                        "alert_level": "High" if days_until <= 30 else "Medium" if days_until <= 60 else "Low"
                    })
        
        return {"alerts": alerts, "total": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance-report")
async def get_compliance_report():
    """Generate compliance report"""
    try:
        db = SessionLocal()
        nurses = db.query(Nurse).all()
        validations = db.query(CompetencyValidation).all()
        db.close()
        
        today = date.today()
        expired = [v for v in validations if v.next_due_date and v.next_due_date < today]
        due_soon = [v for v in validations if v.next_due_date and 0 <= (v.next_due_date - today).days <= 30]
        
        return {
            "report_date": datetime.now().isoformat(),
            "total_nurses": len(nurses),
            "total_validations": len(validations),
            "expired_count": len(expired),
            "due_soon_count": len(due_soon),
            "compliance_rate": round(((len(validations) - len(expired)) / len(validations) * 100) if validations else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


