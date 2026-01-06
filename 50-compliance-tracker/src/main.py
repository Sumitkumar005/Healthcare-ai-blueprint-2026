"""
FastAPI application for Healthcare Regulatory Compliance Update Tracker
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from compliance_monitor import ComplianceMonitor
from action_generator import ActionGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./compliance_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PracticeProfile(Base):
    """Database model for practice profile"""
    __tablename__ = "practice_profiles"
    
    id = Column(Integer, primary_key=True)
    practice_id = Column(String, unique=True)
    practice_type = Column(String)  # primary_care, specialty, hospital, etc.
    state = Column(String)
    services_offered = Column(Text)  # JSON string
    practice_size = Column(String)  # small, medium, large
    created_at = Column(DateTime, default=datetime.utcnow)


class RegulatoryUpdate(Base):
    """Database model for regulatory updates"""
    __tablename__ = "regulatory_updates"
    
    id = Column(Integer, primary_key=True)
    update_id = Column(String, unique=True)
    source = Column(String)  # CMS, CDC, OSHA, state_health, etc.
    title = Column(String)
    summary = Column(Text)
    full_text = Column(Text)
    relevance_score = Column(Integer)  # 0-100
    urgency = Column(String)  # high, medium, low
    impact = Column(String)  # high, medium, low
    published_date = Column(DateTime)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActionItem(Base):
    """Database model for action items"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True)
    update_id = Column(String)
    practice_id = Column(String)
    action_description = Column(Text)
    responsible_party = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceChecklist(Base):
    """Database model for compliance checklist"""
    __tablename__ = "compliance_checklist"
    
    id = Column(Integer, primary_key=True)
    practice_id = Column(String)
    update_id = Column(String)
    checklist_item = Column(String)
    completed = Column(Boolean, default=False)
    completed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Regulatory Compliance Update Tracker",
    description="Track and manage regulatory compliance updates",
    version="1.0.0"
)

compliance_monitor = ComplianceMonitor()
action_generator = ActionGenerator()


class PracticeProfileRequest(BaseModel):
    """Request to add practice profile"""
    practice_id: str
    practice_type: str
    state: str
    services_offered: List[str]
    practice_size: str


