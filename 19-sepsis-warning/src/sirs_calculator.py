"""
SIRS (Systemic Inflammatory Response Syndrome) calculator.
"""

import logging

logger = logging.getLogger(__name__)


class SIRSCalculator:
    """Calculates SIRS criteria for sepsis risk."""
    
    def calculate(self, vitals: dict) -> int:
        """
        Calculate SIRS score.
        
        SIRS criteria (1 point each):
        - Temp <36°C or >38°C
        - Heart rate >90
        - Respiratory rate >20
        - WBC <4k or >12k
        
        Args:
            vitals: Vital signs dictionary
            
        Returns:
            SIRS score (0-4)
        """
        score = 0
        
        temp_f = vitals.get("temperature", 98.6)
        temp_c = (temp_f - 32) * 5/9
        
        if temp_c < 36 or temp_c > 38:
            score += 1
        
        if vitals.get("heart_rate", 0) > 90:
            score += 1
        
        if vitals.get("respiratory_rate", 0) > 20:
            score += 1
        
        wbc = vitals.get("wbc")
        if wbc and (wbc < 4 or wbc > 12):
            score += 1
        
        return score
    
    def get_risk_level(self, score: int) -> str:
        """Get risk level based on SIRS score."""
        if score >= 2:
            return "High"
        elif score == 1:
            return "Medium"
        else:
            return "Low"

