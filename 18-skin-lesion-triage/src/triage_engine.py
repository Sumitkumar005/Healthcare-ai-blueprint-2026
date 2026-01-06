"""
Triage recommendation engine.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class TriageEngine:
    """Provides triage recommendations based on risk scores."""
    
    def get_recommendation(self, risk_score: float) -> Dict:
        """
        Get triage recommendation based on risk score.
        
        Args:
            risk_score: Risk score (0-10)
            
        Returns:
            Recommendation dictionary
        """
        if risk_score >= 7:
            return {
                "level": "Urgent Referral",
                "rationale": "High risk features present. Urgent dermatology referral recommended for evaluation."
            }
        elif risk_score >= 4:
            return {
                "level": "Routine Referral",
                "rationale": "Moderate risk features. Routine dermatology referral recommended within 1-2 months."
            }
        else:
            return {
                "level": "Monitor/Reassure",
                "rationale": "Low risk features. Continue monitoring. Reassure patient. Consider routine follow-up."
            }

