"""
Wound description generator.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """Generates standardized wound descriptions."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def generate(self, wound_type: str, size: Optional[str]) -> str:
        """
        Generate standardized SOAP-style wound description.
        
        Args:
            wound_type: Classified wound type
            size: Size measurement if available
            
        Returns:
            Standardized description
        """
        prompt = f"""Generate a standardized SOAP-style wound description:

Wound Type: {wound_type}
Size: {size or 'Not measured'}

Include:
- Location
- Size and dimensions
- Appearance (color, drainage, edges)
- Surrounding skin condition
- Stage/classification if applicable

Use professional medical terminology."""
        
        if self.llm_client:
            try:
                return self.llm_client.generate(prompt, max_tokens=500, temperature=0.7)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback
        return f"""
WOUND DESCRIPTION

Type: {wound_type}
Size: {size or 'Not measured'}
Appearance: [Describe based on wound type]
Surrounding Skin: [Assess condition]
Stage: [If applicable]

NOTE: This is a template. For full AI-powered description, configure vision AI API keys.
"""

