"""
FastAPI application for Medical Equipment Maintenance Tracker
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from equipment_manager import EquipmentManager
from maintenance_scheduler import MaintenanceScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./equipment_maintenance.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Equipment(Base):
    """Database model for equipment"""
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True)
    equipment_type = Column(String)
    serial_number = Column(String, unique=True)
    location = Column(String)
    purchase_date = Column(Date)
    maintenance_frequency = Column(String)  # annual, semi-annual, quarterly
    service_provider = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaintenanceRecord(Base):
    """Database model for maintenance records"""
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer)
    maintenance_date = Column(Date)
    technician = Column(String)
    results = Column(Text)
    next_due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Equipment Maintenance Tracker",
    description="Track equipment maintenance schedules and compliance",
    version="1.0.0"
)

equipment_manager = EquipmentManager()
maintenance_scheduler = MaintenanceScheduler()


class EquipmentRequest(BaseModel):
    """Request to add equipment"""
    equipment_type: str
    serial_number: str
    location: str
    purchase_date: str
    maintenance_frequency: str
    service_provider: Optional[str] = None


class MaintenanceRequest(BaseModel):
    """Request to log maintenance"""
    equipment_id: int
    maintenance_date: str
    technician: str
    results: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Equipment Maintenance Tracker</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .section { margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>🏥 Medical Equipment Maintenance Tracker</h1>
            <div class="section">
                <h2>API Endpoints</h2>
                <ul>
                    <li>POST /api/equipment - Add equipment</li>
                    <li>GET /api/equipment - List all equipment</li>
                    <li>POST /api/maintenance - Log maintenance</li>
                    <li>GET /api/alerts - Get maintenance alerts</li>
                    <li>GET /api/compliance-report - Generate compliance report</li>
                </ul>
            </div>
        </body>
    </html>
    """)


