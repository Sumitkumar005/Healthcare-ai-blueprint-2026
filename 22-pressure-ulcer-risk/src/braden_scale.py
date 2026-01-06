"""
Braden Scale calculator.
"""

import logging

logger = logging.getLogger(__name__)


class BradenScale:
    """Calculates Braden Scale score for pressure ulcer risk."""
    
    def calculate(self, assessment: dict) -> int:
        """
        Calculate Braden Scale score.
        
        Lower score = higher risk
        Range: 6-23
        
        Args:
            assessment: Assessment dictionary
            
        Returns:
            Braden score
        """
        score = (
            assessment.get("sensory_perception", 4) +
            assessment.get("moisture", 4) +
            assessment.get("activity", 4) +
            assessment.get("mobility", 4) +
            assessment.get("nutrition", 4) +
            assessment.get("friction_shear", 3)
        )
        return score
    
    def get_risk_level(self, score: int) -> str:
        """Get risk level based on score."""
        if score <= 9:
            return "Severe Risk"
        elif score <= 12:
            return "High Risk"
        elif score <= 14:
            return "Moderate Risk"
        elif score <= 18:
            return "Mild Risk"
        else:
            return "No Risk"

