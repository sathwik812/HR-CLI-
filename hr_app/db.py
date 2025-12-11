import sqlite3
from typing import List, Optional, Tuple
from .model import Employee
from .config import DB_FILE

class HRManagementSystem:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file  # path to SQLite DB
        self._create_table()    # ensure table exists on init

    def _connect(self):
        try:
            conn = sqlite3.connect(self.db_file)  # connect to SQLite DB
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def _create_table(self):
        # create employees table if not exists with salary constraint
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    emp_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    role TEXT NOT NULL,
                    salary REAL NOT NULL CHECK (salary >= 0)
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to create table: {e}")

    def add_employee(self, emp: Employee) -> bool:
        # validate and insert employee
        if not emp.emp_id.strip() or not emp.name.strip():
            print("ID and Name cannot be empty.")
            return False
        if emp.salary < 0:
            print("Salary cannot be negative.")
            return False
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO employees (emp_id, name, department, role, salary) VALUES (?, ?, ?, ?, ?)",
                emp.to_tuple()
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print("Error: Duplicate employee ID.")
            return False
        except Exception as e:
            print(f"Failed to add employee: {e}")
            return False

    def get_all_employees(self) -> List[Employee]:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees ORDER BY name")
            rows = cur.fetchall()
            conn.close()
            return [Employee(*row) for row in rows]
        except Exception as e:
            print(f"Failed to retrieve employees: {e}")
            return []

    def find_employee_by_id(self, emp_id: str) -> Optional[Employee]:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees WHERE emp_id = ?", (emp_id,))
            row = cur.fetchone()
            conn.close()
            return Employee(*row) if row else None
        except Exception as e:
            print(f"Search error: {e}")
            return None

    def find_employees_by_name(self, name: str) -> List[Employee]:
        try:
            conn = self._connect()
            cur = conn.cursor()
            pattern = f"%{name}%"
            cur.execute("SELECT emp_id, name, department, role, salary FROM employees WHERE name LIKE ? ORDER BY name", (pattern,))
            rows = cur.fetchall()
            conn.close()
            return [Employee(*row) for row in rows]
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def update_employee(self, emp_id: str, role: Optional[str] = None, salary: Optional[float] = None,
                        department: Optional[str] = None, name: Optional[str] = None) -> bool:
        if salary is not None and salary < 0:
            print("Salary cannot be negative.")
            return False
        try:
            conn = self._connect()
            cur = conn.cursor()
            fields = []
            params = []
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
            sql = f"UPDATE employees SET {', '.join(fields)} WHERE emp_id = ?"
            cur.execute(sql, tuple(params))
            conn.commit()
            updated = cur.rowcount
            conn.close()
            return bool(updated)
        except Exception as e:
            print(f"Update failed: {e}")
            return False

    def delete_employee(self, emp_id: str) -> bool:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
            conn.commit()
            deleted = cur.rowcount
            conn.close()
            return bool(deleted)
        except Exception as e:
            print(f"Delete failed: {e}")
            return False

    def salary_report(self) -> Tuple[float, List[Tuple[str, float]]]:
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("SELECT SUM(salary) FROM employees")
            total = cur.fetchone()[0] or 0.0
            cur.execute("SELECT department, AVG(salary) FROM employees GROUP BY department")
            rows = cur.fetchall()
            conn.close()
            return total, rows
        except Exception as e:
            print(f"Failed to compute salary report: {e}")
            return 0.0, []
