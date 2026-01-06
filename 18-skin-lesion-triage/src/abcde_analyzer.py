"""
ABCDE criteria analyzer for skin lesions.
"""

import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class ABCDEAnalyzer:
    """Analyzes skin lesions using ABCDE criteria."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def analyze(self, image_data: bytes) -> Dict:
        """
        Analyze lesion using ABCDE criteria.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with ABCDE scores
        """
        # In production, use vision AI to analyze each criterion
        # For now, return mock analysis
        
        return {
            "asymmetry": "Slightly asymmetric",
            "border": "Irregular",
            "color": "Multiple colors",
            "diameter": "6mm",
            "evolution": "Stable"  # Would need multiple photos over time
        }
    
    def calculate_risk_score(self, abcde_scores: Dict) -> float:
        """
        Calculate risk score based on ABCDE criteria.
        
        Args:
            abcde_scores: ABCDE assessment dictionary
            
        Returns:
            Risk score (0-10)
        """
        score = 0.0
        
        # Asymmetry (0-2 points)
        if "asymmetric" in abcde_scores.get("asymmetry", "").lower():
            score += 2.0
        elif "slightly" in abcde_scores.get("asymmetry", "").lower():
            score += 1.0
        
        # Border (0-2 points)
        if "irregular" in abcde_scores.get("border", "").lower():
            score += 2.0
        elif "slightly" in abcde_scores.get("border", "").lower():
            score += 1.0
        
        # Color (0-2 points)
        if "multiple" in abcde_scores.get("color", "").lower():
            score += 2.0
        elif "varied" in abcde_scores.get("color", "").lower():
            score += 1.0
        
        # Diameter (0-2 points)
        diameter_str = abcde_scores.get("diameter", "0mm")
        try:
            diameter = float(diameter_str.replace("mm", "").strip())
            if diameter > 6:
                score += 2.0
            elif diameter > 4:
                score += 1.0
        except:
            pass
        
        # Evolution (0-2 points)
        if "changing" in abcde_scores.get("evolution", "").lower():
            score += 2.0
        elif "growing" in abcde_scores.get("evolution", "").lower():
            score += 1.0
        
        return min(score, 10.0)

