# hr_app/utils.py - helper functions for CLI and sanitization
from typing import List
from .model import Employee

def sanitize_salary_input(s: str) -> float:
    """
    Clean salary string by removing commas, currency symbols and underscores,
    then convert to float. Raises ValueError on invalid input.
    """
    cleaned = s.replace(",", "").replace("_", "").replace("₹", "").replace("$", "").strip()
    return float(cleaned)

def print_employees_table(employees: List[Employee]):
    # simple formatted table for CLI
    if not employees:
        print("No employees found.")
        return
    headers = ["ID", "Name", "Department", "Role", "Salary"]
    cols = [
        [e.emp_id for e in employees],
        [e.name for e in employees],
        [e.department for e in employees],
        [e.role for e in employees],
        [f"{e.salary:.2f}" for e in employees]
    ]
    widths = [max(len(h), max((len(x) for x in col), default=0)) for h, col in zip(headers, cols)]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    sep_line = "-+-".join("-" * w for w in widths)
    print(header_line)
    print(sep_line)
    for e in employees:
        row = " | ".join([
            e.emp_id.ljust(widths[0]),
            e.name.ljust(widths[1]),
            e.department.ljust(widths[2]),
            e.role.ljust(widths[3]),
            f"{e.salary:.2f}".rjust(widths[4])
        ])
        print(row)