@app.post("/api/equipment")
async def add_equipment(request: EquipmentRequest):
    """Add new equipment to inventory"""
    try:
        logger.info(f"Adding equipment: {request.serial_number}")
        
        db = SessionLocal()
        
        # Check if serial number already exists
        existing = db.query(Equipment).filter(
            Equipment.serial_number == request.serial_number
        ).first()
        
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Equipment with this serial number already exists")
        
        equipment = Equipment(
            equipment_type=request.equipment_type,
            serial_number=request.serial_number,
            location=request.location,
            purchase_date=datetime.fromisoformat(request.purchase_date).date(),
            maintenance_frequency=request.maintenance_frequency,
            service_provider=request.service_provider
        )
        
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        db.close()
        
        return {
            "message": "Equipment added successfully",
            "equipment_id": equipment.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding equipment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/equipment")
async def get_equipment():
    """Get all equipment with maintenance status"""
    try:
        db = SessionLocal()
        equipment_list = db.query(Equipment).all()
        
        result = []
        for eq in equipment_list:
            # Get last maintenance
            last_maintenance = db.query(MaintenanceRecord).filter(
                MaintenanceRecord.equipment_id == eq.id
            ).order_by(MaintenanceRecord.maintenance_date.desc()).first()
            
            # Calculate next due date
            next_due = maintenance_scheduler.calculate_next_due(
                eq.maintenance_frequency,
                last_maintenance.next_due_date if last_maintenance else eq.purchase_date
            )
            
            # Check if overdue
            is_overdue = next_due < datetime.now().date() if next_due else False
            
            result.append({
                "id": eq.id,
                "equipment_type": eq.equipment_type,
                "serial_number": eq.serial_number,
                "location": eq.location,
                "maintenance_frequency": eq.maintenance_frequency,
                "last_maintenance": last_maintenance.maintenance_date.isoformat() if last_maintenance else None,
                "next_due_date": next_due.isoformat() if next_due else None,
                "is_overdue": is_overdue,
                "service_provider": eq.service_provider
            })
        
        db.close()
        
        return {"equipment": result, "total": len(result)}
    except Exception as e:
        logger.error(f"Error getting equipment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maintenance")
async def log_maintenance(request: MaintenanceRequest):
    """Log maintenance completion"""
    try:
        logger.info(f"Logging maintenance for equipment {request.equipment_id}")
        
        db = SessionLocal()
        
        # Verify equipment exists
        equipment = db.query(Equipment).filter(Equipment.id == request.equipment_id).first()
        if not equipment:
            db.close()
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        # Calculate next due date
        next_due = maintenance_scheduler.calculate_next_due(
            equipment.maintenance_frequency,
            datetime.fromisoformat(request.maintenance_date).date()
        )
        
        maintenance = MaintenanceRecord(
            equipment_id=request.equipment_id,
            maintenance_date=datetime.fromisoformat(request.maintenance_date).date(),
            technician=request.technician,
            results=request.results,
            next_due_date=next_due
        )
        
        db.add(maintenance)
        db.commit()
        db.close()
        
        return {
            "message": "Maintenance logged successfully",
            "next_due_date": next_due.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(days: int = 30):
    """Get maintenance alerts for upcoming and overdue maintenance"""
    try:
        db = SessionLocal()
        equipment_list = db.query(Equipment).all()
        
        alerts = []
        cutoff_date = datetime.now().date() + timedelta(days=days)
        
        for eq in equipment_list:
            last_maintenance = db.query(MaintenanceRecord).filter(
                MaintenanceRecord.equipment_id == eq.id
            ).order_by(MaintenanceRecord.maintenance_date.desc()).first()
            
            next_due = maintenance_scheduler.calculate_next_due(
                eq.maintenance_frequency,
                last_maintenance.next_due_date if last_maintenance else eq.purchase_date
            )
            
            if next_due and next_due <= cutoff_date:
                days_until = (next_due - datetime.now().date()).days
                alert_level = "Overdue" if days_until < 0 else "High" if days_until <= 7 else "Medium" if days_until <= 14 else "Low"
                
                alerts.append({
                    "equipment_id": eq.id,
                    "equipment_type": eq.equipment_type,
                    "serial_number": eq.serial_number,
                    "location": eq.location,
                    "next_due_date": next_due.isoformat(),
                    "days_until": days_until,
                    "alert_level": alert_level
                })
        
        db.close()
        
        # Sort by urgency
        alerts.sort(key=lambda x: x["days_until"])
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "overdue": len([a for a in alerts if a["days_until"] < 0])
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance-report")
async def get_compliance_report():
    """Generate compliance report"""
    try:
        db = SessionLocal()
        equipment_list = db.query(Equipment).all()
        maintenance_records = db.query(MaintenanceRecord).all()
        db.close()
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_equipment": len(equipment_list),
            "equipment_by_type": {},
            "maintenance_summary": {
                "total_maintenance_records": len(maintenance_records),
                "overdue_count": 0,
                "due_soon_count": 0
            },
            "equipment_details": []
        }
        
        # Group by type
        for eq in equipment_list:
            if eq.equipment_type not in report["equipment_by_type"]:
                report["equipment_by_type"][eq.equipment_type] = 0
            report["equipment_by_type"][eq.equipment_type] += 1
        
        # Get alerts for overdue/due soon
        alerts_response = await get_alerts(days=30)
        report["maintenance_summary"]["overdue_count"] = alerts_response["overdue"]
        report["maintenance_summary"]["due_soon_count"] = len(
            [a for a in alerts_response["alerts"] if a["days_until"] >= 0]
        )
        
        # Equipment details
        for eq in equipment_list:
            last_maintenance = next(
                (m for m in maintenance_records if m.equipment_id == eq.id),
                None
            )
            
            report["equipment_details"].append({
                "equipment_type": eq.equipment_type,
                "serial_number": eq.serial_number,
                "location": eq.location,
                "last_maintenance": last_maintenance.maintenance_date.isoformat() if last_maintenance else "Never",
                "maintenance_frequency": eq.maintenance_frequency
            })
        
        return report
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


