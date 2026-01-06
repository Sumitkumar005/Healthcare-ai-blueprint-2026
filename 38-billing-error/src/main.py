"""
FastAPI application for Medical Billing Error Detection
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

from error_detector import BillingErrorDetector
from rules_engine import BillingRulesEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./billing_errors.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Claim(Base):
    """Database model for claims"""
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True)
    claim_id = Column(String, unique=True)
    provider_id = Column(String)
    patient_id = Column(String)
    diagnosis_codes = Column(String)  # JSON string
    procedure_codes = Column(String)  # JSON string
    modifiers = Column(String, nullable=True)  # JSON string
    revenue = Column(Float)
    errors_detected = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Billing Error Detection", version="1.0.0")
error_detector = BillingErrorDetector()
rules_engine = BillingRulesEngine()


class ClaimRequest(BaseModel):
    """Request to review claim"""
    claim_id: str
    provider_id: str
    patient_id: str
    diagnosis_codes: List[str]
    procedure_codes: List[str]
    modifiers: Optional[List[str]] = None
    revenue: float


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Medical Billing Error Detection</h1><p>Use API endpoints</p>")


@app.post("/api/claim/review")
async def review_claim(request: ClaimRequest):
    """Review claim for errors"""
    try:
        import json
        
        # Check rules-based errors
        rule_errors = rules_engine.check_claim(
            request.diagnosis_codes,
            request.procedure_codes,
            request.modifiers or []
        )
        
        # AI-powered analysis for complex cases
        ai_errors = error_detector.analyze_claim(
            request.diagnosis_codes,
            request.procedure_codes,
            request.modifiers or []
        )
        
        all_errors = rule_errors + ai_errors
        
        # Save claim
        db = SessionLocal()
        claim = Claim(
            claim_id=request.claim_id,
            provider_id=request.provider_id,
            patient_id=request.patient_id,
            diagnosis_codes=json.dumps(request.diagnosis_codes),
            procedure_codes=json.dumps(request.procedure_codes),
            modifiers=json.dumps(request.modifiers) if request.modifiers else None,
            revenue=request.revenue,
            errors_detected=json.dumps(all_errors)
        )
        db.add(claim)
        db.commit()
        db.close()
        
        return {
            "claim_id": request.claim_id,
            "errors_detected": len(all_errors),
            "errors": all_errors,
            "recommendation": "Review required" if all_errors else "Approve for submission"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get error pattern analytics"""
    try:
        import json
        db = SessionLocal()
        claims = db.query(Claim).all()
        db.close()
        
        total_claims = len(claims)
        claims_with_errors = sum(1 for c in claims if c.errors_detected)
        
        error_types = {}
        for claim in claims:
            if claim.errors_detected:
                errors = json.loads(claim.errors_detected)
                for error in errors:
                    error_type = error.get("type", "unknown")
                    error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_claims": total_claims,
            "claims_with_errors": claims_with_errors,
            "error_rate": round((claims_with_errors / total_claims * 100) if total_claims > 0 else 0, 2),
            "error_types": error_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


