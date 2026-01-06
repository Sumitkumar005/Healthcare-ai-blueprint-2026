"""
FastAPI application for Clinical Quality Metrics Dashboard
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from metrics_calculator import QualityMetricsCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./quality_metrics.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PatientMetric(Base):
    """Database model for patient metrics"""
    __tablename__ = "patient_metrics"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    metric_type = Column(String)  # HbA1c, BP, Mammogram, etc.
    value = Column(Float, nullable=True)
    test_date = Column(Date)
    meets_target = Column(Integer)  # 0 or 1
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinical Quality Metrics Dashboard", version="1.0.0")
calculator = QualityMetricsCalculator()


class MetricRequest(BaseModel):
    """Request to add metric"""
    patient_id: str
    metric_type: str
    value: float = None
    test_date: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Clinical Quality Metrics Dashboard</h1><p>Use API endpoints</p>")


@app.post("/api/metric")
async def add_metric(request: MetricRequest):
    """Add patient metric"""
    try:
        db = SessionLocal()
        metric = PatientMetric(
            patient_id=request.patient_id,
            metric_type=request.metric_type,
            value=request.value,
            test_date=datetime.fromisoformat(request.test_date).date(),
            meets_target=calculator.check_target(request.metric_type, request.value) if request.value else 0
        )
        db.add(metric)
        db.commit()
        db.close()
        return {"message": "Metric added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_dashboard():
    """Get quality metrics dashboard"""
    try:
        db = SessionLocal()
        metrics = db.query(PatientMetric).all()
        db.close()
        
        dashboard = calculator.calculate_dashboard(metrics)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

