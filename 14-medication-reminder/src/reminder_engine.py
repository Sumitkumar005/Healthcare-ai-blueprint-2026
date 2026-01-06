"""
Medication reminder engine.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ReminderEngine:
    """Manages medication schedules and reminders."""
    
    def __init__(self):
        self.medications = {}
    
    def add_medication(self, medication_data: Dict):
        """Add medication schedule."""
        patient = medication_data["patient_name"]
        if patient not in self.medications:
            self.medications[patient] = []
        
        self.medications[patient].append({
            "medication_name": medication_data["medication_name"],
            "dose": medication_data["dose"],
            "frequency": medication_data["frequency"],
            "times": medication_data["times"]
        })
    
    def get_medications(self, patient: str) -> List[Dict]:
        """Get patient medications."""
        return self.medications.get(patient, [])

