"""
PDF generation utilities for prior authorization documents.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. PDF generation will be limited.")

logger = logging.getLogger(__name__)


def generate_pdf(prior_auth_content: Dict[str, str], patient_name: str) -> Path:
    """
    Generate PDF from prior authorization content.
    
    Args:
        prior_auth_content: Dictionary with prior auth sections
        patient_name: Patient name for filename
        
    Returns:
        Path to generated PDF file
    """
    if not REPORTLAB_AVAILABLE:
        logger.warning("ReportLab not available. Creating text file instead.")
        return _generate_text_file(prior_auth_content, patient_name)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename
    safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prior_auth_{safe_name}_{timestamp}.pdf"
    pdf_path = output_dir / filename
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#003366',
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#0066CC',
            spaceAfter=6,
        )
        normal_style = styles['Normal']
        
        # Title
        story.append(Paragraph("PRIOR AUTHORIZATION REQUEST", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("PATIENT INFORMATION", heading_style))
        story.append(Paragraph(prior_auth_content.get('patient_info', ''), normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Diagnosis
        story.append(Paragraph("DIAGNOSIS", heading_style))
        story.append(Paragraph(prior_auth_content.get('diagnosis', ''), normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Treatment Requested
        story.append(Paragraph("TREATMENT REQUESTED", heading_style))
        story.append(Paragraph(prior_auth_content.get('treatment_requested', ''), normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Medical Justification
        story.append(Paragraph("MEDICAL JUSTIFICATION", heading_style))
        justification = prior_auth_content.get('medical_justification', '')
        # Split into paragraphs
        for para in justification.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Supporting Documentation
        story.append(Paragraph("SUPPORTING DOCUMENTATION", heading_style))
        story.append(Paragraph(prior_auth_content.get('supporting_documentation', ''), normal_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF generated successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        # Fallback to text file
        return _generate_text_file(prior_auth_content, patient_name)


def _generate_text_file(prior_auth_content: Dict[str, str], patient_name: str) -> Path:
    """Generate text file as fallback."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prior_auth_{safe_name}_{timestamp}.txt"
    txt_path = output_dir / filename
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("PRIOR AUTHORIZATION REQUEST\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y')}\n\n")
        
        for section, content in prior_auth_content.items():
            f.write(f"\n{section.upper().replace('_', ' ')}\n")
            f.write("-" * 50 + "\n")
            f.write(content + "\n\n")
    
    logger.info(f"Text file generated: {txt_path}")
    return txt_path


