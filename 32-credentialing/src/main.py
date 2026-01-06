"""
FastAPI application for Credentialing Automation
"""
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from credential_manager import CredentialManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./credentialing.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProviderCredential(Base):
    """Database model for provider credentials"""
    __tablename__ = "provider_credentials"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(String)
    credential_type = Column(String)  # License, DEA, Certification, etc.
    credential_number = Column(String)
    issue_date = Column(Date)
    expiration_date = Column(Date)
    status = Column(String)  # Active, Expired, Pending
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credentialing Automation", version="1.0.0")
manager = CredentialManager()


class CredentialRequest(BaseModel):
    """Request to add credential"""
    provider_id: str
    credential_type: str
    credential_number: str
    expiration_date: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content="<h1>Credentialing Automation</h1><p>Use API endpoints</p>")


@app.post("/api/credential")
async def add_credential(request: CredentialRequest):
    """Add provider credential"""
    try:
        db = SessionLocal()
        credential = ProviderCredential(
            provider_id=request.provider_id,
            credential_type=request.credential_type,
            credential_number=request.credential_number,
            expiration_date=datetime.fromisoformat(request.expiration_date).date(),
            status="Active"
        )
        db.add(credential)
        db.commit()
        db.close()
        return {"message": "Credential added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/credentials/{provider_id}")
async def get_credentials(provider_id: str):
    """Get all credentials for a provider"""
    try:
        db = SessionLocal()
        credentials = db.query(ProviderCredential).filter(
            ProviderCredential.provider_id == provider_id
        ).all()
        db.close()
        
        return {"credentials": [
            {
                "type": c.credential_type,
                "number": c.credential_number,
                "expiration": c.expiration_date.isoformat() if c.expiration_date else None,
                "status": c.status
            }
            for c in credentials
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

