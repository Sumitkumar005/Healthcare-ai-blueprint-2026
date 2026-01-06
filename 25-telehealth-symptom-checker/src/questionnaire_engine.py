"""
Adaptive questionnaire engine for pre-visit symptom collection
"""
import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class QuestionnaireEngine:
    """Handles adaptive questioning based on chief complaint"""
    
    def __init__(self):
        """Initialize the questionnaire engine"""
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.client = None
        
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
        
        # Store session state
        self.sessions: Dict[str, Dict] = {}
        
        # Red flag keywords
        self.red_flags = [
            "chest pain", "shortness of breath", "severe headache",
            "loss of consciousness", "severe abdominal pain",
            "difficulty breathing", "severe dizziness", "severe weakness",
            "suicidal", "suicide", "severe bleeding", "stroke symptoms"
        ]
    
    def start_questionnaire(
        self,
        session_id: str,
        chief_complaint: str
    ) -> Dict:
        """
        Start a new questionnaire session
        
        Args:
            session_id: Unique session identifier
            chief_complaint: Patient's chief complaint
            
        Returns:
            Dictionary with first question and question_id
        """
        logger.info(f"Starting questionnaire for session {session_id}")
        
        # Initialize session
        self.sessions[session_id] = {
            "chief_complaint": chief_complaint,
            "responses": {},
            "current_question_index": 0,
            "questions_asked": []
        }
        
        # Generate first question based on chief complaint
        first_question = self._generate_adaptive_question(
            chief_complaint=chief_complaint,
            previous_responses={},
            question_number=1
        )
        
        question_id = "q1"
        self.sessions[session_id]["questions_asked"].append(question_id)
        
        return {
            "question": first_question,
            "question_id": question_id
        }
    
    def process_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str,
        chief_complaint: str
    ) -> Dict:
        """
        Process an answer and generate next question
        
        Args:
            session_id: Session identifier
            question_id: ID of the question being answered
            answer: Patient's answer
            chief_complaint: Chief complaint for context
            
        Returns:
            Dictionary with next question or completion status
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session["responses"][question_id] = answer
        
        # Check for red flags
        red_flags = self._detect_red_flags(answer)
        
        # Determine if we should continue or complete
        question_count = len(session["questions_asked"])
        
        # Standard questions to ask
        standard_questions = [
            "When did the symptoms start?",
            "How would you rate the severity on a scale of 1-10?",
            "What makes the symptoms better or worse?",
            "Are you currently taking any medications?",
            "Do you have any known allergies?",
            "Any relevant medical history for this condition?"
        ]
        
        # If we've asked enough questions, complete
        if question_count >= 6:
            return {
                "is_complete": True,
                "question": None,
                "question_id": None,
                "red_flags": red_flags
            }
        
        # Generate next adaptive question
        next_question = self._generate_adaptive_question(
            chief_complaint=chief_complaint,
            previous_responses=session["responses"],
            question_number=question_count + 1
        )
        
        next_question_id = f"q{question_count + 1}"
        session["questions_asked"].append(next_question_id)
        
        return {
            "is_complete": False,
            "question": next_question,
            "question_id": next_question_id,
            "red_flags": red_flags
        }
    
    def _generate_adaptive_question(
        self,
        chief_complaint: str,
        previous_responses: Dict,
        question_number: int
    ) -> str:
        """
        Generate an adaptive question based on chief complaint and previous answers
        
        Args:
            chief_complaint: Patient's chief complaint
            previous_responses: Dictionary of previous Q&A
            question_number: Current question number
            
        Returns:
            Generated question string
        """
        # Standard questions for first few
        if question_number == 1:
            return f"Tell me more about your {chief_complaint}. When did it start?"
        
        if question_number == 2:
            return "On a scale of 1 to 10, how severe are your symptoms?"
        
        if question_number == 3:
            return "What makes your symptoms better or worse? Any triggers?"
        
        if question_number == 4:
            return "Are you currently taking any medications? Please list them."
        
        if question_number == 5:
            return "Do you have any known allergies to medications or other substances?"
        
        if question_number == 6:
            return "Is there any relevant medical history related to this condition?"
        
        # Use AI for adaptive follow-up if available
        if self.client and len(previous_responses) > 0:
            try:
                prompt = f"""Based on the patient's chief complaint "{chief_complaint}" and their previous answers:
{self._format_responses(previous_responses)}

Generate a relevant follow-up question (question #{question_number}) to gather more information about their condition. Keep it concise and medical.

Question:"""
                
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a medical assistant helping gather patient history."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                
                question = response.choices[0].message.content.strip()
                return question
            except Exception as e:
                logger.warning(f"AI question generation failed: {e}")
        
        # Fallback to generic question
        return "Is there anything else you'd like to tell me about your symptoms?"
    
    def _format_responses(self, responses: Dict) -> str:
        """Format responses for AI prompt"""
        formatted = []
        for q_id, answer in responses.items():
            formatted.append(f"Q: {q_id}\nA: {answer}")
        return "\n\n".join(formatted)
    
    def _detect_red_flags(self, text: str) -> List[str]:
        """
        Detect red flag symptoms in patient response
        
        Args:
            text: Patient's response text
            
        Returns:
            List of detected red flags
        """
        text_lower = text.lower()
        detected = []
        
        for flag in self.red_flags:
            if flag in text_lower:
                detected.append(flag)
        
        return detected




