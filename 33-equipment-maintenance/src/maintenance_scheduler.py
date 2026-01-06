"""
Maintenance scheduling logic
"""
import logging
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class MaintenanceScheduler:
    """Handles maintenance scheduling calculations"""
    
    def calculate_next_due(
        self,
        frequency: str,
        last_date: date
    ) -> Optional[date]:
        """
        Calculate next maintenance due date
        
        Args:
            frequency: Maintenance frequency (annual, semi-annual, quarterly, monthly)
            last_date: Last maintenance date or purchase date
            
        Returns:
            Next due date
        """
        frequency_days = {
            "annual": 365,
            "semi-annual": 180,
            "quarterly": 90,
            "monthly": 30
        }
        
        days = frequency_days.get(frequency.lower())
        if not days:
            logger.warning(f"Unknown frequency: {frequency}")
            return None
        
        return last_date + timedelta(days=days)
    
    def get_alert_level(self, days_until: int) -> str:
        """
        Determine alert level based on days until maintenance
        
        Args:
            days_until: Days until maintenance is due (negative if overdue)
            
        Returns:
            Alert level string
        """
        if days_until < 0:
            return "Overdue"
        elif days_until <= 7:
            return "High"
        elif days_until <= 14:
            return "Medium"
        elif days_until <= 30:
            return "Low"
        else:
            return "Normal"
    
    def should_alert(self, days_until: int, alert_days: int = 30) -> bool:
        """
        Check if maintenance should trigger an alert
        
        Args:
            days_until: Days until maintenance is due
            alert_days: Number of days before due date to start alerting
            
        Returns:
            True if alert should be sent
        """
        return days_until <= alert_days


