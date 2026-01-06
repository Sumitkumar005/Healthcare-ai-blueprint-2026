"""
Intervention recommendations for burnout prevention
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


class InterventionEngine:
    """Generates intervention recommendations"""
    
    def get_interventions(self, risk_score: float) -> List[str]:
        """Get intervention recommendations based on risk score"""
        interventions = []
        
        if risk_score >= 70:
            interventions.extend([
                "Immediate schedule adjustment recommended",
                "Inbox management support needed",
                "Peer support resources",
                "Administrative burden reduction",
                "Consider temporary workload reduction"
            ])
        elif risk_score >= 40:
            interventions.extend([
                "Monitor workload closely",
                "Encourage vacation utilization",
                "Inbox management strategies",
                "Schedule optimization"
            ])
        else:
            interventions.append("Continue current practices")
        
        return interventions


