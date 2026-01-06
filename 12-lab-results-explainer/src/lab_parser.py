"""
Lab results parser.
"""

import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class LabParser:
    """Parses lab results text."""
    
    def parse(self, text: str) -> List[Dict]:
        """
        Parse lab results text.
        
        Args:
            text: Lab results text
            
        Returns:
            List of lab result dictionaries
        """
        results = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Basic pattern: "Test Name: Value (Reference Range)"
            match = re.match(r'(.+?):\s*([\d.]+)\s*\(([^)]+)\)', line)
            if match:
                test_name = match.group(1).strip()
                value = float(match.group(2))
                reference = match.group(3).strip()
                
                results.append({
                    "test_name": test_name,
                    "value": value,
                    "reference_range": reference,
                    "status": self._determine_status(value, reference)
                })
        
        return results
    
    def _determine_status(self, value: float, reference: str) -> str:
        """Determine if value is normal, high, or low."""
        # Simple parsing of reference range
        if '-' in reference:
            parts = reference.split('-')
            try:
                low = float(parts[0])
                high = float(parts[1])
                if value < low:
                    return "low"
                elif value > high:
                    return "high"
                else:
                    return "normal"
            except:
                return "unknown"
        return "unknown"

