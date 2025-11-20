"""
Survey App Utility Functions
============================
Shared helper functions used across different view modules.
"""


def extract_value(response_data):
    """
    Extract the actual value from response_data JSON.
    
    Args:
        response_data: Can be dict, list, or primitive type
        
    Returns:
        The extracted value or None
    """
    # Handle boolean False explicitly (it's a valid value, not empty)
    if response_data is None:
        return None
    
    if isinstance(response_data, dict):
        # Try common keys
        for key in ['value', 'answer', 'text', 'rating', 'selected_options']:
            if key in response_data:
                return response_data[key]
        return response_data
    
    return response_data


def extract_value_for_pdf(response_data):
    """
    Helper function to extract value from response_data for PDF generation.
    
    Args:
        response_data: Can be dict, list, or primitive type
        
    Returns:
        The extracted value or None
    """
    # Handle boolean False explicitly (it's a valid value, not empty)
    if response_data is None:
        return None
        
    if isinstance(response_data, dict):
        for key in ['value', 'answer', 'text', 'rating', 'selected_options']:
            if key in response_data:
                return response_data[key]
        return response_data
        
    return response_data
