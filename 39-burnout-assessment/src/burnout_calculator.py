"""
Burnout risk calculation
"""
import logging

logger = logging.getLogger(__name__)


class BurnoutRiskCalculator:
    """Calculates provider burnout risk scores"""
    
    def calculate_risk(
        self,
        patient_volume: int,
        appointment_hours: float,
        inbox_messages: int,
        after_hours_work: float,
        vacation_days_used: int,
        patient_complexity: float
    ) -> float:
        """Calculate burnout risk score (0-100)"""
        risk = 0.0
        
        # Patient volume factor (0-25 points)
        if patient_volume > 25:
            risk += 25
        elif patient_volume > 20:
            risk += 20
        elif patient_volume > 15:
            risk += 15
        else:
            risk += patient_volume * 0.8
        
        # Appointment hours factor (0-20 points)
        if appointment_hours > 50:
            risk += 20
        elif appointment_hours > 40:
            risk += 15
        elif appointment_hours > 30:
            risk += 10
        
        # Inbox burden factor (0-20 points)
        if inbox_messages > 100:
            risk += 20
        elif inbox_messages > 50:
            risk += 15
        elif inbox_messages > 25:
            risk += 10
        
        # After-hours work factor (0-15 points)
        if after_hours_work > 10:
            risk += 15
        elif after_hours_work > 5:
            risk += 10
        
        # Vacation utilization factor (0-10 points)
        if vacation_days_used < 5:
            risk += 10
        elif vacation_days_used < 10:
            risk += 5
        
        # Patient complexity factor (0-10 points)
        if patient_complexity > 1.5:
            risk += 10
        elif patient_complexity > 1.2:
            risk += 5
        
        return min(risk, 100.0)  # Cap at 100


