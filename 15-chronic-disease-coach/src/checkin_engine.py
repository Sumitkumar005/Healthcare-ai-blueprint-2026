"""
Chronic disease check-in engine.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CheckInEngine:
    """Manages disease-specific check-ins."""
    
    def process_checkin(self, checkin_data: Dict) -> Dict:
        """Process check-in data."""
        disease_type = checkin_data.get("disease_type")
        data = checkin_data.get("data", {})
        
        if disease_type == "diabetes":
            return self._process_diabetes(data)
        elif disease_type == "chf":
            return self._process_chf(data)
        elif disease_type == "copd":
            return self._process_copd(data)
        else:
            return {"status": "unknown_disease"}
    
    def _process_diabetes(self, data: Dict) -> Dict:
        """Process diabetes check-in."""
        blood_sugar = data.get("blood_sugar", 0)
        return {
            "status": "good" if 80 <= blood_sugar <= 180 else "needs_attention",
            "message": f"Blood sugar: {blood_sugar} mg/dL"
        }
    
    def _process_chf(self, data: Dict) -> Dict:
        """Process CHF check-in."""
        weight = data.get("weight", 0)
        return {
            "status": "good" if weight < 200 else "needs_attention",
            "message": f"Weight: {weight} lbs"
        }
    
    def _process_copd(self, data: Dict) -> Dict:
        """Process COPD check-in."""
        breathing = data.get("breathing_difficulty", 0)
        return {
            "status": "good" if breathing < 5 else "needs_attention",
            "message": f"Breathing difficulty: {breathing}/10"
        }

