"""
FastAPI application for No-Show Prediction Model
"""
import os
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

from prediction_model import NoShowPredictor
from intervention_engine import InterventionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./no_show_prediction.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Appointment(Base):
    """Database model for appointments"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    appointment_date = Column(DateTime)
    appointment_type = Column(String)
    day_of_week = Column(String)
    time_of_day = Column(String)
    lead_time_days = Column(Integer)
    no_show = Column(Boolean)
    predicted_risk = Column(Float, nullable=True)
    intervention_applied = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="No-Show Prediction Model",
    description="ML-powered no-show prediction with intervention triggers",
    version="1.0.0"
)

# Initialize components
predictor = NoShowPredictor()
intervention_engine = InterventionEngine()


class PredictionRequest(BaseModel):
    """Request for no-show prediction"""
    patient_id: str
    appointment_date: str
    appointment_type: str
    day_of_week: str
    time_of_day: str
    lead_time_days: int
    patient_history: Optional[dict] = None


class PredictionResponse(BaseModel):
    """Prediction response"""
    patient_id: str
    appointment_date: str
    risk_score: float
    risk_level: str
    interventions: List[str]
    recommendations: List[str]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard"""
    return HTMLResponse(content="""
    <html>
        <head><title>No-Show Prediction Dashboard</title></head>
        <body>
            <h1>No-Show Prediction Model</h1>
            <p>Use API endpoints to interact with the prediction system.</p>
            <ul>
                <li>POST /api/data/upload - Upload historical data</li>
                <li>POST /api/predict - Predict no-show risk</li>
                <li>GET /api/dashboard - Get analytics</li>
            </ul>
        </body>
    </html>
    """)


@app.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload historical appointment data (CSV)"""
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        logger.info(f"Uploaded {len(df)} records")
        
        # Validate columns
        required_cols = ['patient_id', 'appointment_date', 'appointment_type', 'no_show']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        
        # Process and store
        db = SessionLocal()
        count = 0
        for _, row in df.iterrows():
            appointment = Appointment(
                patient_id=str(row['patient_id']),
                appointment_date=pd.to_datetime(row['appointment_date']),
                appointment_type=str(row.get('appointment_type', 'Unknown')),
                day_of_week=pd.to_datetime(row['appointment_date']).strftime('%A'),
                time_of_day=str(row.get('time_of_day', 'Unknown')),
                lead_time_days=int(row.get('lead_time_days', 0)),
                no_show=bool(row['no_show'])
            )
            db.add(appointment)
            count += 1
        
        db.commit()
        db.close()
        
        # Train model
        predictor.train_model(df)
        
        return {
            "message": f"Successfully uploaded {count} records",
            "records_processed": count
        }
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_no_show(request: PredictionRequest):
    """Predict no-show risk for an appointment"""
    try:
        # Make prediction
        risk_score = predictor.predict(
            appointment_type=request.appointment_type,
            day_of_week=request.day_of_week,
            time_of_day=request.time_of_day,
            lead_time_days=request.lead_time_days,
            patient_history=request.patient_history or {}
        )
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "High"
        elif risk_score >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Get interventions
        interventions = intervention_engine.get_interventions(risk_score, risk_level)
        recommendations = intervention_engine.get_recommendations(risk_score)
        
        # Store prediction
        db = SessionLocal()
        appointment = Appointment(
            patient_id=request.patient_id,
            appointment_date=datetime.fromisoformat(request.appointment_date),
            appointment_type=request.appointment_type,
            day_of_week=request.day_of_week,
            time_of_day=request.time_of_day,
            lead_time_days=request.lead_time_days,
            no_show=None,  # Unknown until appointment
            predicted_risk=risk_score,
            intervention_applied=", ".join(interventions)
        )
        db.add(appointment)
        db.commit()
        db.close()
        
        return PredictionResponse(
            patient_id=request.patient_id,
            appointment_date=request.appointment_date,
            risk_score=risk_score,
            risk_level=risk_level,
            interventions=interventions,
            recommendations=recommendations
        )
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_dashboard():
    """Get analytics dashboard data"""
    try:
        db = SessionLocal()
        appointments = db.query(Appointment).all()
        db.close()
        
        if not appointments:
            return {
                "total_appointments": 0,
                "no_show_rate": 0,
                "by_day": {},
                "by_time": {},
                "risk_distribution": {}
            }
        
        # Calculate metrics
        total = len(appointments)
        no_shows = sum(1 for a in appointments if a.no_show is True)
        no_show_rate = (no_shows / total * 100) if total > 0 else 0
        
        # By day of week
        by_day = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_appts = [a for a in appointments if a.day_of_week == day]
            day_no_shows = sum(1 for a in day_appts if a.no_show is True)
            by_day[day] = {
                "total": len(day_appts),
                "no_shows": day_no_shows,
                "rate": (day_no_shows / len(day_appts) * 100) if day_appts else 0
            }
        
        # Risk distribution
        risk_dist = {"High": 0, "Medium": 0, "Low": 0}
        for appt in appointments:
            if appt.predicted_risk:
                if appt.predicted_risk >= 0.7:
                    risk_dist["High"] += 1
                elif appt.predicted_risk >= 0.4:
                    risk_dist["Medium"] += 1
                else:
                    risk_dist["Low"] += 1
        
        return {
            "total_appointments": total,
            "no_show_rate": round(no_show_rate, 2),
            "by_day": by_day,
            "risk_distribution": risk_dist
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



