"""
Morse Fall Scale calculator.
"""

import logging

logger = logging.getLogger(__name__)


class MorseFallScale:
    """Morse Fall Scale assessment calculator."""
    
    def calculate_score(self, assessment: dict) -> int:
        """
        Calculate Morse Fall Scale score.
        
        Args:
            assessment: Dictionary with assessment values
            
        Returns:
            Total score (0-125)
        """
        score = (
            assessment.get("history_of_falling", 0) +
            assessment.get("secondary_diagnosis", 0) +
            assessment.get("ambulatory_aid", 0) +
            assessment.get("iv_heparin_lock", 0) +
            assessment.get("gait", 0) +
            assessment.get("mental_status", 0)
        )
        return score
    
    def get_risk_level(self, score: int) -> str:
        """
        Get risk level based on score.
        
        Args:
            score: Morse Fall Scale score
            
        Returns:
            Risk level string
        """
        if score <= 24:
            return "Low Risk"
        elif score <= 50:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def get_recommendations(self, score: int) -> str:
        """
        Get intervention recommendations based on score.
        
        Args:
            score: Morse Fall Scale score
            
        Returns:
            Recommendations string
        """
        if score <= 24:
            return "Standard fall precautions. Regular monitoring."
        elif score <= 50:
            return "Enhanced fall precautions. Consider bed alarm, non-slip footwear, frequent rounding."
        else:
            return "High fall risk. Implement comprehensive fall prevention: bed alarm, 1:1 monitoring if needed, non-slip footwear, clear pathways, frequent rounding, consider sitter."

