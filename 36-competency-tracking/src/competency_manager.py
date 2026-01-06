"""
Competency management logic
"""
import logging
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class CompetencyManager:
    """Manages competency tracking"""
    
    def calculate_next_due(self, frequency: str, validation_date: date) -> date:
        """Calculate next due date based on frequency"""
        frequency_days = {
            "annual": 365,
            "biennial": 730,
            "quarterly": 90
        }
        
        days = frequency_days.get(frequency.lower(), 365)
        return validation_date + timedelta(days=days)
    
    def is_expired(self, next_due_date: Optional[date]) -> bool:
        """Check if competency is expired"""
        if not next_due_date:
            return False
        return next_due_date < date.today()
    
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


