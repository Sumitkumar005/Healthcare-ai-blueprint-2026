"""
Main FastAPI application for Insurance Prior Authorization Auto-Generator.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .generator import PriorAuthGenerator
from .pdf_generator import generate_pdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Prior Authorization Generator",
    description="AI-powered prior authorization request generator",
    version="1.0.0",
)

# Initialize generator
generator = PriorAuthGenerator()


class PriorAuthRequest(BaseModel):
    """Request model for prior authorization generation."""
    
    patient_name: str = Field(..., description="Patient full name")
    patient_dob: str = Field(..., description="Patient date of birth (YYYY-MM-DD)")
    patient_id: Optional[str] = Field(None, description="Patient ID/MRN")
    diagnosis_code: str = Field(..., description="Primary diagnosis ICD-10 code")
    diagnosis_description: str = Field(..., description="Diagnosis description")
    treatment_code: str = Field(..., description="CPT code for requested treatment")
    treatment_description: str = Field(..., description="Treatment description")
    clinical_notes: str = Field(..., description="Clinical rationale and notes")
    provider_name: Optional[str] = Field(None, description="Provider name")
    provider_npi: Optional[str] = Field(None, description="Provider NPI")
    insurance_name: Optional[str] = Field(None, description="Insurance company name")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML interface."""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    
    # Fallback HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prior Authorization Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            textarea { height: 100px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Prior Authorization Generator</h1>
        <form id="authForm">
            <div class="form-group">
                <label>Patient Name:</label>
                <input type="text" name="patient_name" required>
            </div>
            <div class="form-group">
                <label>Date of Birth (YYYY-MM-DD):</label>
                <input type="text" name="patient_dob" required>
            </div>
            <div class="form-group">
                <label>Diagnosis Code (ICD-10):</label>
                <input type="text" name="diagnosis_code" required>
            </div>
            <div class="form-group">
                <label>Diagnosis Description:</label>
                <input type="text" name="diagnosis_description" required>
            </div>
            <div class="form-group">
                <label>Treatment Code (CPT):</label>
                <input type="text" name="treatment_code" required>
            </div>
            <div class="form-group">
                <label>Treatment Description:</label>
                <input type="text" name="treatment_description" required>
            </div>
            <div class="form-group">
                <label>Clinical Notes/Rationale:</label>
                <textarea name="clinical_notes" required></textarea>
            </div>
            <button type="submit">Generate Prior Authorization</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('authForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            });
        </script>
    </body>
    </html>
    """


@app.post("/generate")
async def generate_prior_auth(request: PriorAuthRequest):
    """
    Generate prior authorization request.
    
    Args:
        request: Prior authorization request data
        
    Returns:
        Generated prior auth document
    """
    try:
        logger.info(f"Generating prior auth for patient: {request.patient_name}")
        
        # Generate prior auth content
        prior_auth_content = generator.generate(request.dict())
        
        # Generate PDF
        pdf_path = generate_pdf(prior_auth_content, request.patient_name)
        
        return {
            "status": "success",
            "message": "Prior authorization generated successfully",
            "content": prior_auth_content,
            "pdf_path": str(pdf_path),
        }
        
    except Exception as e:
        logger.error(f"Error generating prior auth: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating prior auth: {str(e)}")


@app.get("/download/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF."""
    pdf_path = Path(__file__).parent.parent / "output" / filename
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="PDF not found")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


