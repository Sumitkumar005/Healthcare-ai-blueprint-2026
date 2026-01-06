"""
Referral performance tracking
"""
import logging
from typing import List
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReferralPerformanceTracker:
    """Tracks referral network performance"""
    
    def calculate_performance(self, referrals: List) -> dict:
        """Calculate performance metrics by specialist"""
        by_specialist = defaultdict(lambda: {"total": 0, "completed": 0, "ratings": []})
        
        for referral in referrals:
            spec = referral.specialist_name
            by_specialist[spec]["total"] += 1
            if referral.completed:
                by_specialist[spec]["completed"] += 1
            if referral.satisfaction_rating:
                by_specialist[spec]["ratings"].append(referral.satisfaction_rating)
        
        results = {}
        for spec, data in by_specialist.items():
            completion_rate = (data["completed"] / data["total"] * 100) if data["total"] > 0 else 0
            avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
            
            results[spec] = {
                "total_referrals": data["total"],
                "completion_rate": round(completion_rate, 2),
                "average_rating": round(avg_rating, 2) if avg_rating > 0 else None
            }
        
        return {"specialists": results}

