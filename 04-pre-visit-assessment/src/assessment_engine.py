"""
Pre-visit assessment engine.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class AssessmentEngine:
    """Manages pre-visit assessment flow."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
        
        self.questions = [
            {"id": 1, "text": "Do you have any new symptoms or concerns since your last visit?", "urgent": False},
            {"id": 2, "text": "Are you taking all your medications as prescribed?", "urgent": False},
            {"id": 3, "text": "Do you have any allergies or adverse reactions to report?", "urgent": False},
            {"id": 4, "text": "Are you experiencing any chest pain, shortness of breath, or severe symptoms?", "urgent": True},
            {"id": 5, "text": "Have you had any recent hospitalizations or emergency visits?", "urgent": False},
        ]
    
    def get_next_question(self, current_id: int, responses: Dict) -> Optional[Dict]:
        """
        Get next question based on current progress.
        
        Args:
            current_id: Current question ID
            responses: Dictionary of responses so far
            
        Returns:
            Next question or None if complete
        """
        # Check for urgent responses
        if current_id == 4 and responses.get(4, "").lower() in ["yes", "y"]:
            return {
                "id": 99,
                "text": "URGENT: Please call 911 or go to emergency room immediately if symptoms are severe!",
                "urgent": True
            }
        
        # Get next question
        next_id = current_id + 1
        if next_id <= len(self.questions):
            return self.questions[next_id - 1]
        
        return None
    
    def generate_summary(self, responses: Dict) -> str:
        """
        Generate pre-visit summary from responses.
        
        Args:
            responses: Dictionary of question_id -> answer
            
        Returns:
            Summary string
        """
        if self.llm_client:
            prompt = f"""Generate a pre-visit assessment summary from these patient responses:

{self._format_responses(responses)}

Create a concise summary highlighting:
1. New symptoms or concerns
2. Medication adherence
3. Urgent flags
4. Recommendations for provider"""
            
            try:
                return self.llm_client.generate(prompt, max_tokens=500)
            except:
                pass
        
        # Fallback summary
        summary = "PRE-VISIT ASSESSMENT SUMMARY\n\n"
        for q_id, answer in responses.items():
            if q_id < len(self.questions):
                summary += f"Q: {self.questions[q_id-1]['text']}\nA: {answer}\n\n"
        return summary
    
    def _format_responses(self, responses: Dict) -> str:
        """Format responses for display."""
        formatted = []
        for q_id, answer in responses.items():
            if q_id < len(self.questions):
                formatted.append(f"Q: {self.questions[q_id-1]['text']}\nA: {answer}")
        return "\n\n".join(formatted)
