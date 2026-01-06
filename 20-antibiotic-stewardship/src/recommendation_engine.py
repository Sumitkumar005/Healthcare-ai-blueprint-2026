"""
Antibiotic recommendation engine.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates antibiotic recommendations based on guidelines."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def recommend(self, request: Dict) -> Dict:
        """
        Generate antibiotic recommendation.
        
        Args:
            request: Request dictionary with infection details
            
        Returns:
            Recommendation dictionary
        """
        prompt = f"""Recommend an appropriate antibiotic based on these clinical factors:

Infection Site: {request.get('infection_site', 'N/A')}
Patient Age: {request.get('patient_age', 'N/A')} years
Severity: {request.get('severity', 'N/A')}
Renal Function: {request.get('renal_function', 'N/A')}
Allergies: {', '.join(request.get('allergies', [])) or 'None'}

Provide:
1. Recommended antibiotic (prefer narrow-spectrum when appropriate)
2. Dosing (consider renal function)
3. Duration of therapy
4. Rationale based on clinical guidelines
5. Alternative options if first choice unavailable

Follow IDSA guidelines. Prefer narrow-spectrum antibiotics when safe and appropriate."""
        
        if self.llm_client:
            try:
                response = self.llm_client.generate(prompt, max_tokens=1000, temperature=0.7)
                # Parse response (simplified)
                return {
                    "antibiotic": "See AI recommendation below",
                    "dosing": "See AI recommendation",
                    "duration": "See AI recommendation",
                    "rationale": response
                }
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback recommendations
        site = request.get('infection_site', '').lower()
        if site == 'uti':
            return {
                "antibiotic": "Nitrofurantoin 100mg twice daily",
                "dosing": "100mg PO BID",
                "duration": "5 days",
                "rationale": "Narrow-spectrum for uncomplicated UTI. Avoid if CrCl <60."
            }
        elif site == 'pneumonia':
            return {
                "antibiotic": "Amoxicillin 875mg/clavulanate 125mg twice daily",
                "dosing": "875/125mg PO BID",
                "duration": "7-10 days",
                "rationale": "Community-acquired pneumonia. Adjust for severity and risk factors."
            }
        else:
            return {
                "antibiotic": "Consult guidelines",
                "dosing": "N/A",
                "duration": "N/A",
                "rationale": "Please consult IDSA guidelines for this infection type."
            }

