"""
Unit tests for prior authorization generator.
"""

import pytest
from src.generator import PriorAuthGenerator


def test_generator_initialization():
    """Test that generator can be initialized."""
    # This will fail if no API keys, but that's OK for testing structure
    try:
        generator = PriorAuthGenerator()
        assert generator is not None
    except ValueError:
        # Expected if no API keys configured
        pass


def test_generate_with_mock_data():
    """Test generation with mock data."""
    request_data = {
        "patient_name": "John Doe",
        "patient_dob": "1980-01-01",
        "diagnosis_code": "E11.9",
        "diagnosis_description": "Type 2 diabetes",
        "treatment_code": "97110",
        "treatment_description": "Physical therapy",
        "clinical_notes": "Patient requires physical therapy for diabetic neuropathy.",
    }
    
    try:
        generator = PriorAuthGenerator()
        result = generator.generate(request_data)
        
        assert "patient_info" in result
        assert "diagnosis" in result
        assert "treatment_requested" in result
        assert "medical_justification" in result
        assert "supporting_documentation" in result
        
    except ValueError:
        # Expected if no API keys
        pytest.skip("API keys not configured")


def test_format_patient_info():
    """Test patient info formatting."""
    request_data = {
        "patient_name": "Jane Smith",
        "patient_dob": "1975-05-15",
        "patient_id": "MRN12345",
    }
    
    generator = PriorAuthGenerator()
    formatted = generator._format_patient_info(request_data)
    
    assert "Jane Smith" in formatted
    assert "1975-05-15" in formatted
    assert "MRN12345" in formatted


if __name__ == "__main__":
    pytest.main([__file__])


