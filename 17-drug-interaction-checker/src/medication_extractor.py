"""
Medication extraction from photos (reuses OCR from project 03).
"""

import logging

logger = logging.getLogger(__name__)


class MedicationExtractor:
    """Extracts medications from photos using OCR."""
    
    def extract_from_image(self, image_data: bytes) -> list:
        """Extract medications from image."""
        # Reuse OCR logic from project 03
        # For now, return mock data
        return ["Lisinopril", "Metformin", "Aspirin"]

