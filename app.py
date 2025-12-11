# streamlit_app.py - Streamlit launcher using hr_app package
import streamlit as st
from hr_app.db import HRManagementSystem
from hr_app.model import Employee
from hr_app.utils import sanitize_salary_input

hr = HRManagementSystem()  # shared DB access

def main():
    st.title("HR Management System")
    menu = ["Add Employee", "View Employees", "Search", "Update", "Delete", "Salary Report"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Employee":
        st.header("Add Employee")
        with st.form("add_form"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            department = st.text_input("Department")
            role = st.text_input("Role")
            salary = st.text_input("Salary")
            submitted = st.form_submit_button("Add")
            if submitted:
                try:
                    salary_val = sanitize_salary_input(salary)
                except Exception:
                    st.warning("Enter a numeric salary like 1200000 or 1,200,000 (commas allowed).")
                    salary_val = None
                if salary_val is not None:
                    emp = Employee(emp_id=emp_id.strip(), name=name.strip(), department=department.strip(), role=role.strip(), salary=salary_val)
                    if hr.add_employee(emp):
                        st.success("Employee added.")
                    else:
                        st.error("Failed to add employee. Check console for details.")

    elif choice == "View Employees":
        st.header("All Employees")
        employees = hr.get_all_employees()
        if employees:
            data = [[e.emp_id, e.name, e.department, e.role, f"{e.salary:.2f}"] for e in employees]
            st.table(data)
        else:
            st.info("No employees found.")

    elif choice == "Search":
        st.header("Search Employee")
        search_by = st.radio("Search by", ("ID", "Name"))
        if search_by == "ID":
            emp_id = st.text_input("Employee ID")
            if st.button("Search by ID"):
                emp = hr.find_employee_by_id(emp_id.strip())
                if emp:
                    st.write({"ID": emp.emp_id, "Name": emp.name, "Department": emp.department, "Role": emp.role, "Salary": f"{emp.salary:.2f}"})
                else:
                    st.info("Employee not found.")
        else:
            name = st.text_input("Name or partial name")
            if st.button("Search by Name"):
                results = hr.find_employees_by_name(name.strip())
                if results:
                    data = [[e.emp_id, e.name, e.department, e.role, f"{e.salary:.2f}"] for e in results]
                    st.table(data)
                else:
                    st.info("No matches found.")

    elif choice == "Update":
        st.header("Update Employee")
        emp_id = st.text_input("Employee ID to update")
        if st.button("Load Employee"):
            emp = hr.find_employee_by_id(emp_id.strip())
            if emp:
                st.session_state["loaded_emp"] = emp
            else:
                st.info("Employee not found.")
        if "loaded_emp" in st.session_state:
            emp = st.session_state["loaded_emp"]
            with st.form("update_form"):
                name = st.text_input("Name", value=emp.name)
                department = st.text_input("Department", value=emp.department)
                role = st.text_input("Role", value=emp.role)
                salary = st.text_input("Salary", value=f"{emp.salary:.2f}")
                submitted = st.form_submit_button("Update")
                if submitted:
                    try:
                        salary_val = sanitize_salary_input(salary)
                    except Exception:
                        st.warning("Enter a numeric salary.")
                        salary_val = None
                    if salary_val is not None:
                        if hr.update_employee(emp.emp_id, name=name.strip(), department=department.strip(), role=role.strip(), salary=salary_val):
                            st.success("Employee updated.")
                        else:
                            st.error("Update failed.")
                        del st.session_state["loaded_emp"]

    elif choice == "Delete":
        st.header("Delete Employee")
        emp_id = st.text_input("Employee ID to delete")
        if st.button("Delete"):
            if emp_id.strip():
                if hr.delete_employee(emp_id.strip()):
                    st.success("Employee deleted.")
                else:
                    st.warning("Employee not found.")
            else:
                st.warning("Enter an Employee ID.")

    elif choice == "Salary Report":
        st.header("Salary Report")
        total, dept_avgs = hr.salary_report()
        st.write(f"**Total salary payout:** {total:.2f}")
        if dept_avgs:
            st.write("**Average salary per department**")
            for dept, avg in dept_avgs:
                st.write(f"- {dept}: {avg:.2f}")
        else:
            st.info("No department data available.")

if __name__ == "__main__":
    main()


