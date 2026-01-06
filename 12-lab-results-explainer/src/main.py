"""
Lab Results Explainer.
"""

import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .lab_parser import LabParser
from .explanation_generator import ExplanationGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI(title="Lab Results Explainer", version="1.0.0")
parser = LabParser()
generator = ExplanationGenerator()


class LabResultsRequest(BaseModel):
    lab_results_text: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve main interface."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lab Results Explainer</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
            textarea { width: 100%; height: 200px; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .normal { color: #28a745; }
            .abnormal { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Lab Results Explainer</h1>
        <form id="labForm">
            <textarea id="labResults" placeholder="Paste lab results here or upload PDF/image..."></textarea>
            <button type="submit">Explain Results</button>
        </form>
        <div id="result"></div>
        <script>
            document.getElementById('labForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const text = document.getElementById('labResults').value;
                const response = await fetch('/explain', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({lab_results_text: text})
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<div class="result"><pre>' + result.explanation + '</pre></div>';
            });
        </script>
    </body>
    </html>
    """
    return html


@app.post("/explain")
async def explain_results(request: LabResultsRequest):
    """Explain lab results."""
    try:
        # Parse lab results
        parsed = parser.parse(request.lab_results_text)
        
        # Generate explanation
        explanation = generator.generate(parsed)
        
        return {"status": "success", "explanation": explanation}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

