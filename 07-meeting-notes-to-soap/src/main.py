"""
Main FastAPI application for Meeting Notes to SOAP Converter.
"""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .soap_generator import SOAPGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Meeting Notes to SOAP Converter", version="1.0.0")
generator = SOAPGenerator()


class MeetingNotesRequest(BaseModel):
    """Request model for SOAP note generation."""
    meeting_notes: str = Field(..., description="Meeting notes or transcript")
    disciplines: List[str] = Field(default=["nursing", "pt", "ot", "social_work"], description="Disciplines to generate SOAP notes for")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meeting Notes to SOAP Converter</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            textarea { width: 100%; height: 300px; padding: 10px; border: 1px solid #ddd; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-top: 10px; }
            .soap-note { margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }
            h3 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Meeting Notes to SOAP Note Converter</h1>
        <form id="notesForm">
            <textarea id="meetingNotes" placeholder="Paste meeting notes or transcript here..."></textarea>
            <button type="submit">Generate SOAP Notes</button>
        </form>
        <div id="results"></div>
        <script>
            document.getElementById('notesForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const notes = document.getElementById('meetingNotes').value;
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({meeting_notes: notes, disciplines: ['nursing', 'pt', 'ot', 'social_work']})
                });
                const result = await response.json();
                let html = '';
                for (const [discipline, soap] of Object.entries(result.soap_notes)) {
                    html += `<div class="soap-note"><h3>${discipline.toUpperCase()} SOAP Note</h3><pre>${soap}</pre></div>`;
                }
                document.getElementById('results').innerHTML = html;
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/generate")
async def generate_soap_notes(request: MeetingNotesRequest):
    """Generate SOAP notes from meeting notes."""
    try:
        logger.info("Generating SOAP notes from meeting notes")
        soap_notes = generator.generate_soap_notes(request.meeting_notes, request.disciplines)
        return {"status": "success", "soap_notes": soap_notes}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


