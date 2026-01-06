"""
Time tracking logic
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TimeTracker:
    """Tracks staff time for tasks"""
    
    def calculate_duration(self, start_time: datetime, end_time: Optional[datetime]) -> Optional[float]:
        """Calculate duration in minutes"""
        if not start_time or not end_time:
            return None
        
        duration = (end_time - start_time).total_seconds() / 60
        return duration
    
    def validate_task_category(self, category: str, role: str) -> bool:
        """Validate task category for role"""
        valid_categories = {
            "nursing": ["patient_care", "documentation", "medication", "communication"],
            "physician": ["patient_care", "documentation", "consultation", "procedures"]
        }
        
        role_categories = valid_categories.get(role.lower(), [])
        return category in role_categories


