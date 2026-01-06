"""
FastAPI application for Patient Satisfaction Survey Analyzer
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

from analyzer import SurveyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./satisfaction_surveys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SurveyResponse(Base):
    """Database model for survey responses"""
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    category = Column(String)
    score = Column(Float)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Satisfaction Survey Analyzer", version="1.0.0")
analyzer = SurveyAnalyzer()


class SurveyRequest(BaseModel):
    """Request to analyze survey"""
    patient_id: str
    category: str
    score: float
    comment: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Patient Satisfaction Survey Analyzer</h1><p>Use API endpoints</p>")


@app.post("/api/survey")
async def add_survey(request: SurveyRequest):
    """Add survey response"""
    try:
        db = SessionLocal()
        response = SurveyResponse(
            patient_id=request.patient_id,
            category=request.category,
            score=request.score,
            comment=request.comment
        )
        db.add(response)
        db.commit()
        db.close()
        return {"message": "Survey response added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_surveys():
    """Analyze all survey responses"""
    try:
        db = SessionLocal()
        responses = db.query(SurveyResponse).all()
        db.close()
        
        analysis = analyzer.analyze(responses)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

