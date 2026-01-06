"""
Voice-to-Clinical-Note Converter - Main FastAPI application.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .transcriber import AudioTranscriber
from .note_generator import ClinicalNoteGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(
    title="Voice-to-Clinical-Note Converter",
    description="Convert voice memos to structured clinical notes",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcriber = AudioTranscriber()
note_generator = ClinicalNoteGenerator()


class TranscriptionRequest(BaseModel):
    """Request model for transcription."""
    note_type: str = "visit_note"  # visit_note, wound_care, medication


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main interface."""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    
    # Fallback HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voice-to-Clinical-Note Converter</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }
            button:disabled { opacity: 0.6; cursor: not-allowed; }
            #recordingStatus { margin: 20px 0; font-weight: bold; }
            #transcriptionResult { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            textarea { width: 100%; height: 300px; padding: 10px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Voice-to-Clinical-Note Converter</h1>
        <div>
            <button id="recordBtn" onclick="startRecording()">Start Recording</button>
            <button id="stopBtn" onclick="stopRecording()" disabled>Stop Recording</button>
        </div>
        <div id="recordingStatus"></div>
        <div id="transcriptionResult"></div>
        <script>
            let mediaRecorder;
            let audioChunks = [];
            
            async function startRecording() {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    await uploadAudio(audioBlob);
                };
                
                mediaRecorder.start();
                document.getElementById('recordBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('recordingStatus').textContent = 'Recording...';
            }
            
            function stopRecording() {
                mediaRecorder.stop();
                document.getElementById('recordBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                document.getElementById('recordingStatus').textContent = 'Processing...';
            }
            
            async function uploadAudio(audioBlob) {
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');
                
                const response = await fetch('/transcribe', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                document.getElementById('transcriptionResult').innerHTML = 
                    '<h3>Structured Clinical Note:</h3><textarea readonly>' + result.structured_note + '</textarea>';
                document.getElementById('recordingStatus').textContent = 'Complete!';
            }
        </script>
    </body>
    </html>
    """


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), note_type: str = "visit_note"):
    """
    Transcribe audio and generate structured clinical note.
    
    Args:
        audio: Audio file (webm, wav, mp3)
        note_type: Type of note (visit_note, wound_care, medication)
        
    Returns:
        Structured clinical note
    """
    try:
        logger.info(f"Transcribing audio for note type: {note_type}")
        
        # Read audio file
        audio_data = await audio.read()
        
        # Transcribe audio
        transcription = await transcriber.transcribe(audio_data, audio.filename)
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        # Generate structured note
        structured_note = note_generator.generate(transcription, note_type)
        
        return {
            "status": "success",
            "transcription": transcription,
            "structured_note": structured_note,
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