class RegulatoryUpdateRequest(BaseModel):
    """Request to add regulatory update"""
    update_id: str
    source: str
    title: str
    summary: str
    full_text: str
    published_date: str
    deadline: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Regulatory Compliance Tracker</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .section { margin: 30px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>📋 Healthcare Regulatory Compliance Update Tracker</h1>
            <div class="section">
                <h2>API Endpoints</h2>
                <ul>
                    <li>POST /api/practice - Add practice profile</li>
                    <li>POST /api/update - Add regulatory update</li>
                    <li>GET /api/updates/{practice_id} - Get relevant updates</li>
                    <li>GET /api/action-items/{practice_id} - Get action items</li>
                    <li>GET /api/compliance-status/{practice_id} - Get compliance status</li>
                </ul>
            </div>
        </body>
    </html>
    """)


@app.post("/api/practice")
async def add_practice(request: PracticeProfileRequest):
    """Add practice profile"""
    try:
        logger.info(f"Adding practice profile: {request.practice_id}")
        
        import json
        db = SessionLocal()
        
        # Check if practice exists
        existing = db.query(PracticeProfile).filter(
            PracticeProfile.practice_id == request.practice_id
        ).first()
        
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Practice already exists")
        
        practice = PracticeProfile(
            practice_id=request.practice_id,
            practice_type=request.practice_type,
            state=request.state,
            services_offered=json.dumps(request.services_offered),
            practice_size=request.practice_size
        )
        
        db.add(practice)
        db.commit()
        db.close()
        
        return {"message": "Practice profile added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding practice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update")
async def add_regulatory_update(request: RegulatoryUpdateRequest):
    """Add regulatory update"""
    try:
        logger.info(f"Adding regulatory update: {request.update_id}")
        
        db = SessionLocal()
        
        # Check if update exists
        existing = db.query(RegulatoryUpdate).filter(
            RegulatoryUpdate.update_id == request.update_id
        ).first()
        
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="Update already exists")
        
        # Determine urgency and impact (simplified)
        urgency = compliance_monitor.determine_urgency(request.full_text)
        impact = compliance_monitor.determine_impact(request.full_text)
        
        update = RegulatoryUpdate(
            update_id=request.update_id,
            source=request.source,
            title=request.title,
            summary=request.summary,
            full_text=request.full_text,
            published_date=datetime.fromisoformat(request.published_date),
            deadline=datetime.fromisoformat(request.deadline).date() if request.deadline else None,
            urgency=urgency,
            impact=impact,
            relevance_score=0  # Will be calculated when matched to practices
        )
        
        db.add(update)
        db.commit()
        db.close()
        
        return {
            "message": "Regulatory update added successfully",
            "urgency": urgency,
            "impact": impact
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/updates/{practice_id}")
async def get_relevant_updates(practice_id: str):
    """Get relevant updates for practice"""
    try:
        import json
        db = SessionLocal()
        
        practice = db.query(PracticeProfile).filter(
            PracticeProfile.practice_id == practice_id
        ).first()
        
        if not practice:
            db.close()
            raise HTTPException(status_code=404, detail="Practice not found")
        
        updates = db.query(RegulatoryUpdate).all()
        
        # Filter and score updates for relevance
        relevant_updates = []
        for update in updates:
            relevance_score = compliance_monitor.calculate_relevance(
                practice_data={
                    "practice_type": practice.practice_type,
                    "state": practice.state,
                    "services_offered": json.loads(practice.services_offered),
                    "practice_size": practice.practice_size
                },
                update_data={
                    "source": update.source,
                    "title": update.title,
                    "full_text": update.full_text
                }
            )
            
            if relevance_score > 30:  # Threshold for relevance
                update.relevance_score = relevance_score
                db.commit()
                
                relevant_updates.append({
                    "update_id": update.update_id,
                    "source": update.source,
                    "title": update.title,
                    "summary": update.summary,
                    "relevance_score": relevance_score,
                    "urgency": update.urgency,
                    "impact": update.impact,
                    "published_date": update.published_date.isoformat(),
                    "deadline": update.deadline.isoformat() if update.deadline else None
                })
        
        db.close()
        
        # Sort by relevance and urgency
        relevant_updates.sort(
            key=lambda x: (
                x["urgency"] == "high",
                x["relevance_score"]
            ),
            reverse=True
        )
        
        return {
            "practice_id": practice_id,
            "total_updates": len(relevant_updates),
            "updates": relevant_updates
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/action-items/{practice_id}")
async def get_action_items(practice_id: str):
    """Get action items for practice"""
    try:
        db = SessionLocal()
        
        action_items = db.query(ActionItem).filter(
            ActionItem.practice_id == practice_id
        ).order_by(ActionItem.due_date).all()
        
        db.close()
        
        return {
            "practice_id": practice_id,
            "total_items": len(action_items),
            "pending": len([a for a in action_items if a.status == "pending"]),
            "in_progress": len([a for a in action_items if a.status == "in_progress"]),
            "completed": len([a for a in action_items if a.status == "completed"]),
            "action_items": [
                {
                    "id": a.id,
                    "update_id": a.update_id,
                    "action_description": a.action_description,
                    "responsible_party": a.responsible_party,
                    "due_date": a.due_date.isoformat() if a.due_date else None,
                    "status": a.status
                }
                for a in action_items
            ]
        }
    except Exception as e:
        logger.error(f"Error getting action items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/action-items/generate/{practice_id}/{update_id}")
async def generate_action_items(practice_id: str, update_id: str):
    """Generate action items for an update"""
    try:
        db = SessionLocal()
        
        practice = db.query(PracticeProfile).filter(
            PracticeProfile.practice_id == practice_id
        ).first()
        
        update = db.query(RegulatoryUpdate).filter(
            RegulatoryUpdate.update_id == update_id
        ).first()
        
        if not practice or not update:
            db.close()
            raise HTTPException(status_code=404, detail="Practice or update not found")
        
        # Generate action items
        action_items = action_generator.generate_action_items(
            update_title=update.title,
            update_summary=update.summary,
            update_full_text=update.full_text,
            deadline=update.deadline
        )
        
        # Save action items
        created_items = []
        for item in action_items:
            action_item = ActionItem(
                update_id=update_id,
                practice_id=practice_id,
                action_description=item["description"],
                responsible_party=item.get("responsible_party"),
                due_date=item.get("due_date"),
                status="pending"
            )
            db.add(action_item)
            created_items.append({
                "description": item["description"],
                "responsible_party": item.get("responsible_party"),
                "due_date": item.get("due_date").isoformat() if item.get("due_date") else None
            })
        
        db.commit()
        db.close()
        
        return {
            "message": "Action items generated successfully",
            "update_id": update_id,
            "action_items": created_items
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating action items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance-status/{practice_id}")
async def get_compliance_status(practice_id: str):
    """Get compliance status for practice"""
    try:
        db = SessionLocal()
        
        action_items = db.query(ActionItem).filter(
            ActionItem.practice_id == practice_id
        ).all()
        
        checklist_items = db.query(ComplianceChecklist).filter(
            ComplianceChecklist.practice_id == practice_id
        ).all()
        
        db.close()
        
        total_actions = len(action_items)
        completed_actions = len([a for a in action_items if a.status == "completed"])
        pending_actions = len([a for a in action_items if a.status == "pending"])
        
        total_checklist = len(checklist_items)
        completed_checklist = len([c for c in checklist_items if c.completed])
        
        compliance_rate = (
            (completed_actions + completed_checklist) / (total_actions + total_checklist) * 100
            if (total_actions + total_checklist) > 0 else 100
        )
        
        # Get high-priority pending items
        high_priority_pending = [
            {
                "action_description": a.action_description,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "responsible_party": a.responsible_party
            }
            for a in action_items
            if a.status == "pending" and a.due_date and a.due_date < datetime.now().date()
        ]
        
        return {
            "practice_id": practice_id,
            "compliance_rate": round(compliance_rate, 2),
            "action_items": {
                "total": total_actions,
                "completed": completed_actions,
                "pending": pending_actions
            },
            "checklist": {
                "total": total_checklist,
                "completed": completed_checklist
            },
            "high_priority_pending": high_priority_pending,
            "status": "compliant" if compliance_rate >= 90 else "at_risk" if compliance_rate >= 70 else "non_compliant"
        }
    except Exception as e:
        logger.error(f"Error getting compliance status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

