"""
FastAPI application for Healthcare Social Media Content Generator
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from content_generator import SocialMediaContentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./social_media_content.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Content(Base):
    """Database model for generated content"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True)
    content_id = Column(String, unique=True)
    topic = Column(String)
    platform = Column(String)  # facebook, instagram, linkedin, twitter
    content_text = Column(Text)
    hashtags = Column(String, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Social Media Content Generator", version="1.0.0")
generator = SocialMediaContentGenerator()


class ContentRequest(BaseModel):
    """Request to generate content"""
    topic: str
    platform: str
    scheduled_date: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Healthcare Social Media Content Generator</h1><p>Use API endpoints</p>")


@app.post("/api/content/generate")
async def generate_content(request: ContentRequest):
    """Generate social media content"""
    try:
        content_data = generator.generate_content(
            topic=request.topic,
            platform=request.platform
        )
        
        import json
        db = SessionLocal()
        content = Content(
            content_id=f"content_{datetime.now().timestamp()}",
            topic=request.topic,
            platform=request.platform,
            content_text=content_data["content"],
            hashtags=", ".join(content_data.get("hashtags", [])),
            scheduled_date=datetime.fromisoformat(request.scheduled_date) if request.scheduled_date else None
        )
        db.add(content)
        db.commit()
        db.close()
        
        return {
            "content_id": content.content_id,
            "content": content_data["content"],
            "hashtags": content_data.get("hashtags", []),
            "platform": request.platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/content/calendar")
async def get_content_calendar():
    """Get content calendar"""
    try:
        db = SessionLocal()
        contents = db.query(Content).filter(
            Content.scheduled_date.isnot(None)
        ).order_by(Content.scheduled_date).all()
        db.close()
        
        return {
            "calendar": [
                {
                    "content_id": c.content_id,
                    "topic": c.topic,
                    "platform": c.platform,
                    "scheduled_date": c.scheduled_date.isoformat() if c.scheduled_date else None
                }
                for c in contents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


