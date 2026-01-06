"""
Nutrition screening tools - MST and MUST.
"""

import logging

logger = logging.getLogger(__name__)


class NutritionScreening:
    """Nutrition risk screening calculators."""
    
    def calculate_mst(self, weight_loss: bool, reduced_appetite: bool) -> int:
        """
        Calculate MST (Malnutrition Screening Tool) score.
        
        Args:
            weight_loss: Recent weight loss
            reduced_appetite: Reduced appetite
            
        Returns:
            Score (0-2)
        """
        score = 0
        if weight_loss:
            score += 1
        if reduced_appetite:
            score += 1
        return score
    
    def get_mst_risk(self, score: int) -> str:
        """Get MST risk level."""
        if score == 0:
            return "Low Risk"
        elif score == 1:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def get_mst_recommendation(self, score: int) -> str:
        """Get MST recommendation."""
        if score == 0:
            return "Continue routine monitoring."
        elif score == 1:
            return "Monitor closely. Consider dietitian referral if condition worsens."
        else:
            return "HIGH RISK - Immediate dietitian referral recommended."
    
    def calculate_must(self, bmi: float, weight_loss_percent: float, acute_disease: bool) -> int:
        """
        Calculate MUST (Malnutrition Universal Screening Tool) score.
        
        Args:
            bmi: Body Mass Index
            weight_loss_percent: Weight loss percentage
            acute_disease: Acute disease effect
            
        Returns:
            Score (0-6)
        """
        score = 0
        
        # BMI component
        if bmi < 18.5:
            score += 2
        elif bmi < 20:
            score += 1
        
        # Weight loss component
        if weight_loss_percent >= 10:
            score += 2
        elif weight_loss_percent >= 5:
            score += 1
        
        # Acute disease component
        if acute_disease:
            score += 2
        
        return min(score, 6)  # Cap at 6
    
    def get_must_risk(self, score: int) -> str:
        """Get MUST risk level."""
        if score == 0:
            return "Low Risk"
        elif score <= 2:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def get_must_recommendation(self, score: int) -> str:
        """Get MUST recommendation."""
        if score == 0:
            return "Low risk. Routine care."
        elif score <= 2:
            return "Medium risk. Monitor nutritional status. Consider dietitian consultation."
        else:
            return "HIGH RISK - Immediate dietitian referral and nutritional intervention required."

