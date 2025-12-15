from .model import Employee
from .db import HRManagementSystem
from .utils import sanitize_salary_input, print_employees_table
from .agent import chat_with_hr  

# Package metadata
__version__ = "1.0.0"
__all__ = ["Employee", "HRManagementSystem", "sanitize_salary_input", "print_employees_table", "chat_with_hr"]