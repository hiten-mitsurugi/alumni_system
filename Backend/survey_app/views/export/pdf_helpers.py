"""
PDF Export Helper Functions
============================
Shared utilities for PDF generation across different export types.
"""

import json


def extract_value_for_pdf(response_data):
    """
    Helper function to extract value from response_data for PDF export.
    
    Args:
        response_data: Response data in various formats (dict, list, string, etc.)
        
    Returns:
        Extracted value or None
    """
    if not response_data:
        return None
    if isinstance(response_data, dict):
        for key in ['value', 'answer', 'text', 'rating', 'selected_options']:
            if key in response_data:
                return response_data[key]
        return response_data
    return response_data
