# cli.py - CLI launcher that uses hr_app package
import sys
from hr_app.db import HRManagementSystem
from hr_app.model import Employee
from hr_app.utils import print_employees_table, sanitize_salary_input

def main_menu():
    hr = HRManagementSystem()  # instantiate system
    while True:
        print("\nHR Management System")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Search Employee")
        print("4. Update Employee")
        print("5. Delete Employee")
        print("6. Salary Report")
        print("7. Exit")
        choice = input("Select an option [1-7]: ").strip()
        try:
            if choice == "1":
                emp_id = input("Enter Employee ID: ").strip()
                name = input("Enter Name: ").strip()
                department = input("Enter Department: ").strip()
                role = input("Enter Role: ").strip()
                salary_str = input("Enter Salary: ").strip()
                try:
                    salary = sanitize_salary_input(salary_str)  # sanitize and convert
                except ValueError:
                    print("Invalid salary. Please enter a numeric value like 1200000 or 1200000.00.")
                    continue
                emp = Employee(emp_id, name, department, role, salary)
                hr.add_employee(emp)

            elif choice == "2":
                employees = hr.get_all_employees()
                print_employees_table(employees)

            elif choice == "3":
                sub = input("Search by ID or Name? [id/name]: ").strip().lower()
                if sub == "id":
                    emp_id = input("Enter Employee ID: ").strip()
                    emp = hr.find_employee_by_id(emp_id)
                    if emp:
                        print_employees_table([emp])
                    else:
                        print("Employee not found.")
                elif sub == "name":
                    name = input("Enter Name or partial name: ").strip()
                    results = hr.find_employees_by_name(name)
                    print_employees_table(results)
                else:
                    print("Invalid option. Choose 'id' or 'name'.")

            elif choice == "4":
                emp_id = input("Enter Employee ID to update: ").strip()
                emp = hr.find_employee_by_id(emp_id)
                if not emp:
                    print("Employee not found.")
                    continue
                print("Leave field blank to keep current value.")
                new_name = input(f"Name [{emp.name}]: ").strip() or None
                new_dept = input(f"Department [{emp.department}]: ").strip() or None
                new_role = input(f"Role [{emp.role}]: ").strip() or None
                new_salary_str = input(f"Salary [{emp.salary:.2f}]: ").strip() or None
                new_salary = None
                if new_salary_str is not None:
                    try:
                        new_salary = sanitize_salary_input(new_salary_str)
                    except ValueError:
                        print("Invalid salary input. Update aborted.")
                        continue
                hr.update_employee(emp_id, role=new_role, salary=new_salary, department=new_dept, name=new_name)

            elif choice == "5":
                emp_id = input("Enter Employee ID to delete: ").strip()
                confirm = input(f"Are you sure you want to delete employee {emp_id}? [y/N]: ").strip().lower()
                if confirm == "y":
                    hr.delete_employee(emp_id)
                else:
                    print("Delete cancelled.")

            elif choice == "6":
                total, dept_avgs = hr.salary_report()
                print(f"Total salary payout: {total:.2f}")
                if dept_avgs:
                    print("\nAverage salary per department:")
                    for dept, avg in dept_avgs:
                        print(f" - {dept}: {avg:.2f}")
                else:
                    print("No department data available.")

            elif choice == "7":
                print("Exiting. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please choose a number between 1 and 7.")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main_menu()
