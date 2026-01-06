"""
FastAPI application for Patient Education Material Customizer
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

from material_generator import EducationMaterialGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./education_materials.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Material(Base):
    """Database model for education materials"""
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True)
    material_id = Column(String, unique=True)
    patient_id = Column(String)
    topic = Column(String)
    reading_level = Column(String)  # 5th_grade, 8th_grade, high_school, college
    language = Column(String, default="en")
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Education Material Customizer", version="1.0.0")
generator = EducationMaterialGenerator()


class MaterialRequest(BaseModel):
    """Request to generate material"""
    patient_id: str
    topic: str
    reading_level: str = "8th_grade"
    language: str = "en"
    specific_concerns: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Patient Education Material Customizer</h1><p>Use API endpoints</p>")


@app.post("/api/material/generate")
async def generate_material(request: MaterialRequest):
    """Generate customized education material"""
    try:
        content = generator.generate_material(
            topic=request.topic,
            reading_level=request.reading_level,
            language=request.language,
            specific_concerns=request.specific_concerns
        )
        
        db = SessionLocal()
        material = Material(
            material_id=f"material_{datetime.now().timestamp()}",
            patient_id=request.patient_id,
            topic=request.topic,
            reading_level=request.reading_level,
            language=request.language,
            content=content
        )
        db.add(material)
        db.commit()
        db.close()
        
        return {
            "material_id": material.material_id,
            "content": content,
            "topic": request.topic,
            "reading_level": request.reading_level,
            "language": request.language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/material/{material_id}")
async def get_material(material_id: str):
    """Get generated material"""
    try:
        db = SessionLocal()
        material = db.query(Material).filter(Material.material_id == material_id).first()
        db.close()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        return {
            "material_id": material.material_id,
            "topic": material.topic,
            "content": material.content,
            "reading_level": material.reading_level,
            "language": material.language
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


