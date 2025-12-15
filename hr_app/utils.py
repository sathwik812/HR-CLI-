# hr_app/utils.py - helper functions for CLI and sanitization
from typing import List
from .model import Employee

# hr_app/utils.py - helper functions for salary sanitization

def sanitize_salary_input(s: str) -> float:
    """
    Clean salary string by removing commas, currency symbols and underscores,
    then convert to float. Raises ValueError on invalid input.
    
    Examples:
        "75000" -> 75000.0
        "75,000" -> 75000.0
        "$75,000" -> 75000.0
        "₹75,000" -> 75000.0
        "75_000" -> 75000.0
    
    Args:
        s: Salary string to sanitize
        
    Returns:
        float: Cleaned salary value
        
    Raises:
        ValueError: If the input cannot be converted to a valid number
    """
    cleaned = (
        s.replace(",", "")
         .replace("_", "")
         .replace("₹", "")
         .replace("$", "")
         .replace("€", "")
         .replace("£", "")
         .strip()
    )
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(
            f"Invalid salary format: '{s}'. "
            "Please provide a numeric value (e.g., 75000 or 75,000)"
        )