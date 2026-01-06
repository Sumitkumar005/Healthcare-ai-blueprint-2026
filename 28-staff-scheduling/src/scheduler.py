"""
Schedule optimization logic
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ScheduleOptimizer:
    """Optimizes staff schedules"""
    
    def generate_schedule(
        self,
        staff_members: List,
        start_date: datetime,
        end_date: datetime,
        patient_census: int,
        acuity_level: str
    ) -> Dict:
        """Generate optimized schedule"""
        # Calculate required staff based on patient census and acuity
        required_nurses = self._calculate_required_staff(patient_census, acuity_level)
        
        # Simple scheduling algorithm (can be enhanced with OR-Tools)
        schedule = {}
        current_date = start_date
        
        while current_date <= end_date:
            day_schedule = []
            # Assign staff for this day
            for i, staff in enumerate(staff_members[:required_nurses]):
                day_schedule.append({
                    "staff_id": staff.id,
                    "staff_name": staff.name,
                    "shift": "Day" if i % 2 == 0 else "Night"
                })
            
            schedule[current_date.strftime("%Y-%m-%d")] = day_schedule
            current_date += timedelta(days=1)
        
        return schedule
    
    def _calculate_required_staff(self, census: int, acuity: str) -> int:
        """Calculate required staff based on census and acuity"""
        # Simple ratio calculation
        if acuity == "High":
            ratio = 1  # 1 nurse per patient
        elif acuity == "Medium":
            ratio = 3  # 1 nurse per 3 patients
        else:
            ratio = 5  # 1 nurse per 5 patients
        
        return max(1, (census + ratio - 1) // ratio)  # Ceiling division

