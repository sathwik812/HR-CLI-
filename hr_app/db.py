
# hr_app/db.py
import sqlite3  # For SQLite database operations
from typing import List, Optional, Tuple  # For type hints
from .model import Employee  # Import Employee model
from .config import DB_FILE  # Import database file path

class HRManagementSystem:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file  # Store database file path
        self._create_table()  # Ensure table exists on init
    
    def _connect(self):
        try:
            conn = sqlite3.connect(self.db_file)  # Connect to SQLite DB
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def _create_table(self):
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    emp_id TEXT PRIMARY KEY,  # Employee ID as primary key
                    name TEXT NOT NULL,  # Employee name
                    department TEXT NOT NULL,  # Department
                    role TEXT NOT NULL,  # Role
                    salary REAL NOT NULL CHECK (salary >= 0)  # Salary, must be non-negative
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to create table: {e}")
    
    def add_employee(self, emp: Employee) -> Tuple[bool, str]:
        """Add employee with Pydantic validation"""
        try:
            # Employee is already validated by Pydantic
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO employees (emp_id, name, department, role, salary) VALUES (?, ?, ?, ?, ?)",
                emp.to_tuple()  # Insert employee data
            )
            conn.commit()
            conn.close()
            return True, "Employee added successfully."
        except sqlite3.IntegrityError:
            return False, "Employee ID already exists."
        except Exception as e:
            return False, f"Failed to add employee: {str(e)}"
    
    def get_all_employees(self) -> List[Employee]:
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees ORDER BY name")  # Query all employees
            rows = cur.fetchall()
            conn.close()
            # Convert rows to Employee objects
            employees = []
            for row in rows:
                try:
                    employee = Employee(
                        emp_id=row[0],
                        name=row[1],
                        department=row[2],
                        role=row[3],
                        salary=row[4]
                    )
                    employees.append(employee)
                except Exception as e:
                    print(f"Error creating Employee from row {row}: {e}")
                    continue
            return employees  # Return list of Employee objects
        except Exception as e:
            print(f"Failed to retrieve employees: {e}")
            return []
    
    def find_employee_by_id(self, emp_id: str) -> Optional[Employee]:
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees WHERE emp_id = ?", (emp_id,))  # Query by ID
            row = cur.fetchone()
            conn.close()
            if row:
                return Employee(
                    emp_id=row[0],
                    name=row[1],
                    department=row[2],
                    role=row[3],
                    salary=row[4]
                )  # Return Employee object if found
            return None  # Not found
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    # Other methods remain the same...
    def find_employees_by_name(self, name: str) -> List[Employee]:
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            pattern = f"%{name}%"  # SQL LIKE pattern
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees WHERE name LIKE ? ORDER BY name", (pattern,))
            rows = cur.fetchall()
            conn.close()
            employees = []
            for row in rows:
                try:
                    employee = Employee(
                        emp_id=row[0],
                        name=row[1],
                        department=row[2],
                        role=row[3],
                        salary=row[4]
                    )
                    employees.append(employee)
                except Exception as e:
                    print(f"Error creating Employee from row {row}: {e}")
                    continue
            return employees  # Return list of matching employees
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def update_employee(self, emp_id: str, role: Optional[str] = None, salary: Optional[float] = None,
                        department: Optional[str] = None, name: Optional[str] = None) -> bool:
        if salary is not None and salary < 0:
            print("Salary cannot be negative.")
            return False
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            fields = []  # Fields to update
            params = []  # Parameters for SQL
            if name is not None:
                fields.append("name = ?"); params.append(name)
            if department is not None:
                fields.append("department = ?"); params.append(department)
            if role is not None:
                fields.append("role = ?"); params.append(role)
            if salary is not None:
                fields.append("salary = ?"); params.append(salary)
            if not fields:
                print("No updates provided.")
                conn.close()
                return False
            params.append(emp_id)
            sql = f"UPDATE employees SET {', '.join(fields)} WHERE emp_id = ?"  # Build SQL
            cur.execute(sql, tuple(params))  # Execute update
            conn.commit()
            updated = cur.rowcount  # Number of rows updated
            conn.close()
            return bool(updated)
        except Exception as e:
            print(f"Update failed: {e}")
            return False
    
    def delete_employee(self, emp_id: str) -> bool:
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            cur.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))  # Delete by ID
            conn.commit()
            deleted = cur.rowcount  # Number of rows deleted
            conn.close()
            return bool(deleted)
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    
    def salary_report(self) -> Tuple[float, List[Tuple[str, float]]]:
        try:
            conn = self._connect()  # Connect to DB
            cur = conn.cursor()
            cur.execute("SELECT SUM(salary) FROM employees")  # Total salary payout
            total = cur.fetchone()[0] or 0.0
            cur.execute("SELECT department, AVG(salary) FROM employees GROUP BY department")  # Avg salary by dept
            rows = cur.fetchall()
            conn.close()
            return total, rows  # Return total and department averages
        except Exception as e:
            print(f"Failed to compute salary report: {e}")
            return 0.0, []