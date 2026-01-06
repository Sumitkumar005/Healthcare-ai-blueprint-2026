"""
Prior authorization generator using AI to create medical justification.
"""

import logging
from typing import Dict, Any
import sys
from pathlib import Path

# Add shared utilities to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from utils.api_client import get_free_llm_client

logger = logging.getLogger(__name__)


class PriorAuthGenerator:
    """
    Generates prior authorization requests with AI-powered medical justification.
    """
    
    def __init__(self):
        """Initialize the generator with LLM client."""
        try:
            self.llm_client = get_free_llm_client()
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
            self.llm_client = None
    
    def generate(self, request_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prior authorization request.
        
        Args:
            request_data: Dictionary containing patient and treatment information
            
        Returns:
            Dictionary with generated prior auth sections
        """
        try:
            # Build prompt for AI
            prompt = self._build_prompt(request_data)
            
            # Generate medical justification using AI
            if self.llm_client:
                medical_justification = self.llm_client.generate(
                    prompt,
                    max_tokens=1500,
                    temperature=0.7,
                )
            else:
                # Fallback if no LLM available
                medical_justification = self._generate_fallback_justification(request_data)
            
            # Structure the prior auth document
            prior_auth = {
                "patient_info": self._format_patient_info(request_data),
                "diagnosis": self._format_diagnosis(request_data),
                "treatment_requested": self._format_treatment(request_data),
                "medical_justification": medical_justification,
                "supporting_documentation": self._format_supporting_docs(request_data),
            }
            
            logger.info("Prior authorization generated successfully")
            return prior_auth
            
        except Exception as e:
            logger.error(f"Error generating prior auth: {str(e)}")
            raise
    
    def _build_prompt(self, request_data: Dict[str, Any]) -> str:
        """Build prompt for AI medical justification generation."""
        prompt = f"""You are a medical expert writing a prior authorization request for insurance approval.

Patient Information:
- Name: {request_data.get('patient_name', 'N/A')}
- Date of Birth: {request_data.get('patient_dob', 'N/A')}
- Diagnosis: {request_data.get('diagnosis_code', 'N/A')} - {request_data.get('diagnosis_description', 'N/A')}

Treatment Requested:
- CPT Code: {request_data.get('treatment_code', 'N/A')}
- Treatment: {request_data.get('treatment_description', 'N/A')}

Clinical Context:
{request_data.get('clinical_notes', 'N/A')}

Write a comprehensive medical justification for this prior authorization request. Include:
1. Medical necessity statement
2. Evidence-based reasoning
3. Clinical guidelines supporting the treatment
4. Expected outcomes
5. Why this specific treatment is needed

Use professional medical language and be specific. Keep it concise but comprehensive (500-800 words)."""
        
        return prompt
    
    def _generate_fallback_justification(self, request_data: Dict[str, Any]) -> str:
        """Generate basic justification without AI (fallback)."""
        return f"""MEDICAL NECESSITY STATEMENT

The requested treatment ({request_data.get('treatment_description', 'treatment')}) is medically necessary for this patient based on the following:

1. DIAGNOSIS: The patient has been diagnosed with {request_data.get('diagnosis_description', 'condition')} (ICD-10: {request_data.get('diagnosis_code', 'N/A')}).

2. CLINICAL RATIONALE: {request_data.get('clinical_notes', 'Clinical notes indicate medical necessity for this treatment.')}

3. TREATMENT INDICATION: The requested treatment (CPT: {request_data.get('treatment_code', 'N/A')}) is the appropriate intervention for this condition based on clinical guidelines.

4. EXPECTED OUTCOMES: This treatment is expected to improve patient outcomes and quality of life.

We respectfully request approval for this prior authorization."""
    
    def _format_patient_info(self, request_data: Dict[str, Any]) -> str:
        """Format patient information section."""
        return f"""PATIENT INFORMATION
Name: {request_data.get('patient_name', 'N/A')}
Date of Birth: {request_data.get('patient_dob', 'N/A')}
Patient ID: {request_data.get('patient_id', 'N/A')}
Insurance: {request_data.get('insurance_name', 'N/A')}
Policy Number: {request_data.get('policy_number', 'N/A')}"""
    
    def _format_diagnosis(self, request_data: Dict[str, Any]) -> str:
        """Format diagnosis section."""
        return f"""DIAGNOSIS
ICD-10 Code: {request_data.get('diagnosis_code', 'N/A')}
Description: {request_data.get('diagnosis_description', 'N/A')}"""
    
    def _format_treatment(self, request_data: Dict[str, Any]) -> str:
        """Format treatment requested section."""
        return f"""TREATMENT REQUESTED
CPT Code: {request_data.get('treatment_code', 'N/A')}
Description: {request_data.get('treatment_description', 'N/A')}
Provider: {request_data.get('provider_name', 'N/A')}
Provider NPI: {request_data.get('provider_npi', 'N/A')}"""
    
    def _format_supporting_docs(self, request_data: Dict[str, Any]) -> str:
        """Format supporting documentation section."""
        return """SUPPORTING DOCUMENTATION
- Clinical notes and assessment
- Diagnostic test results (if applicable)
- Treatment history
- Provider notes and recommendations"""


