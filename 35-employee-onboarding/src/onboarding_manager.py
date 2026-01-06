"""
Onboarding workflow management
"""
import logging
from typing import List, Dict
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)


class OnboardingManager:
    """Manages employee onboarding workflows"""
    
    def calculate_onboarding_progress(self, requirements: List) -> Dict:
        """
        Calculate onboarding progress
        
        Args:
            requirements: List of document requirements
            
        Returns:
            Dictionary with progress metrics
        """
        total = len(requirements)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "progress_percentage": 0,
                "status": "not_started"
            }
        
        completed = sum(1 for r in requirements if r.uploaded and r.verified)
        progress = (completed / total * 100)
        
        if progress == 100:
            status = "completed"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "pending"
        
        return {
            "total": total,
            "completed": completed,
            "progress_percentage": round(progress, 2),
            "status": status
        }
    
    def get_upcoming_deadlines(self, requirements: List, days: int = 30) -> List[Dict]:
        """
        Get requirements with upcoming deadlines
        
        Args:
            requirements: List of document requirements
            days: Number of days to look ahead
            
        Returns:
            List of requirements with upcoming deadlines
        """
        cutoff_date = date.today() + timedelta(days=days)
        upcoming = []
        
        for req in requirements:
            if req.expiration_date and req.expiration_date <= cutoff_date:
                days_until = (req.expiration_date - date.today()).days
                upcoming.append({
                    "employee_id": req.employee_id,
                    "document_type": req.document_type,
                    "expiration_date": req.expiration_date.isoformat(),
                    "days_until": days_until,
                    "is_overdue": days_until < 0
                })
        
        return sorted(upcoming, key=lambda x: x["days_until"])


