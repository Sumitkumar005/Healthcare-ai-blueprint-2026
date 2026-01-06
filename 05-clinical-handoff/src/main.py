"""
Clinical Handoff Summarizer.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .transcriber import HandoffTranscriber
from .handoff_generator import HandoffGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "handoffs.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Clinical Handoff Summarizer", version="1.0.0")
transcriber = HandoffTranscriber()
generator = HandoffGenerator()


class HandoffRequest(BaseModel):
    voice_notes: str  # Transcribed text or voice file path


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clinical Handoff Summarizer</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            textarea { width: 100%; height: 200px; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-top: 10px; }
            .handoff-report { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .critical { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Clinical Handoff Summarizer</h1>
        <form id="handoffForm">
            <textarea id="voiceNotes" placeholder="Paste transcribed voice notes or type handoff information here..."></textarea>
            <button type="submit">Generate Handoff Report</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('handoffForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const notes = document.getElementById('voiceNotes').value;
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({voice_notes: notes})
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<div class="handoff-report"><pre>' + result.handoff_report + '</pre></div>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/generate")
async def generate_handoff(request: HandoffRequest):
    """Generate handoff report."""
    try:
        handoff_report = generator.generate(request.voice_notes)
        return {"status": "success", "handoff_report": handoff_report}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
