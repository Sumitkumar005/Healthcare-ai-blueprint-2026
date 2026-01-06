"""
CAM (Confusion Assessment Method) assessment.
"""

import logging

logger = logging.getLogger(__name__)


class CAMAssessment:
    """Performs CAM assessment for delirium."""
    
    def assess(self, assessment: dict) -> bool:
        """
        Assess for delirium using CAM criteria.
        
        CAM requires:
        1. Acute onset AND fluctuating course
        2. Inattention
        3. EITHER disorganized thinking OR altered consciousness
        
        Args:
            assessment: CAM assessment dictionary
            
        Returns:
            True if delirium positive
        """
        # Feature 1: Acute onset and fluctuating course
        feature1 = assessment.get("acute_onset", False) and assessment.get("fluctuating_course", False)
        
        # Feature 2: Inattention
        feature2 = assessment.get("inattention", False)
        
        # Feature 3: Disorganized thinking OR altered consciousness
        feature3 = assessment.get("disorganized_thinking", False) or assessment.get("altered_consciousness", False)
        
        # Delirium positive if: Feature 1 AND Feature 2 AND Feature 3
        return feature1 and feature2 and feature3

