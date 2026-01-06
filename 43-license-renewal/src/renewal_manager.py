"""
License renewal management
"""
import logging
from datetime import date, timedelta
from typing import List

logger = logging.getLogger(__name__)


class RenewalManager:
    """Manages license renewals"""
    
    def check_renewal_due(self, expiration_date: date, days: int = 90) -> bool:
        """Check if renewal is due within specified days"""
        if not expiration_date:
            return False
        days_until = (expiration_date - date.today()).days
        return 0 <= days_until <= days
    
    def get_alert_level(self, days_until: int) -> str:
        """Get alert level based on days until expiration"""
        if days_until < 0:
            return "Overdue"
        elif days_until <= 30:
            return "High"
        elif days_until <= 60:
            return "Medium"
        elif days_until <= 90:
            return "Low"
        return "Normal"
    
    def check_cme_requirements(self, cme_required: float, cme_completed: float) -> dict:
        """Check CME requirement status"""
        remaining = max(0, cme_required - cme_completed)
        percentage = (cme_completed / cme_required * 100) if cme_required > 0 else 100
        
        return {
            "required": cme_required,
            "completed": cme_completed,
            "remaining": remaining,
            "percentage": round(percentage, 2),
            "status": "complete" if remaining == 0 else "in_progress"
        }


