"""
FastAPI application for Patient Financial Counseling Automation
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from eligibility_checker import EligibilityChecker
from program_matcher import ProgramMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./financial_counseling.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PatientFinancial(Base):
    """Database model for patient financial data"""
    __tablename__ = "patient_financial"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    income = Column(Float)
    household_size = Column(Integer)
    insurance_status = Column(String)
    assets = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssistanceProgram(Base):
    """Database model for assistance programs"""
    __tablename__ = "assistance_programs"
    
    id = Column(Integer, primary_key=True)
    program_name = Column(String)
    program_type = Column(String)  # charity_care, medicaid, pharmaceutical, nonprofit
    income_threshold = Column(Float, nullable=True)
    household_size_limit = Column(Integer, nullable=True)
    eligibility_criteria = Column(Text)  # JSON string
    contact_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EligibilityMatch(Base):
    """Database model for eligibility matches"""
    __tablename__ = "eligibility_matches"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    program_id = Column(Integer)
    match_score = Column(Float)
    eligibility_status = Column(String)  # eligible, potentially_eligible, not_eligible
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Financial Counseling Automation", version="1.0.0")
eligibility_checker = EligibilityChecker()
program_matcher = ProgramMatcher()


class PatientFinancialRequest(BaseModel):
    """Request to add patient financial data"""
    patient_id: str
    income: float
    household_size: int
    insurance_status: str
    assets: Optional[float] = None


class ProgramRequest(BaseModel):
    """Request to add assistance program"""
    program_name: str
    program_type: str
    income_threshold: Optional[float] = None
    household_size_limit: Optional[int] = None
    eligibility_criteria: dict
    contact_info: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Patient Financial Counseling Automation</h1><p>Use API endpoints</p>")


@app.post("/api/patient/financial")
async def add_patient_financial(request: PatientFinancialRequest):
    """Add patient financial data"""
    try:
        db = SessionLocal()
        patient = PatientFinancial(
            patient_id=request.patient_id,
            income=request.income,
            household_size=request.household_size,
            insurance_status=request.insurance_status,
            assets=request.assets
        )
        db.add(patient)
        db.commit()
        db.close()
        return {"message": "Patient financial data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/program")
async def add_program(request: ProgramRequest):
    """Add assistance program"""
    try:
        import json
        db = SessionLocal()
        program = AssistanceProgram(
            program_name=request.program_name,
            program_type=request.program_type,
            income_threshold=request.income_threshold,
            household_size_limit=request.household_size_limit,
            eligibility_criteria=json.dumps(request.eligibility_criteria),
            contact_info=request.contact_info
        )
        db.add(program)
        db.commit()
        db.close()
        return {"message": "Program added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/eligibility/check/{patient_id}")
async def check_eligibility(patient_id: str):
    """Check patient eligibility for assistance programs"""
    try:
        import json
        db = SessionLocal()
        
        patient = db.query(PatientFinancial).filter(PatientFinancial.patient_id == patient_id).first()
        if not patient:
            db.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        programs = db.query(AssistanceProgram).all()
        
        matches = []
        for program in programs:
            eligibility_criteria = json.loads(program.eligibility_criteria)
            match_score, status = eligibility_checker.check_eligibility(
                patient_data={
                    "income": patient.income,
                    "household_size": patient.household_size,
                    "insurance_status": patient.insurance_status,
                    "assets": patient.assets
                },
                program_criteria=eligibility_criteria,
                program_threshold=program.income_threshold
            )
            
            if match_score > 0:
                match = EligibilityMatch(
                    patient_id=patient_id,
                    program_id=program.id,
                    match_score=match_score,
                    eligibility_status=status
                )
                db.add(match)
                matches.append({
                    "program_name": program.program_name,
                    "program_type": program.program_type,
                    "match_score": round(match_score, 2),
                    "eligibility_status": status,
                    "contact_info": program.contact_info
                })
        
        db.commit()
        db.close()
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "patient_id": patient_id,
            "matches": matches,
            "total_matches": len(matches)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/revenue-recovery")
async def get_revenue_recovery():
    """Get revenue recovery metrics"""
    try:
        db = SessionLocal()
        matches = db.query(EligibilityMatch).filter(
            EligibilityMatch.eligibility_status == "eligible"
        ).all()
        db.close()
        
        return {
            "total_eligible_patients": len(set(m.patient_id for m in matches)),
            "total_programs_matched": len(matches),
            "estimated_recovery": len(matches) * 5000  # Simplified estimate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

