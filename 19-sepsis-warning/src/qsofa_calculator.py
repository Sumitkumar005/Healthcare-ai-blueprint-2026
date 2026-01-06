"""
qSOFA (Quick SOFA) calculator.
"""

import logging

logger = logging.getLogger(__name__)


class QSOFACalculator:
    """Calculates qSOFA score for sepsis risk."""
    
    def calculate(self, vitals: dict) -> int:
        """
        Calculate qSOFA score.
        
        qSOFA criteria (1 point each):
        - Altered mental status
        - Respiratory rate ≥22
        - Systolic BP ≤100
        
        Args:
            vitals: Vital signs dictionary
            
        Returns:
            qSOFA score (0-3)
        """
        score = 0
        
        if vitals.get("mental_status", "").lower() == "altered":
            score += 1
        
        if vitals.get("respiratory_rate", 0) >= 22:
            score += 1
        
        if vitals.get("systolic_bp", 0) <= 100:
            score += 1
        
        return score
    
    def get_risk_level(self, score: int) -> str:
        """Get risk level based on qSOFA score."""
        if score >= 2:
            return "High"
        elif score == 1:
            return "Medium"
        else:
            return "Low"

