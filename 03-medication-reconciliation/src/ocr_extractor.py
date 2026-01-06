"""
OCR extraction for medication lists.
"""

import logging
import io
from typing import Optional
from fastapi import UploadFile

try:
    import pytesseract
    from PIL import Image
    try:
        from pdf2image import convert_from_bytes
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class MedicationOCRExtractor:
    """Extracts text from medication list images/PDFs."""
    
    def __init__(self):
        """Initialize OCR extractor."""
        if not OCR_AVAILABLE:
            logger.warning("OCR libraries not available. Install pytesseract and Pillow.")
    
    async def extract(self, file: UploadFile) -> str:
        """
        Extract text from uploaded file.
        
        Args:
            file: Uploaded file (image or PDF)
            
        Returns:
            Extracted text
        """
        if not OCR_AVAILABLE:
            return "Mock extracted text: Lisinopril 10mg daily, Metformin 500mg twice daily"
        
        try:
            content = await file.read()
            file_extension = file.filename.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                if not PDF_AVAILABLE:
                    return "PDF processing not available. Please install pdf2image."
                images = convert_from_bytes(content)
                text = ""
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"
                return text
            else:
                # Image file
                image = Image.open(io.BytesIO(content))
                text = pytesseract.image_to_string(image)
                return text
                
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return f"Error extracting text: {str(e)}"
