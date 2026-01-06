"""
Post-discharge follow-up engine.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)


class FollowUpEngine:
    """Manages post-discharge follow-ups."""
    
    def __init__(self):
        self.followups = {}
        self.responses = {}
        self.flagged_patients = []
    
    def schedule_followups(self, patient_name: str, discharge_date: str):
        """Schedule follow-ups at 48 hours and 7 days."""
        discharge = datetime.fromisoformat(discharge_date)
        followup_48h = discharge + timedelta(hours=48)
        followup_7d = discharge + timedelta(days=7)
        
        self.followups[patient_name] = {
            "discharge_date": discharge_date,
            "followup_48h": followup_48h.isoformat(),
            "followup_7d": followup_7d.isoformat(),
            "completed_48h": False,
            "completed_7d": False
        }
    
    def process_response(self, follow_up_id: int, responses: Dict) -> bool:
        """Process follow-up response and check for concerns."""
        # Check for concerning responses
        concerns = []
        if responses.get("fever", "").lower() == "yes":
            concerns.append("Fever reported")
        if responses.get("chest_pain", "").lower() == "yes":
            concerns.append("Chest pain reported - URGENT")
        if responses.get("wound_problems", "").lower() == "yes":
            concerns.append("Wound problems reported")
        
        if concerns:
            self.flagged_patients.append({
                "follow_up_id": follow_up_id,
                "concerns": concerns,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False
    
    def get_flagged_patients(self) -> List[Dict]:
        """Get patients flagged for immediate attention."""
        return self.flagged_patients
    
    def get_upcoming_followups(self) -> List[Dict]:
        """Get upcoming follow-ups."""
        upcoming = []
        for patient, data in self.followups.items():
            if not data["completed_48h"]:
                upcoming.append({
                    "patient": patient,
                    "type": "48-hour",
                    "due": data["followup_48h"]
                })
            if not data["completed_7d"]:
                upcoming.append({
                    "patient": patient,
                    "type": "7-day",
                    "due": data["followup_7d"]
                })
        return upcoming

