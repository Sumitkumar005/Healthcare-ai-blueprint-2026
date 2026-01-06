"""
Medication adherence tracking.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdherenceTracker:
    """Tracks medication adherence."""
    
    def __init__(self):
        self.confirmations = {}  # patient -> list of confirmations
        self.schedules = {}  # patient -> medication schedules
    
    def record_confirmation(self, confirmation: Dict):
        """Record medication confirmation."""
        patient = confirmation["patient_name"]
        if patient not in self.confirmations:
            self.confirmations[patient] = []
        
        self.confirmations[patient].append({
            "medication": confirmation["medication_name"],
            "time": confirmation["scheduled_time"],
            "confirmed_at": datetime.now().isoformat()
        })
    
    def calculate_adherence(self, patient: str) -> float:
        """
        Calculate adherence rate for patient.
        
        Args:
            patient: Patient name
            
        Returns:
            Adherence rate (0-100)
        """
        # Simplified calculation
        if patient not in self.confirmations:
            return 0.0
        
        # Count confirmations in last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_confirmations = [
            c for c in self.confirmations[patient]
            if datetime.fromisoformat(c["confirmed_at"]) > week_ago
        ]
        
        # Assume 2 doses per day for calculation
        expected_doses = 14  # 7 days * 2 doses
        actual_doses = len(recent_confirmations)
        
        return min(100.0, (actual_doses / expected_doses) * 100) if expected_doses > 0 else 0.0
    
    def get_provider_dashboard(self) -> List[Dict]:
        """Get provider dashboard with all patients."""
        dashboard = []
        for patient in set(list(self.confirmations.keys()) + list(self.schedules.keys())):
            adherence = self.calculate_adherence(patient)
            dashboard.append({
                "patient": patient,
                "adherence_rate": adherence,
                "status": "Needs Intervention" if adherence < 80 else "Good"
            })
        return dashboard

