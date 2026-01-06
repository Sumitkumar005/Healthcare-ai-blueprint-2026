"""
Medication reconciliation engine.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))
from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class ReconciliationEngine:
    """Reconciles home and hospital medications."""
    
    def __init__(self):
        try:
            self.llm_client = get_free_llm_client()
        except:
            self.llm_client = None
    
    def reconcile(self, home_meds: List[Dict], hospital_meds: List[Dict]) -> Dict:
        """
        Reconcile medication lists.
        
        Args:
            home_meds: List of home medications
            hospital_meds: List of hospital medications
            
        Returns:
            Dictionary with continue, discontinue, start_new lists
        """
        if self.llm_client:
            return self._reconcile_with_ai(home_meds, hospital_meds)
        else:
            return self._reconcile_basic(home_meds, hospital_meds)
    
    def _reconcile_with_ai(self, home_meds: List[Dict], hospital_meds: List[Dict]) -> Dict:
        """Reconcile using AI."""
        prompt = f"""Reconcile these medication lists:

Home Medications:
{self._format_meds(home_meds)}

Hospital Discharge Medications:
{self._format_meds(hospital_meds)}

Categorize each medication as:
1. CONTINUE - Same medication, continue as prescribed
2. DISCONTINUE - Home medication not in discharge list
3. START NEW - New medication in discharge list

Return JSON: {{"continue": [...], "discontinue": [...], "start_new": [...]}}"""
        
        try:
            response = self.llm_client.generate(prompt, max_tokens=1000)
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"AI reconciliation failed: {e}")
        
        return self._reconcile_basic(home_meds, hospital_meds)
    
    def _reconcile_basic(self, home_meds: List[Dict], hospital_meds: List[Dict]) -> Dict:
        """Basic reconciliation logic."""
        home_names = {med.get('name', '').lower() for med in home_meds}
        hospital_names = {med.get('name', '').lower() for med in hospital_meds}
        
        continue_list = []
        discontinue_list = []
        start_new_list = []
        
        # Find medications to continue (in both lists)
        for med in hospital_meds:
            med_name = med.get('name', '').lower()
            if med_name in home_names:
                continue_list.append(f"{med.get('name', 'Unknown')} {med.get('dose', '')} {med.get('frequency', '')}")
            else:
                start_new_list.append(f"{med.get('name', 'Unknown')} {med.get('dose', '')} {med.get('frequency', '')}")
        
        # Find medications to discontinue (in home but not hospital)
        for med in home_meds:
            med_name = med.get('name', '').lower()
            if med_name not in hospital_names:
                discontinue_list.append(f"{med.get('name', 'Unknown')} {med.get('dose', '')} {med.get('frequency', '')}")
        
        return {
            "continue": continue_list,
            "discontinue": discontinue_list,
            "start_new": start_new_list
        }
    
    def _format_meds(self, meds: List[Dict]) -> str:
        """Format medications for display."""
        return "\n".join([f"- {m.get('name', 'Unknown')} {m.get('dose', '')} {m.get('frequency', '')}" for m in meds])
    
    def check_interactions(self, medications: List[str]) -> List[str]:
        """
        Check for drug interactions.
        
        Args:
            medications: List of medication strings
            
        Returns:
            List of interaction warnings
        """
        # Basic interaction checking (in production, use drug database)
        warnings = []
        
        # Example: Check for common interactions
        med_names = [m.lower() for m in medications]
        
        if 'warfarin' in ' '.join(med_names) and 'aspirin' in ' '.join(med_names):
            warnings.append("Warfarin + Aspirin: Increased bleeding risk - monitor closely")
        
        if 'lisinopril' in ' '.join(med_names) and 'spironolactone' in ' '.join(med_names):
            warnings.append("Lisinopril + Spironolactone: Risk of hyperkalemia - monitor potassium")
        
        return warnings
