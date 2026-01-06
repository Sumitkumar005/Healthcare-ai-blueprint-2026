"""
Prevention plan generator.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class PreventionPlanner:
    """Generates personalized prevention plans."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def generate_plan(self, assessment: Dict, score: int) -> str:
        """
        Generate personalized prevention plan.
        
        Args:
            assessment: Braden assessment data
            score: Braden score
            
        Returns:
            Prevention plan text
        """
        prompt = f"""Generate a personalized pressure ulcer prevention plan based on this Braden Scale assessment:

Braden Score: {score} (Lower = Higher Risk)

Assessment Details:
- Sensory Perception: {assessment.get('sensory_perception', 'N/A')}/4
- Moisture: {assessment.get('moisture', 'N/A')}/4
- Activity: {assessment.get('activity', 'N/A')}/4
- Mobility: {assessment.get('mobility', 'N/A')}/4
- Nutrition: {assessment.get('nutrition', 'N/A')}/4
- Friction/Shear: {assessment.get('friction_shear', 'N/A')}/3

Generate a comprehensive prevention plan including:
1. Turn schedule recommendations
2. Pressure-reducing surface recommendations
3. Skin care interventions
4. Nutritional support
5. Mobility interventions
6. Monitoring frequency

Focus on areas with low scores (higher risk)."""
        
        if self.llm_client:
            try:
                return self.llm_client.generate(prompt, max_tokens=1000, temperature=0.7)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback plan
        if score <= 12:
            return f"""
PREVENTION PLAN - HIGH RISK (Score: {score})

1. Turn Schedule: Every 2 hours
2. Pressure-Reducing Surface: High-specification foam or air mattress
3. Skin Inspection: Daily
4. Nutrition: High-protein diet, consider supplements
5. Mobility: Encourage movement, repositioning
6. Moisture Management: Keep skin dry, use moisture barriers
"""
        else:
            return f"""
PREVENTION PLAN - MODERATE/LOW RISK (Score: {score})

1. Turn Schedule: Every 4 hours
2. Standard pressure-relieving measures
3. Regular skin inspection
4. Maintain good nutrition
"""

