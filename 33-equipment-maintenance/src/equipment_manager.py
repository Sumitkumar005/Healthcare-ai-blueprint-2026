"""
Equipment inventory management
"""
import logging
from typing import Optional
from datetime import date

logger = logging.getLogger(__name__)


class EquipmentManager:
    """Manages equipment inventory"""
    
    def validate_equipment(self, equipment_type: str, serial_number: str) -> tuple[bool, Optional[str]]:
        """
        Validate equipment data
        
        Args:
            equipment_type: Type of equipment
            serial_number: Serial number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not equipment_type or not equipment_type.strip():
            return False, "Equipment type is required"
        
        if not serial_number or not serial_number.strip():
            return False, "Serial number is required"
        
        if len(serial_number) < 3:
            return False, "Serial number must be at least 3 characters"
        
        return True, None
    
    def get_maintenance_frequency_days(self, frequency: str) -> Optional[int]:
        """
        Convert maintenance frequency to days
        
        Args:
            frequency: Frequency string (annual, semi-annual, quarterly, monthly)
            
        Returns:
            Number of days or None if invalid
        """
        frequency_map = {
            "annual": 365,
            "semi-annual": 180,
            "quarterly": 90,
            "monthly": 30
        }
        
        return frequency_map.get(frequency.lower())


