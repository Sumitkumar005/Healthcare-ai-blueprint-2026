"""
Campaign management for portal activation
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CampaignManager:
    """Manages activation campaigns"""
    
    def get_target_patients(
        self,
        segment: str,
        patients: List,
        usage_records: List
    ) -> List[Dict]:
        """
        Get target patients for a campaign segment
        
        Args:
            segment: Target segment (inactive, low_usage, etc.)
            patients: List of all patients
            usage_records: List of usage records
            
        Returns:
            List of target patient dictionaries
        """
        targets = []
        
        if segment == "inactive":
            # Patients who haven't activated
            for patient in patients:
                usage = next(
                    (u for u in usage_records if u.patient_id == patient.patient_id),
                    None
                )
                if not usage or not usage.activated:
                    targets.append({
                        "patient_id": patient.patient_id,
                        "email": patient.email,
                        "phone": patient.phone
                    })
        
        elif segment == "low_usage":
            # Activated but low usage (no login in 90 days)
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            for patient in patients:
                usage = next(
                    (u for u in usage_records if u.patient_id == patient.patient_id),
                    None
                )
                if usage and usage.activated:
                    if not usage.last_login or usage.last_login < ninety_days_ago:
                        targets.append({
                            "patient_id": patient.patient_id,
                            "email": patient.email,
                            "phone": patient.phone
                        })
        
        elif segment == "feature_non_users":
            # Activated but not using key features
            for patient in patients:
                usage = next(
                    (u for u in usage_records if u.patient_id == patient.patient_id),
                    None
                )
                if usage and usage.activated:
                    if not (usage.feature_messaging or usage.feature_bill_pay or usage.feature_scheduling):
                        targets.append({
                            "patient_id": patient.patient_id,
                            "email": patient.email,
                            "phone": patient.phone
                        })
        
        return targets
    
    def calculate_campaign_effectiveness(
        self,
        campaign_id: int,
        results: List
    ) -> Dict:
        """
        Calculate campaign effectiveness metrics
        
        Args:
            campaign_id: Campaign ID
            results: List of campaign results
            
        Returns:
            Dictionary with effectiveness metrics
        """
        total_sent = len(results)
        if total_sent == 0:
            return {
                "total_sent": 0,
                "open_rate": 0,
                "click_rate": 0,
                "activation_rate": 0
            }
        
        opened = sum(1 for r in results if r.opened)
        clicked = sum(1 for r in results if r.clicked)
        activated = sum(1 for r in results if r.activated)
        
        return {
            "total_sent": total_sent,
            "opened": opened,
            "clicked": clicked,
            "activated": activated,
            "open_rate": round((opened / total_sent * 100), 2),
            "click_rate": round((clicked / total_sent * 100), 2),
            "activation_rate": round((activated / total_sent * 100), 2)
        }


