"""
FastAPI application for Healthcare Staff Time-Study Automation
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

from time_tracker import TimeTracker
from workflow_analyzer import WorkflowAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./time_study.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TaskLog(Base):
    """Database model for task logs"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(String)
    role = Column(String)  # nursing, physician, etc.
    task_category = Column(String)  # patient_care, documentation, medication, etc.
    task_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Staff Time-Study Automation", version="1.0.0")
time_tracker = TimeTracker()
workflow_analyzer = WorkflowAnalyzer()


class TaskStartRequest(BaseModel):
    """Request to start task"""
    staff_id: str
    role: str
    task_category: str
    task_name: str


class TaskEndRequest(BaseModel):
    """Request to end task"""
    task_log_id: int
    notes: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Healthcare Staff Time-Study Automation</h1><p>Use API endpoints</p>")


@app.post("/api/task/start")
async def start_task(request: TaskStartRequest):
    """Start task tracking"""
    try:
        db = SessionLocal()
        task_log = TaskLog(
            staff_id=request.staff_id,
            role=request.role,
            task_category=request.task_category,
            task_name=request.task_name,
            start_time=datetime.utcnow()
        )
        db.add(task_log)
        db.commit()
        db.refresh(task_log)
        db.close()
        
        return {
            "message": "Task started",
            "task_log_id": task_log.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task/end")
async def end_task(request: TaskEndRequest):
    """End task tracking"""
    try:
        db = SessionLocal()
        task_log = db.query(TaskLog).filter(TaskLog.id == request.task_log_id).first()
        if not task_log:
            db.close()
            raise HTTPException(status_code=404, detail="Task log not found")
        
        task_log.end_time = datetime.utcnow()
        if task_log.start_time:
            duration = (task_log.end_time - task_log.start_time).total_seconds() / 60
            task_log.duration_minutes = duration
        
        if request.notes:
            task_log.notes = request.notes
        
        db.commit()
        db.close()
        
        return {
            "message": "Task ended",
            "duration_minutes": round(task_log.duration_minutes, 2) if task_log.duration_minutes else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """Get workflow analytics"""
    try:
        db = SessionLocal()
        task_logs = db.query(TaskLog).filter(TaskLog.duration_minutes.isnot(None)).all()
        db.close()
        
        return workflow_analyzer.analyze_workflow(task_logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


