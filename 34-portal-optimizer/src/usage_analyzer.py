"""
Portal usage analytics engine
"""
import logging
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class UsageAnalyzer:
    """Analyzes patient portal usage patterns"""
    
    def calculate_analytics(self, patients: List, usage_records: List) -> dict:
        """
        Calculate comprehensive usage analytics
        
        Args:
            patients: List of patient records
            usage_records: List of portal usage records
            
        Returns:
            Dictionary with analytics data
        """
        total_patients = len(patients)
        activated_count = sum(1 for u in usage_records if u.activated)
        activation_rate = (activated_count / total_patients * 100) if total_patients > 0 else 0
        
        # Feature usage
        messaging_users = sum(1 for u in usage_records if u.feature_messaging)
        bill_pay_users = sum(1 for u in usage_records if u.feature_bill_pay)
        scheduling_users = sum(1 for u in usage_records if u.feature_scheduling)
        
        # Active users (logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = sum(
            1 for u in usage_records
            if u.activated and u.last_login and u.last_login >= thirty_days_ago
        )
        
        # Usage by age group
        age_groups = defaultdict(lambda: {"total": 0, "activated": 0})
        for patient in patients:
            if patient.age:
                if patient.age < 30:
                    group = "18-29"
                elif patient.age < 40:
                    group = "30-39"
                elif patient.age < 50:
                    group = "40-49"
                elif patient.age < 60:
                    group = "50-59"
                else:
                    group = "60+"
                
                age_groups[group]["total"] += 1
                usage = next((u for u in usage_records if u.patient_id == patient.patient_id), None)
                if usage and usage.activated:
                    age_groups[group]["activated"] += 1
        
        return {
            "total_patients": total_patients,
            "activated_patients": activated_count,
            "activation_rate": round(activation_rate, 2),
            "active_users_30d": active_users,
            "feature_usage": {
                "messaging": messaging_users,
                "bill_pay": bill_pay_users,
                "scheduling": scheduling_users
            },
            "usage_by_age": {
                group: {
                    "total": data["total"],
                    "activated": data["activated"],
                    "rate": round((data["activated"] / data["total"] * 100) if data["total"] > 0 else 0, 2)
                }
                for group, data in age_groups.items()
            }
        }


