"""
FastAPI application for Clinical Trial Patient Matching
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from matcher import TrialMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./clinical_trials.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ClinicalTrial(Base):
    """Database model for clinical trials"""
    __tablename__ = "clinical_trials"
    
    id = Column(Integer, primary_key=True)
    trial_id = Column(String, unique=True)
    trial_name = Column(String)
    condition = Column(String)
    inclusion_criteria = Column(Text)  # JSON string
    exclusion_criteria = Column(Text)  # JSON string
    location = Column(String)
    compensation = Column(String, nullable=True)
    contact_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    """Database model for patients"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    demographics = Column(Text)  # JSON string
    diagnoses = Column(Text)  # JSON string
    medications = Column(Text)  # JSON string
    medical_history = Column(Text)  # JSON string
    lab_values = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class Match(Base):
    """Database model for trial matches"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    trial_id = Column(String)
    match_score = Column(Float)
    match_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinical Trial Patient Matching", version="1.0.0")
matcher = TrialMatcher()


class TrialRequest(BaseModel):
    """Request to add trial"""
    trial_id: str
    trial_name: str
    condition: str
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    location: str
    compensation: Optional[str] = None
    contact_info: Optional[str] = None


class PatientRequest(BaseModel):
    """Request to add patient"""
    patient_id: str
    demographics: dict
    diagnoses: List[str]
    medications: List[str]
    medical_history: dict
    lab_values: Optional[dict] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Clinical Trial Patient Matching</h1><p>Use API endpoints</p>")


@app.post("/api/trial")
async def add_trial(request: TrialRequest):
    """Add clinical trial"""
    try:
        import json
        db = SessionLocal()
        trial = ClinicalTrial(
            trial_id=request.trial_id,
            trial_name=request.trial_name,
            condition=request.condition,
            inclusion_criteria=json.dumps(request.inclusion_criteria),
            exclusion_criteria=json.dumps(request.exclusion_criteria),
            location=request.location,
            compensation=request.compensation,
            contact_info=request.contact_info
        )
        db.add(trial)
        db.commit()
        db.close()
        return {"message": "Trial added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patient")
async def add_patient(request: PatientRequest):
    """Add patient"""
    try:
        import json
        db = SessionLocal()
        patient = Patient(
            patient_id=request.patient_id,
            demographics=json.dumps(request.demographics),
            diagnoses=json.dumps(request.diagnoses),
            medications=json.dumps(request.medications),
            medical_history=json.dumps(request.medical_history),
            lab_values=json.dumps(request.lab_values) if request.lab_values else None
        )
        db.add(patient)
        db.commit()
        db.close()
        return {"message": "Patient added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match/{patient_id}")
async def match_patient(patient_id: str):
    """Match patient to trials"""
    try:
        import json
        db = SessionLocal()
        
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            db.close()
            raise HTTPException(status_code=404, detail="Patient not found")
        
        trials = db.query(ClinicalTrial).all()
        
        matches = []
        for trial in trials:
            match_score, reason = matcher.match_patient_to_trial(
                patient_data={
                    "demographics": json.loads(patient.demographics),
                    "diagnoses": json.loads(patient.diagnoses),
                    "medications": json.loads(patient.medications),
                    "medical_history": json.loads(patient.medical_history),
                    "lab_values": json.loads(patient.lab_values) if patient.lab_values else {}
                },
                trial_data={
                    "inclusion_criteria": json.loads(trial.inclusion_criteria),
                    "exclusion_criteria": json.loads(trial.exclusion_criteria),
                    "condition": trial.condition
                }
            )
            
            if match_score > 0:
                match = Match(
                    patient_id=patient_id,
                    trial_id=trial.trial_id,
                    match_score=match_score,
                    match_reason=reason
                )
                db.add(match)
                matches.append({
                    "trial_id": trial.trial_id,
                    "trial_name": trial.trial_name,
                    "condition": trial.condition,
                    "match_score": round(match_score, 2),
                    "match_reason": reason,
                    "location": trial.location
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


