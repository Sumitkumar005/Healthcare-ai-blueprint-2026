"""
Pre-Visit Patient Assessment Automation.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .assessment_engine import AssessmentEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "assessments.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Pre-Visit Assessment", version="1.0.0")
engine_assessment = AssessmentEngine()


class AssessmentResponse(BaseModel):
    patient_id: str
    question_id: int
    answer: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve assessment interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pre-Visit Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; border-radius: 5px; padding: 20px; height: 500px; overflow-y: auto; margin-bottom: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .bot-message { background: #e3f2fd; }
            .user-message { background: #f5f5f5; text-align: right; }
            .urgent { background: #ffebee; border-left: 4px solid #f44336; }
            input { width: 70%; padding: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Pre-Visit Patient Assessment</h1>
        <div class="chat-container" id="chat"></div>
        <div>
            <input type="text" id="userInput" placeholder="Type your answer...">
            <button onclick="sendAnswer()">Send</button>
        </div>
        <script>
            let currentQuestion = 0;
            let responses = {};
            
            async function startAssessment() {
                const response = await fetch('/start', {method: 'POST'});
                const data = await response.json();
                displayQuestion(data.question);
                currentQuestion = data.question_id;
            }
            
            async function sendAnswer() {
                const input = document.getElementById('userInput');
                const answer = input.value;
                if (!answer) return;
                
                addMessage(answer, 'user');
                input.value = '';
                
                const response = await fetch('/answer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question_id: currentQuestion, answer: answer})
                });
                const data = await response.json();
                
                if (data.next_question) {
                    displayQuestion(data.next_question);
                    currentQuestion = data.next_question.id;
                } else if (data.summary) {
                    displaySummary(data.summary);
                }
            }
            
            function displayQuestion(question) {
                addMessage(question.text, 'bot', question.urgent);
            }
            
            function displaySummary(summary) {
                addMessage('Assessment Complete! Summary: ' + summary, 'bot');
            }
            
            function addMessage(text, type, urgent) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = 'message ' + type + '-message' + (urgent ? ' urgent' : '');
                div.textContent = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
            
            window.onload = startAssessment;
            document.getElementById('userInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendAnswer();
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/start")
async def start_assessment():
    """Start new assessment."""
    question = engine_assessment.get_next_question(0, {})
    return {"question_id": 1, "question": question}


@app.post("/answer")
async def submit_answer(response: AssessmentResponse):
    """Process answer and get next question."""
    responses = {response.question_id: response.answer}
    next_question = engine_assessment.get_next_question(response.question_id, responses)
    
    if next_question:
        return {"next_question": next_question}
    else:
        summary = engine_assessment.generate_summary(responses)
        return {"summary": summary}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

