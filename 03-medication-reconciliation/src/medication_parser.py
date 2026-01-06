"""
Medication list parser.
"""

import logging
import re
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class MedicationParser:
    """Parses medication lists into structured format."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def parse_list(self, medication_text: str) -> List[Dict[str, str]]:
        """
        Parse medication list text into structured format.
        
        Args:
            medication_text: Raw medication list text
            
        Returns:
            List of medication dictionaries
        """
        if self.llm_client:
            return self._parse_with_ai(medication_text)
        else:
            return self._parse_basic(medication_text)
    
    def _parse_with_ai(self, text: str) -> List[Dict[str, str]]:
        """Parse using AI."""
        prompt = f"""Parse the following medication list into structured format. Extract medication name, dose, frequency, and route.

Medication List:
{text}

Return as JSON array with format: [{{"name": "medication name", "dose": "dose", "frequency": "frequency", "route": "route"}}]"""
        
        try:
            response = self.llm_client.generate(prompt, max_tokens=1000)
            # Simple JSON extraction (in production, use proper JSON parsing)
            import json
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"AI parsing failed: {e}, using basic parser")
        
        return self._parse_basic(text)
    
    def _parse_basic(self, text: str) -> List[Dict[str, str]]:
        """Basic parsing without AI."""
        medications = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Basic pattern matching
            # Format: "Medication Name dose frequency"
            parts = line.split()
            if len(parts) >= 2:
                med = {
                    "name": parts[0],
                    "dose": parts[1] if len(parts) > 1 else "",
                    "frequency": " ".join(parts[2:]) if len(parts) > 2 else "daily",
                    "route": "oral"  # Default
                }
                medications.append(med)
        
        return medications
