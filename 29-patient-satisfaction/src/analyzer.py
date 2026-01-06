"""
Survey analysis engine
"""
import logging
import os
from typing import List
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class SurveyAnalyzer:
    """Analyzes patient satisfaction surveys"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
    
    def analyze(self, responses: List) -> dict:
        """Analyze survey responses"""
        # Calculate average scores
        scores_by_category = {}
        comments = []
        
        for response in responses:
            category = response.category
            if category not in scores_by_category:
                scores_by_category[category] = []
            scores_by_category[category].append(response.score)
            
            if response.comment:
                comments.append(response.comment)
        
        # Calculate averages
        averages = {
            cat: sum(scores) / len(scores)
            for cat, scores in scores_by_category.items()
        }
        
        # Analyze comments with AI if available
        themes = []
        if comments and self.client:
            try:
                prompt = f"Analyze these patient comments and extract main themes:\n\n" + "\n".join(comments[:10])
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                themes = [response.choices[0].message.content]
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
        
        return {
            "average_scores": averages,
            "total_responses": len(responses),
            "themes": themes,
            "action_items": self._generate_action_items(averages)
        }
    
    def _generate_action_items(self, averages: dict) -> List[dict]:
        """Generate action items based on low scores"""
        items = []
        for category, score in averages.items():
            if score < 3.0:  # Low score threshold
                items.append({
                    "category": category,
                    "priority": "High",
                    "suggestion": f"Improve {category} based on patient feedback"
                })
        return items

