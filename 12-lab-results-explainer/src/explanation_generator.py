"""
Lab results explanation generator.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Generates plain-language explanations of lab results."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def generate(self, lab_results: List[Dict]) -> str:
        """
        Generate explanation for lab results.
        
        Args:
            lab_results: Parsed lab results
            
        Returns:
            Plain-language explanation
        """
        prompt = f"""Explain these lab results in plain language for a patient:

{self._format_results(lab_results)}

For each result:
1. Explain what the test measures
2. Explain what the value means in simple terms
3. If abnormal, provide context (e.g., "slightly elevated is common and manageable")
4. Suggest questions to ask the doctor

Use clear, non-technical language. Be reassuring but accurate."""
        
        if self.llm_client:
            try:
                return self.llm_client.generate(prompt, max_tokens=1500, temperature=0.7)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # Fallback
        explanation = "LAB RESULTS EXPLANATION\n\n"
        for result in lab_results:
            explanation += f"{result['test_name']}: {result['value']}\n"
            explanation += f"Reference Range: {result['reference_range']}\n"
            explanation += f"Status: {result['status'].upper()}\n\n"
        explanation += "\nNOTE: This is a basic explanation. For detailed AI-powered explanations, configure API keys."
        return explanation
    
    def _format_results(self, results: List[Dict]) -> str:
        """Format results for prompt."""
        formatted = []
        for r in results:
            formatted.append(f"{r['test_name']}: {r['value']} (Reference: {r['reference_range']}, Status: {r['status']})")
        return "\n".join(formatted)

