"""
FastAPI application for Multi-Location Practice Performance Dashboard
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from performance_analyzer import PerformanceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./multi_location_dashboard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Location(Base):
    """Database model for locations"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    location_id = Column(String, unique=True)
    location_name = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class LocationMetrics(Base):
    """Database model for location metrics"""
    __tablename__ = "location_metrics"
    
    id = Column(Integer, primary_key=True)
    location_id = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    patient_volume = Column(Integer)
    revenue_per_visit = Column(Float)
    no_show_rate = Column(Float)
    patient_satisfaction = Column(Float, nullable=True)
    provider_productivity = Column(Float)
    operating_costs = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Location Practice Performance Dashboard", version="1.0.0")
analyzer = PerformanceAnalyzer()


class LocationRequest(BaseModel):
    """Request to add location"""
    location_id: str
    location_name: str
    address: str


class MetricsRequest(BaseModel):
    """Request to add metrics"""
    location_id: str
    patient_volume: int
    revenue_per_visit: float
    no_show_rate: float
    patient_satisfaction: Optional[float] = None
    provider_productivity: float
    operating_costs: float


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Multi-Location Practice Performance Dashboard</h1><p>Use API endpoints</p>")


@app.post("/api/location")
async def add_location(request: LocationRequest):
    """Add location"""
    try:
        db = SessionLocal()
        location = Location(
            location_id=request.location_id,
            location_name=request.location_name,
            address=request.address
        )
        db.add(location)
        db.commit()
        db.close()
        return {"message": "Location added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/metrics")
async def add_metrics(request: MetricsRequest):
    """Add location metrics"""
    try:
        db = SessionLocal()
        metrics = LocationMetrics(
            location_id=request.location_id,
            patient_volume=request.patient_volume,
            revenue_per_visit=request.revenue_per_visit,
            no_show_rate=request.no_show_rate,
            patient_satisfaction=request.patient_satisfaction,
            provider_productivity=request.provider_productivity,
            operating_costs=request.operating_costs
        )
        db.add(metrics)
        db.commit()
        db.close()
        return {"message": "Metrics added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard")
async def get_dashboard():
    """Get comparative performance dashboard"""
    try:
        db = SessionLocal()
        locations = db.query(Location).all()
        metrics = db.query(LocationMetrics).all()
        db.close()
        
        return analyzer.calculate_comparative_metrics(locations, metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


