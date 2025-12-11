# hr_app/model.py - Employee dataclass
from dataclasses import dataclass

@dataclass
class Employee:
    emp_id: str    # unique employee ID
    name: str      # employee name
    department: str
    role: str
    salary: float

    def to_tuple(self):
        # tuple representation for DB insertion
        return (self.emp_id, self.name, self.department, self.role, self.salary)
