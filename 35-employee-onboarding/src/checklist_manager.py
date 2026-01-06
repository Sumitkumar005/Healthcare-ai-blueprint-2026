"""
Document checklist management
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


class ChecklistManager:
    """Manages document checklists by role"""
    
    # Document requirements by role
    CLINICAL_REQUIREMENTS = [
        "license",
        "dea",
        "titer_measles",
        "titer_varicella",
        "tb_test",
        "background_check",
        "hipaa_training"
    ]
    
    NON_CLINICAL_REQUIREMENTS = [
        "background_check",
        "hipaa_training"
    ]
    
    def get_requirements_for_role(self, role: str) -> List[str]:
        """
        Get document requirements for a specific role
        
        Args:
            role: Employee role (clinical, non_clinical)
            
        Returns:
            List of required document types
        """
        role_lower = role.lower()
        
        if "clinical" in role_lower:
            return self.CLINICAL_REQUIREMENTS.copy()
        else:
            return self.NON_CLINICAL_REQUIREMENTS.copy()
    
    def validate_document_type(self, document_type: str, role: str) -> bool:
        """
        Validate if document type is required for role
        
        Args:
            document_type: Type of document
            role: Employee role
            
        Returns:
            True if document is required for this role
        """
        requirements = self.get_requirements_for_role(role)
        return document_type in requirements
    
    def get_document_display_name(self, document_type: str) -> str:
        """
        Get human-readable name for document type
        
        Args:
            document_type: Document type code
            
        Returns:
            Display name
        """
        display_names = {
            "license": "Medical License",
            "dea": "DEA Registration",
            "titer_measles": "Measles Titer",
            "titer_varicella": "Varicella Titer",
            "tb_test": "TB Test",
            "background_check": "Background Check",
            "hipaa_training": "HIPAA Training"
        }
        
        return display_names.get(document_type, document_type.replace("_", " ").title())


