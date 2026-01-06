"""
FastAPI application for Vaccine Inventory and Administration Tracker
"""
import logging
from typing import Optional
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from inventory_manager import VaccineInventoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./vaccine_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class VaccineInventory(Base):
    """Database model for vaccine inventory"""
    __tablename__ = "vaccine_inventory"
    
    id = Column(Integer, primary_key=True)
    vaccine_type = Column(String)
    lot_number = Column(String)
    expiration_date = Column(Date)
    quantity = Column(Integer)
    storage_location = Column(String)
    temperature_requirement = Column(String, nullable=True)
    received_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class VaccineAdministration(Base):
    """Database model for vaccine administrations"""
    __tablename__ = "vaccine_administrations"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    vaccine_type = Column(String)
    lot_number = Column(String)
    administration_date = Column(Date)
    site = Column(String)  # left_arm, right_arm, etc.
    route = Column(String)  # IM, SC, etc.
    administrator_name = Column(String)
    vis_provided = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TemperatureLog(Base):
    """Database model for temperature logs"""
    __tablename__ = "temperature_logs"
    
    id = Column(Integer, primary_key=True)
    storage_location = Column(String)
    temperature = Column(Float)
    log_date = Column(DateTime, default=datetime.utcnow)
    excursion = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vaccine Inventory and Administration Tracker", version="1.0.0")
inventory_manager = VaccineInventoryManager()


class InventoryRequest(BaseModel):
    """Request to add inventory"""
    vaccine_type: str
    lot_number: str
    expiration_date: str
    quantity: int
    storage_location: str
    temperature_requirement: Optional[str] = None


class AdministrationRequest(BaseModel):
    """Request to log administration"""
    patient_id: str
    vaccine_type: str
    lot_number: str
    administration_date: str
    site: str
    route: str
    administrator_name: str
    vis_provided: bool = False


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Vaccine Inventory and Administration Tracker</h1><p>Use API endpoints</p>")


@app.post("/api/inventory")
async def add_inventory(request: InventoryRequest):
    """Add vaccine inventory"""
    try:
        db = SessionLocal()
        inventory = VaccineInventory(
            vaccine_type=request.vaccine_type,
            lot_number=request.lot_number,
            expiration_date=datetime.fromisoformat(request.expiration_date).date(),
            quantity=request.quantity,
            storage_location=request.storage_location,
            temperature_requirement=request.temperature_requirement,
            received_date=date.today()
        )
        db.add(inventory)
        db.commit()
        db.close()
        return {"message": "Inventory added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/administration")
async def log_administration(request: AdministrationRequest):
    """Log vaccine administration"""
    try:
        db = SessionLocal()
        
        # Check inventory
        inventory = db.query(VaccineInventory).filter(
            VaccineInventory.vaccine_type == request.vaccine_type,
            VaccineInventory.lot_number == request.lot_number,
            VaccineInventory.quantity > 0
        ).first()
        
        if not inventory:
            db.close()
            raise HTTPException(status_code=400, detail="Vaccine not available in inventory")
        
        # Reduce quantity
        inventory.quantity -= 1
        
        # Log administration
        administration = VaccineAdministration(
            patient_id=request.patient_id,
            vaccine_type=request.vaccine_type,
            lot_number=request.lot_number,
            administration_date=datetime.fromisoformat(request.administration_date).date(),
            site=request.site,
            route=request.route,
            administrator_name=request.administrator_name,
            vis_provided=request.vis_provided
        )
        db.add(administration)
        db.commit()
        db.close()
        
        return {"message": "Administration logged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts():
    """Get expiration and temperature alerts"""
    try:
        db = SessionLocal()
        inventory = db.query(VaccineInventory).all()
        temperature_logs = db.query(TemperatureLog).order_by(
            TemperatureLog.log_date.desc()
        ).limit(100).all()
        db.close()
        
        alerts = []
        today = date.today()
        
        # Expiration alerts
        for inv in inventory:
            if inv.expiration_date:
                days_until = (inv.expiration_date - today).days
                if days_until <= 30:
                    alerts.append({
                        "type": "expiration",
                        "vaccine_type": inv.vaccine_type,
                        "lot_number": inv.lot_number,
                        "expiration_date": inv.expiration_date.isoformat(),
                        "days_until": days_until,
                        "alert_level": "High" if days_until <= 7 else "Medium" if days_until <= 14 else "Low"
                    })
        
        # Temperature excursion alerts
        for log in temperature_logs:
            if log.excursion:
                alerts.append({
                    "type": "temperature_excursion",
                    "storage_location": log.storage_location,
                    "temperature": log.temperature,
                    "log_date": log.log_date.isoformat(),
                    "alert_level": "High"
                })
        
        return {"alerts": alerts, "total": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/state-registry-export")
async def export_state_registry():
    """Export data for state registry"""
    try:
        db = SessionLocal()
        administrations = db.query(VaccineAdministration).all()
        db.close()
        
        # Format for state registry (simplified)
        export_data = []
        for admin in administrations:
            export_data.append({
                "patient_id": admin.patient_id,
                "vaccine_type": admin.vaccine_type,
                "lot_number": admin.lot_number,
                "administration_date": admin.administration_date.isoformat(),
                "site": admin.site,
                "route": admin.route,
                "administrator": admin.administrator_name
            })
        
        return {
            "export_date": datetime.now().isoformat(),
            "total_administrations": len(export_data),
            "data": export_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


