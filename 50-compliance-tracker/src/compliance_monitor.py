"""
Compliance monitoring and relevance filtering
"""
import logging
import os
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class ComplianceMonitor:
    """Monitors and filters regulatory updates"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq: {e}")
    
    def calculate_relevance(
        self,
        practice_data: Dict,
        update_data: Dict
    ) -> int:
        """
        Calculate relevance score (0-100) for update to practice
        
        Args:
            practice_data: Practice profile data
            update_data: Regulatory update data
            
        Returns:
            Relevance score 0-100
        """
        score = 0
        
        # State matching
        if "state" in update_data.get("full_text", "").lower():
            if practice_data["state"].lower() in update_data["full_text"].lower():
                score += 30
        
        # Practice type matching
        practice_type = practice_data["practice_type"].lower()
        if practice_type in update_data.get("full_text", "").lower():
            score += 25
        
        # Service matching
        services = practice_data.get("services_offered", [])
        for service in services:
            if service.lower() in update_data.get("full_text", "").lower():
                score += 15
                break
        
        # Source relevance
        source = update_data.get("source", "").lower()
        if source in ["cms", "cdc", "osha"]:
            score += 20  # High relevance sources
        elif source in ["state_health", "medicare", "medicaid"]:
            score += 15
        
        # Use AI for complex relevance if available
        if self.client and score < 50:
            try:
                prompt = f"""Determine if this regulatory update is relevant to this practice:

Practice: {practice_data['practice_type']} in {practice_data['state']}
Services: {', '.join(practice_data.get('services_offered', []))}

Update: {update_data['title']}
Summary: {update_data.get('summary', '')[:200]}

Is this relevant? Return a relevance score 0-100."""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50
                )
                
                # Try to extract score from response
                content = response.choices[0].message.content
                try:
                    ai_score = int(''.join(filter(str.isdigit, content))[:2])
                    if ai_score > score:
                        score = ai_score
                except:
                    pass
            except Exception as e:
                logger.warning(f"AI relevance check failed: {e}")
        
        return min(score, 100)
    
    def determine_urgency(self, text: str) -> str:
        """Determine urgency level from text"""
        text_lower = text.lower()
        
        high_keywords = ["immediate", "urgent", "deadline", "required", "mandatory", "critical"]
        medium_keywords = ["recommended", "should", "important", "consider"]
        
        if any(keyword in text_lower for keyword in high_keywords):
            return "high"
        elif any(keyword in text_lower for keyword in medium_keywords):
            return "medium"
        else:
            return "low"
    
    def determine_impact(self, text: str) -> str:
        """Determine impact level from text"""
        text_lower = text.lower()
        
        high_keywords = ["penalty", "fine", "violation", "enforcement", "audit"]
        medium_keywords = ["compliance", "regulation", "standard", "requirement"]
        
        if any(keyword in text_lower for keyword in high_keywords):
            return "high"
        elif any(keyword in text_lower for keyword in medium_keywords):
            return "medium"
        else:
            return "low"

