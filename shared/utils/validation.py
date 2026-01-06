"""
Validation utilities for medical data.
"""

import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_medical_input(data: Dict[str, Any]) -> bool:
    """
    Validate medical data inputs.
    
    Args:
        data: Dictionary containing medical data
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")
    
    # Check for required fields (basic validation)
    required_fields = []
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    return True


def validate_patient_data(patient_data: Dict[str, Any]) -> bool:
    """
    Validate patient data structure.
    
    Args:
        patient_data: Patient data dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(patient_data, dict):
        raise ValueError("Patient data must be a dictionary")
    
    # Validate patient name if present
    if "name" in patient_data:
        name = patient_data["name"]
        if not isinstance(name, str) or len(name.strip()) < 2:
            raise ValueError("Patient name must be at least 2 characters")
    
    # Validate date if present
    if "date" in patient_data:
        date_str = patient_data["date"]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    return True


def validate_medication_name(medication: str) -> bool:
    """
    Validate medication name format.
    
    Args:
        medication: Medication name string
        
    Returns:
        True if valid format
    """
    if not medication or not isinstance(medication, str):
        return False
    
    # Basic validation: non-empty, reasonable length
    medication = medication.strip()
    if len(medication) < 2 or len(medication) > 100:
        return False
    
    return True


def validate_vital_signs(vitals: Dict[str, Any]) -> bool:
    """
    Validate vital signs data.
    
    Args:
        vitals: Vital signs dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not isinstance(vitals, dict):
        raise ValueError("Vital signs must be a dictionary")
    
    # Validate temperature if present
    if "temperature" in vitals:
        temp = vitals["temperature"]
        if isinstance(temp, (int, float)):
            if temp < 90 or temp > 110:  # Fahrenheit range
                raise ValueError("Temperature out of reasonable range (90-110°F)")
    
    # Validate heart rate if present
    if "heart_rate" in vitals:
        hr = vitals["heart_rate"]
        if isinstance(hr, (int, float)):
            if hr < 30 or hr > 200:
                raise ValueError("Heart rate out of reasonable range (30-200 bpm)")
    
    # Validate blood pressure if present
    if "blood_pressure" in vitals:
        bp = vitals["blood_pressure"]
        if isinstance(bp, str):
            # Format: "120/80"
            match = re.match(r'(\d+)/(\d+)', bp)
            if match:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                if systolic < 50 or systolic > 250:
                    raise ValueError("Systolic BP out of range")
                if diastolic < 30 or diastolic > 150:
                    raise ValueError("Diastolic BP out of range")
    
    return True


