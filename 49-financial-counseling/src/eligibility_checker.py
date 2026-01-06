"""
Eligibility checking logic
"""
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class EligibilityChecker:
    """Checks patient eligibility for assistance programs"""
    
    def check_eligibility(
        self,
        patient_data: Dict,
        program_criteria: Dict,
        program_threshold: float = None
    ) -> Tuple[float, str]:
        """
        Check eligibility and return match score and status
        
        Returns:
            Tuple of (match_score, status)
        """
        score = 0.0
        
        # Income check
        if program_threshold:
            if patient_data["income"] <= program_threshold:
                score += 50.0
                status = "eligible"
            elif patient_data["income"] <= program_threshold * 1.5:
                score += 30.0
                status = "potentially_eligible"
            else:
                status = "not_eligible"
        else:
            # No threshold, check other criteria
            score = 30.0
            status = "potentially_eligible"
        
        # Household size check
        if "household_size_limit" in program_criteria:
            if patient_data["household_size"] <= program_criteria["household_size_limit"]:
                score += 20.0
        
        # Insurance status check
        if "uninsured" in patient_data["insurance_status"].lower():
            score += 30.0
        
        final_score = min(score, 100.0)
        
        if final_score >= 70:
            status = "eligible"
        elif final_score >= 40:
            status = "potentially_eligible"
        else:
            status = "not_eligible"
        
        return final_score, status

