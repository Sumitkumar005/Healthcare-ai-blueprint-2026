"""
Evacuation planning logic
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class EvacuationPlanner:
    """Plans evacuation routes and priorities"""
    
    def generate_plan(self, patients: List, floor: str) -> Dict:
        """Generate evacuation plan"""
        # Prioritize patients
        priority_patients = []
        for patient in patients:
            priority = self._calculate_priority(patient)
            priority_patients.append({
                "patient_id": patient.patient_id,
                "room_number": patient.room_number,
                "mobility_level": patient.mobility_level,
                "acuity_level": patient.acuity_level,
                "priority": priority
            })
        
        # Sort by priority
        priority_patients.sort(key=lambda x: x["priority"])
        
        # Generate routes (simplified)
        routes = []
        for patient in priority_patients:
            route = self._calculate_route(patient["room_number"])
            routes.append({
                "patient_id": patient["patient_id"],
                "route": route,
                "priority": patient["priority"]
            })
        
        return {
            "floor": floor,
            "total_patients": len(patients),
            "evacuation_plan": routes
        }
    
    def _calculate_priority(self, patient) -> int:
        """Calculate evacuation priority (lower = higher priority)"""
        priority = 0
        
        # Non-ambulatory first
        if patient.mobility_level == "stretcher":
            priority = 1
        elif patient.mobility_level == "wheelchair":
            priority = 2
        else:
            priority = 3
        
        # High acuity increases priority
        if patient.acuity_level == "high":
            priority -= 1
        
        return priority
    
    def _calculate_route(self, room_number: str) -> str:
        """Calculate evacuation route (simplified)"""
        # In production, would use pathfinding algorithm
        return f"From {room_number} to nearest exit"


