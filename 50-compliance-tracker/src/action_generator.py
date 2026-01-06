"""
Action item generation from regulatory updates
"""
import logging
import os
from typing import List, Dict
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class ActionGenerator:
    """Generates action items from regulatory updates"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
    
    def generate_action_items(
        self,
        update_title: str,
        update_summary: str,
        update_full_text: str,
        deadline: date = None
    ) -> List[Dict]:
        """
        Generate action items from regulatory update
        
        Args:
            update_title: Title of the update
            update_summary: Summary of the update
            update_full_text: Full text of the update
            deadline: Deadline date if available
            
        Returns:
            List of action item dictionaries
        """
        action_items = []
        
        # Use AI if available
        if self.client:
            try:
                prompt = f"""Based on this regulatory update, generate specific action items:

Title: {update_title}
Summary: {update_summary}

Generate 3-5 specific action items. For each item, provide:
1. Description of the action
2. Suggested responsible party (e.g., "Administrator", "Clinical Staff", "IT")
3. Suggested due date (if deadline is {deadline.isoformat() if deadline else 'not specified'})

Format as a list of actions."""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a healthcare compliance specialist. Generate specific, actionable compliance steps."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400
                )
                
                # Parse response (simplified - in production would parse structured output)
                content = response.choices[0].message.content
                
                # Extract action items (simplified parsing)
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and (line.strip().startswith('-') or line.strip().startswith('1.') or line.strip().startswith('•')):
                        action_text = line.strip().lstrip('-').lstrip('1.').lstrip('•').strip()
                        if action_text and len(action_text) > 10:
                            action_items.append({
                                "description": action_text,
                                "responsible_party": self._extract_responsible_party(action_text),
                                "due_date": deadline or (date.today() + timedelta(days=30))
                            })
            except Exception as e:
                logger.warning(f"AI action generation failed: {e}")
        
        # Fallback action items if AI fails or not available
        if not action_items:
            action_items = [
                {
                    "description": f"Review {update_title} and assess impact on practice",
                    "responsible_party": "Administrator",
                    "due_date": deadline or (date.today() + timedelta(days=14))
                },
                {
                    "description": f"Update policies and procedures based on {update_title}",
                    "responsible_party": "Compliance Officer",
                    "due_date": deadline or (date.today() + timedelta(days=30))
                },
                {
                    "description": f"Train staff on new requirements from {update_title}",
                    "responsible_party": "Training Coordinator",
                    "due_date": deadline or (date.today() + timedelta(days=45))
                }
            ]
        
        return action_items[:5]  # Limit to 5 items
    
    def _extract_responsible_party(self, text: str) -> str:
        """Extract responsible party from action text"""
        text_lower = text.lower()
        
        if "admin" in text_lower or "manager" in text_lower:
            return "Administrator"
        elif "clinical" in text_lower or "provider" in text_lower or "physician" in text_lower:
            return "Clinical Staff"
        elif "it" in text_lower or "technology" in text_lower:
            return "IT Department"
        elif "compliance" in text_lower:
            return "Compliance Officer"
        elif "training" in text_lower or "staff" in text_lower:
            return "Training Coordinator"
        else:
            return "Practice Manager"

