"""
Intervention planner for delirium.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class InterventionPlanner:
    """Generates intervention recommendations for delirium."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def generate_interventions(self, assessment: Dict, is_positive: bool) -> str:
        """
        Generate intervention recommendations.
        
        Args:
            assessment: CAM assessment data
            is_positive: Whether delirium is positive
            
        Returns:
            Intervention recommendations
        """
        if not is_positive:
            return "No delirium detected. Continue routine monitoring."
        
        prompt = f"""Generate intervention recommendations for a patient with positive CAM delirium assessment.

Assessment Details:
- Acute onset and fluctuating course: Yes
- Inattention: {'Yes' if assessment.get('inattention') else 'No'}
- Disorganized thinking: {'Yes' if assessment.get('disorganized_thinking') else 'No'}
- Altered consciousness: {'Yes' if assessment.get('altered_consciousness') else 'No'}

Provide recommendations for:
1. Non-pharmacologic interventions
2. Medication review
3. Environmental modifications
4. Monitoring frequency
5. When to alert provider"""
        
        if self.llm_client:
            try:
                return self.llm_client.generate(prompt, max_tokens=800, temperature=0.7)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback
        return """
DELIRIUM INTERVENTIONS:

1. Non-pharmacologic:
   - Reorient frequently
   - Ensure adequate lighting
   - Minimize noise
   - Encourage family presence
   - Maintain sleep-wake cycle

2. Medication Review:
   - Review all medications for delirium-causing agents
   - Consider reducing or discontinuing anticholinergics, benzodiazepines

3. Environmental:
   - Keep familiar objects nearby
   - Maintain consistent routine
   - Ensure hearing aids/glasses are available

4. Monitoring:
   - Assess every shift
   - Document mental status changes
   - Alert provider immediately

5. Safety:
   - Consider sitter if high risk for falls
   - Ensure call bell is accessible
"""

