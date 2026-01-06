"""
FastAPI application for Healthcare Employee Onboarding Automation
"""
import logging
from typing import List, Optional
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from onboarding_manager import OnboardingManager
from checklist_manager import ChecklistManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./employee_onboarding.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    """Database model for employees"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    role = Column(String)  # clinical, non_clinical
    start_date = Column(Date)
    onboarding_status = Column(String)  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentRequirement(Base):
    """Database model for document requirements"""
    __tablename__ = "document_requirements"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String)
    document_type = Column(String)  # license, dea, titer, tb_test, background_check, hipaa_training
    required = Column(Boolean, default=True)
    uploaded = Column(Boolean, default=False)
    upload_date = Column(DateTime, nullable=True)
    expiration_date = Column(Date, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Employee Onboarding Automation",
    description="Automate healthcare employee onboarding with compliance tracking",
    version="1.0.0"
)

onboarding_manager = OnboardingManager()
checklist_manager = ChecklistManager()


class EmployeeRequest(BaseModel):
    """Request to add employee"""
    employee_id: str
    first_name: str
    last_name: str
    email: str
    role: str
    start_date: str


class DocumentRequest(BaseModel):
    """Request to upload document"""
    employee_id: str
    document_type: str
    expiration_date: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Employee Onboarding Automation</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .section { margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>👥 Healthcare Employee Onboarding Automation</h1>
            <div class="section">
                <h2>API Endpoints</h2>
                <ul>
                    <li>POST /api/employee - Add new employee</li>
                    <li>GET /api/employee/{id}/checklist - Get onboarding checklist</li>
                    <li>POST /api/document - Upload document</li>
                    <li>GET /api/onboarding/status - Get onboarding status</li>
                    <li>GET /api/compliance-report - Generate compliance report</li>
                </ul>
            </div>
        </body>
    </html>
    """)


@app.post("/api/employee")
async def add_employee(request: EmployeeRequest):
    """Add new employee for onboarding"""
    try:
        logger.info(f"Adding employee: {request.employee_id}")
        
        db = SessionLocal()
        
        # Check if employee exists
        existing = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Employee already exists")
        
        employee = Employee(
            employee_id=request.employee_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            role=request.role,
            start_date=datetime.fromisoformat(request.start_date).date(),
            onboarding_status="pending"
        )
        
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        # Create document requirements based on role
        requirements = checklist_manager.get_requirements_for_role(request.role)
        for req_type in requirements:
            doc_req = DocumentRequirement(
                employee_id=request.employee_id,
                document_type=req_type,
                required=True
            )
            db.add(doc_req)
        
        db.commit()
        db.close()
        
        return {
            "message": "Employee added successfully",
            "employee_id": request.employee_id,
            "requirements": requirements
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding employee: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/employee/{employee_id}/checklist")
async def get_checklist(employee_id: str):
    """Get onboarding checklist for employee"""
    try:
        db = SessionLocal()
        
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            db.close()
            raise HTTPException(status_code=404, detail="Employee not found")
        
        requirements = db.query(DocumentRequirement).filter(
            DocumentRequirement.employee_id == employee_id
        ).all()
        
        db.close()
        
        checklist = []
        for req in requirements:
            checklist.append({
                "document_type": req.document_type,
                "required": req.required,
                "uploaded": req.uploaded,
                "upload_date": req.upload_date.isoformat() if req.upload_date else None,
                "expiration_date": req.expiration_date.isoformat() if req.expiration_date else None,
                "verified": req.verified
            })
        
        # Calculate progress
        total = len(checklist)
        completed = sum(1 for item in checklist if item["uploaded"] and item["verified"])
        progress = (completed / total * 100) if total > 0 else 0
        
        return {
            "employee_id": employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "role": employee.role,
            "onboarding_status": employee.onboarding_status,
            "progress": round(progress, 2),
            "checklist": checklist
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting checklist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document")
async def upload_document(
    employee_id: str,
    document_type: str,
    file: UploadFile = File(...),
    expiration_date: Optional[str] = None
):
    """Upload and verify document"""
    try:
        logger.info(f"Uploading document {document_type} for employee {employee_id}")
        
        db = SessionLocal()
        
        # Verify employee exists
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            db.close()
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Find requirement
        requirement = db.query(DocumentRequirement).filter(
            DocumentRequirement.employee_id == employee_id,
            DocumentRequirement.document_type == document_type
        ).first()
        
        if not requirement:
            db.close()
            raise HTTPException(status_code=404, detail="Document requirement not found")
        
        # Update requirement
        requirement.uploaded = True
        requirement.upload_date = datetime.utcnow()
        requirement.verified = True  # Auto-verify for MVP
        
        if expiration_date:
            requirement.expiration_date = datetime.fromisoformat(expiration_date).date()
        
        # Update onboarding status
        all_requirements = db.query(DocumentRequirement).filter(
            DocumentRequirement.employee_id == employee_id
        ).all()
        
        all_complete = all(r.uploaded and r.verified for r in all_requirements)
        if all_complete:
            employee.onboarding_status = "completed"
        else:
            employee.onboarding_status = "in_progress"
        
        db.commit()
        db.close()
        
        # In production, save file to storage
        # For MVP, we just track the upload
        
        return {
            "message": "Document uploaded successfully",
            "document_type": document_type,
            "verified": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/onboarding/status")
async def get_onboarding_status():
    """Get onboarding status for all employees"""
    try:
        db = SessionLocal()
        employees = db.query(Employee).all()
        requirements = db.query(DocumentRequirement).all()
        db.close()
        
        status_list = []
        for employee in employees:
            emp_requirements = [r for r in requirements if r.employee_id == employee.employee_id]
            total = len(emp_requirements)
            completed = sum(1 for r in emp_requirements if r.uploaded and r.verified)
            progress = (completed / total * 100) if total > 0 else 0
            
            status_list.append({
                "employee_id": employee.employee_id,
                "name": f"{employee.first_name} {employee.last_name}",
                "role": employee.role,
                "start_date": employee.start_date.isoformat(),
                "status": employee.onboarding_status,
                "progress": round(progress, 2),
                "completed_documents": completed,
                "total_documents": total
            })
        
        return {
            "total_employees": len(status_list),
            "pending": len([s for s in status_list if s["status"] == "pending"]),
            "in_progress": len([s for s in status_list if s["status"] == "in_progress"]),
            "completed": len([s for s in status_list if s["status"] == "completed"]),
            "employees": status_list
        }
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance-report")
async def get_compliance_report():
    """Generate compliance report"""
    try:
        db = SessionLocal()
        employees = db.query(Employee).all()
        requirements = db.query(DocumentRequirement).all()
        db.close()
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_employees": len(employees),
            "compliance_summary": {
                "fully_compliant": 0,
                "missing_documents": 0,
                "expired_documents": 0
            },
            "employees_with_issues": []
        }
        
        for employee in employees:
            emp_requirements = [r for r in requirements if r.employee_id == employee.employee_id]
            missing = [r for r in emp_requirements if not r.uploaded]
            expired = [
                r for r in emp_requirements
                if r.expiration_date and r.expiration_date < date.today()
            ]
            
            if missing or expired:
                report["compliance_summary"]["missing_documents"] += len(missing)
                report["compliance_summary"]["expired_documents"] += len(expired)
                
                report["employees_with_issues"].append({
                    "employee_id": employee.employee_id,
                    "name": f"{employee.first_name} {employee.last_name}",
                    "missing_documents": [r.document_type for r in missing],
                    "expired_documents": [r.document_type for r in expired]
                })
            else:
                report["compliance_summary"]["fully_compliant"] += 1
        
        return report
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


