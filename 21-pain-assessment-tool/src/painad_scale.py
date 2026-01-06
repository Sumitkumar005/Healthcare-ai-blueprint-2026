"""
PAINAD (Pain Assessment in Advanced Dementia) Scale calculator.
"""

import logging

logger = logging.getLogger(__name__)


class PAINADScale:
    """PAINAD scale assessment calculator."""
    
    def calculate_score(self, assessment: dict) -> int:
        """
        Calculate PAINAD score.
        
        Args:
            assessment: Dictionary with assessment values (0-2 each)
            
        Returns:
            Total score (0-10)
        """
        score = (
            assessment.get("breathing", 0) +
            assessment.get("negative_vocalization", 0) +
            assessment.get("facial_expression", 0) +
            assessment.get("body_language", 0) +
            assessment.get("consolability", 0)
        )
        return score
    
    def get_pain_level(self, score: int) -> str:
        """
        Get pain level based on score.
        
        Args:
            score: PAINAD score (0-10)
            
        Returns:
            Pain level string
        """
        if score == 0:
            return "No Pain"
        elif score <= 3:
            return "Mild Pain"
        elif score <= 6:
            return "Moderate Pain"
        else:
            return "Severe Pain"
    
    def get_interpretation(self, score: int) -> str:
        """
        Get interpretation and recommendations.
        
        Args:
            score: PAINAD score
            
        Returns:
            Interpretation string
        """
        if score == 0:
            return "No pain detected. Continue monitoring."
        elif score <= 3:
            return "Mild pain. Consider non-pharmacologic interventions. Monitor closely."
        elif score <= 6:
            return "Moderate pain. Consider pain medication. Assess response to intervention."
        else:
            return "Severe pain. Immediate pain management intervention needed. Consider PRN medication and reassess frequently."

