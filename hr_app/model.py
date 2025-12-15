# hr_app/model.py - Employee model using Pydantic
from pydantic import BaseModel, Field, field_validator
from typing import Tuple

class Employee(BaseModel):
    """Employee model with validation using Pydantic"""
    emp_id: str = Field(..., description="Unique employee ID", min_length=1)
    name: str = Field(..., description="Employee full name", min_length=1)
    department: str = Field(..., description="Department name", min_length=1)
    role: str = Field(..., description="Job role/title", min_length=1)
    salary: float = Field(..., description="Annual salary", ge=0)
    
    @field_validator('emp_id', 'name', 'department', 'role')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v: float) -> float:
        """Validate salary is non-negative"""
        if v < 0:
            raise ValueError("Salary cannot be negative")
        return round(v, 2)
    
    def to_tuple(self) -> Tuple:
        """Convert to tuple for SQLite insertion"""
        return (self.emp_id, self.name, self.department, self.role, self.salary)
    
    @classmethod
    def from_tuple(cls, data: Tuple) -> 'Employee':
        """Create Employee instance from tuple"""
        return cls(
            emp_id=data[0],
            name=data[1],
            department=data[2],
            role=data[3],
            salary=data[4]
        )