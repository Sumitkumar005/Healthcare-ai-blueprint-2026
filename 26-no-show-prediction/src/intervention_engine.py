"""
Intervention engine for no-show prevention
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


class InterventionEngine:
    """Manages interventions for high-risk appointments"""
    
    def get_interventions(self, risk_score: float, risk_level: str) -> List[str]:
        """
        Get recommended interventions based on risk score
        
        Args:
            risk_score: Predicted no-show probability (0-1)
            risk_level: "High", "Medium", or "Low"
            
        Returns:
            List of intervention actions
        """
        interventions = []
        
        if risk_level == "High":
            interventions.extend([
                "Send extra reminder 48 hours before",
                "Send reminder 24 hours before",
                "Send reminder 2 hours before",
                "Call patient day before",
                "Add to waitlist for backup"
            ])
        elif risk_level == "Medium":
            interventions.extend([
                "Send reminder 24 hours before",
                "Send reminder 2 hours before"
            ])
        else:
            interventions.append("Send standard reminder 24 hours before")
        
        return interventions
    
    def get_recommendations(self, risk_score: float) -> List[str]:
        """
        Get scheduling recommendations
        
        Args:
            risk_score: Predicted no-show probability
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.extend([
                "Consider overbooking this time slot",
                "Offer alternative appointment times",
                "Consider same-day scheduling if available"
            ])
        elif risk_score >= 0.4:
            recommendations.append("Monitor this appointment closely")
        
        return recommendations



