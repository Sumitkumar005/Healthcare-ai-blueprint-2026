"""
Drug interaction checker.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class InteractionChecker:
    """Checks for drug interactions."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
        
        # Known interactions database (simplified)
        self.known_interactions = {
            ("warfarin", "aspirin"): ("Severe", "Increased bleeding risk"),
            ("lisinopril", "spironolactone"): ("Moderate", "Risk of hyperkalemia"),
            ("metformin", "alcohol"): ("Moderate", "Increased risk of lactic acidosis"),
        }
    
    def check_all(self, medications: List[str]) -> List[Dict]:
        """
        Check all pairwise interactions.
        
        Args:
            medications: List of medication names
            
        Returns:
            List of interaction dictionaries
        """
        interactions = []
        
        # Check all pairs
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                med1 = medications[i].lower()
                med2 = medications[j].lower()
                
                interaction = self._check_pair(med1, med2)
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def _check_pair(self, med1: str, med2: str) -> Dict:
        """Check interaction between two medications."""
        # Check known interactions
        key1 = (med1, med2)
        key2 = (med2, med1)
        
        if key1 in self.known_interactions:
            severity, explanation = self.known_interactions[key1]
        elif key2 in self.known_interactions:
            severity, explanation = self.known_interactions[key2]
        else:
            # Use AI to check if not in database
            if self.llm_client:
                explanation = self._check_with_ai(med1, med2)
                if explanation and "interaction" in explanation.lower():
                    severity = "Moderate"  # Default if AI finds interaction
                else:
                    return None
            else:
                return None
        
        return {
            "medication1": med1,
            "medication2": med2,
            "severity": severity,
            "explanation": explanation
        }
    
    def _check_with_ai(self, med1: str, med2: str) -> str:
        """Check interaction using AI."""
        prompt = f"""Do {med1} and {med2} have a known drug interaction? If yes, explain the interaction and its severity (Severe, Moderate, or Minor). If no, say 'No known interaction'."""
        
        try:
            return self.llm_client.generate(prompt, max_tokens=200, temperature=0.7)
        except:
            return None

