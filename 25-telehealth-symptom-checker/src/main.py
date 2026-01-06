"""
FastAPI application for Telehealth Pre-Visit Symptom Checker
"""
import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from questionnaire_engine import QuestionnaireEngine
from hpi_generator import HPIGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./telehealth_symptom_checker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class QuestionnaireSession(Base):
    """Database model for questionnaire sessions"""
    __tablename__ = "questionnaire_sessions"
    
    session_id = Column(String, primary_key=True)
    patient_id = Column(String)
    appointment_id = Column(String)
    chief_complaint = Column(String)
    responses = Column(Text)  # JSON string
    hpi_summary = Column(Text)
    red_flags = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Telehealth Pre-Visit Symptom Checker",
    description="AI-powered pre-visit questionnaire for telehealth appointments",
    version="1.0.0"
)

# Initialize components
questionnaire_engine = QuestionnaireEngine()
hpi_generator = HPIGenerator()


# Pydantic models
class QuestionnaireStartRequest(BaseModel):
    """Request to start a new questionnaire"""
    patient_id: str
    appointment_id: str
    chief_complaint: str


class AnswerRequest(BaseModel):
    """Request to submit an answer"""
    session_id: str
    question_id: str
    answer: str


class QuestionnaireResponse(BaseModel):
    """Response from questionnaire engine"""
    session_id: str
    current_question: Optional[str]
    question_id: Optional[str]
    is_complete: bool
    red_flags: List[str]
    hpi_summary: Optional[str]


# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main questionnaire interface"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Telehealth Symptom Checker</title></head>
                <body>
                    <h1>Telehealth Pre-Visit Symptom Checker</h1>
                    <p>Frontend interface coming soon. Use API endpoints for now.</p>
                </body>
            </html>
            """,
            status_code=200
        )


@app.post("/api/questionnaire/start", response_model=QuestionnaireResponse)
async def start_questionnaire(request: QuestionnaireStartRequest):
    """
    Start a new questionnaire session
    """
    try:
        logger.info(f"Starting questionnaire for patient {request.patient_id}")
        
        # Create session in database
        db = SessionLocal()
        session_id = f"session_{datetime.utcnow().timestamp()}"
        
        session = QuestionnaireSession(
            session_id=session_id,
            patient_id=request.patient_id,
            appointment_id=request.appointment_id,
            chief_complaint=request.chief_complaint,
            responses="{}",
            red_flags="[]"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Start questionnaire engine
        result = questionnaire_engine.start_questionnaire(
            session_id=session_id,
            chief_complaint=request.chief_complaint
        )
        
        db.close()
        
        return QuestionnaireResponse(
            session_id=session_id,
            current_question=result.get("question"),
            question_id=result.get("question_id"),
            is_complete=False,
            red_flags=[],
            hpi_summary=None
        )
    except Exception as e:
        logger.error(f"Error starting questionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/questionnaire/answer", response_model=QuestionnaireResponse)
async def submit_answer(request: AnswerRequest):
    """
    Submit an answer to the current question
    """
    try:
        logger.info(f"Processing answer for session {request.session_id}")
        
        db = SessionLocal()
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Process answer and get next question
        result = questionnaire_engine.process_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
            chief_complaint=session.chief_complaint
        )
        
        # Update session with responses
        import json
        responses = json.loads(session.responses or "{}")
        responses[request.question_id] = request.answer
        session.responses = json.dumps(responses)
        
        # Check for red flags
        red_flags = result.get("red_flags", [])
        if red_flags:
            existing_flags = json.loads(session.red_flags or "[]")
            existing_flags.extend(red_flags)
            session.red_flags = json.dumps(list(set(existing_flags)))
        
        # If complete, generate HPI summary
        if result.get("is_complete"):
            hpi_summary = hpi_generator.generate_hpi(
                chief_complaint=session.chief_complaint,
                responses=responses,
                red_flags=red_flags
            )
            session.hpi_summary = hpi_summary
            session.completed_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return QuestionnaireResponse(
            session_id=request.session_id,
            current_question=result.get("question"),
            question_id=result.get("question_id"),
            is_complete=result.get("is_complete", False),
            red_flags=red_flags,
            hpi_summary=result.get("hpi_summary")
        )
    except Exception as e:
        logger.error(f"Error processing answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/summary/{session_id}")
async def get_summary(session_id: str):
    """
    Get the HPI summary for a completed questionnaire
    """
    try:
        db = SessionLocal()
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.hpi_summary:
            raise HTTPException(
                status_code=400,
                detail="Questionnaire not completed yet"
            )
        
        import json
        return {
            "session_id": session_id,
            "patient_id": session.patient_id,
            "appointment_id": session.appointment_id,
            "chief_complaint": session.chief_complaint,
            "hpi_summary": session.hpi_summary,
            "red_flags": json.loads(session.red_flags or "[]"),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/provider/dashboard")
async def get_provider_dashboard(
    appointment_date: Optional[str] = None,
    include_red_flags_only: bool = False
):
    """
    Get all pre-visit summaries for provider review
    """
    try:
        db = SessionLocal()
        query = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.hpi_summary.isnot(None)
        )
        
        if include_red_flags_only:
            query = query.filter(QuestionnaireSession.red_flags != "[]")
        
        sessions = query.order_by(
            QuestionnaireSession.created_at.desc()
        ).all()
        
        import json
        results = []
        for session in sessions:
            results.append({
                "session_id": session.session_id,
                "patient_id": session.patient_id,
                "appointment_id": session.appointment_id,
                "chief_complaint": session.chief_complaint,
                "hpi_summary": session.hpi_summary,
                "red_flags": json.loads(session.red_flags or "[]"),
                "has_red_flags": len(json.loads(session.red_flags or "[]")) > 0,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            })
        
        db.close()
        
        return {
            "total": len(results),
            "sessions": results
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



