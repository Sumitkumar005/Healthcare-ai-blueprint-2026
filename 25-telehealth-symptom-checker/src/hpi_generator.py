"""
HPI (History of Present Illness) summary generator
"""
import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class HPIGenerator:
    """Generates structured HPI summaries from questionnaire responses"""
    
    def __init__(self):
        """Initialize the HPI generator"""
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
    
    def generate_hpi(
        self,
        chief_complaint: str,
        responses: Dict,
        red_flags: List[str]
    ) -> str:
        """
        Generate a structured HPI summary
        
        Args:
            chief_complaint: Patient's chief complaint
            responses: Dictionary of question-answer pairs
            red_flags: List of detected red flag symptoms
            
        Returns:
            Formatted HPI summary string
        """
        logger.info(f"Generating HPI for chief complaint: {chief_complaint}")
        
        # Use AI if available
        if self.client:
            try:
                prompt = self._create_hpi_prompt(chief_complaint, responses, red_flags)
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a medical documentation assistant. Generate professional, structured HPI summaries in medical format."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                hpi = response.choices[0].message.content.strip()
                return hpi
            except Exception as e:
                logger.warning(f"AI HPI generation failed: {e}, using template")
        
        # Fallback to template-based generation
        return self._generate_template_hpi(chief_complaint, responses, red_flags)
    
    def _create_hpi_prompt(
        self,
        chief_complaint: str,
        responses: Dict,
        red_flags: List[str]
    ) -> str:
        """Create prompt for AI HPI generation"""
        prompt = f"""Generate a structured History of Present Illness (HPI) summary based on the following information:

Chief Complaint: {chief_complaint}

Patient Responses:
"""
        for q_id, answer in responses.items():
            prompt += f"- {q_id}: {answer}\n"
        
        if red_flags:
            prompt += f"\nRed Flags Detected: {', '.join(red_flags)}\n"
        
        prompt += """
Format the HPI as a professional medical note with the following structure:
- Chief Complaint
- History of Present Illness (onset, duration, severity, associated symptoms, aggravating/alleviating factors)
- Review of Systems (relevant to chief complaint)
- Current Medications
- Allergies
- Relevant Medical History

Keep it concise but comprehensive. Use medical terminology appropriately.
"""
        return prompt
    
    def _generate_template_hpi(
        self,
        chief_complaint: str,
        responses: Dict,
        red_flags: List[str]
    ) -> str:
        """Generate HPI using template (fallback)"""
        hpi = f"""HISTORY OF PRESENT ILLNESS

Chief Complaint: {chief_complaint}

"""
        # Extract key information from responses
        symptom_onset = responses.get("q1", "Not specified")
        severity = responses.get("q2", "Not specified")
        triggers = responses.get("q3", "Not specified")
        medications = responses.get("q4", "None reported")
        allergies = responses.get("q5", "None reported")
        history = responses.get("q6", "Not specified")
        
        hpi += f"""History of Present Illness:
The patient presents with {chief_complaint}. Symptoms began: {symptom_onset}. 
Severity: {severity}/10. Aggravating/alleviating factors: {triggers}.

Current Medications: {medications}
Allergies: {allergies}
Relevant Medical History: {history}
"""
        
        if red_flags:
            hpi += f"\n⚠️ RED FLAGS DETECTED: {', '.join(red_flags)} - Requires immediate clinical review.\n"
        
        return hpi



