"""
Clinical trial matching logic
"""
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class TrialMatcher:
    """Matches patients to clinical trials"""
    
    def match_patient_to_trial(
        self,
        patient_data: Dict,
        trial_data: Dict
    ) -> Tuple[float, str]:
        """
        Match patient to trial
        
        Returns:
            Tuple of (match_score, reason)
        """
        score = 0.0
        reasons = []
        
        # Check inclusion criteria
        diagnoses = patient_data.get("diagnoses", [])
        condition = trial_data.get("condition", "").lower()
        
        # Check if patient has matching condition
        for diagnosis in diagnoses:
            if condition in diagnosis.lower() or diagnosis.lower() in condition:
                score += 50.0
                reasons.append(f"Patient has condition: {diagnosis}")
                break
        
        # Check exclusion criteria
        medications = patient_data.get("medications", [])
        exclusion_criteria = trial_data.get("exclusion_criteria", [])
        
        excluded = False
        for exclusion in exclusion_criteria:
            for med in medications:
                if exclusion.lower() in med.lower():
                    excluded = True
                    reasons.append(f"Excluded due to medication: {med}")
                    break
        
        if excluded:
            return 0.0, "; ".join(reasons)
        
        # Age check (simplified)
        demographics = patient_data.get("demographics", {})
        age = demographics.get("age", 0)
        if 18 <= age <= 75:
            score += 20.0
            reasons.append("Age within typical range")
        
        # Calculate final score
        final_score = min(score, 100.0)
        
        return final_score, "; ".join(reasons) if reasons else "Potential match"


