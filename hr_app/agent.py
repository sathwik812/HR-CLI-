# hr_app/agent.py - UPDATED FOR LANGCHAIN 1.1+
import os
from typing import Optional, Annotated

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from .db import HRManagementSystem
from .model import Employee
from .utils import sanitize_salary_input

# Initialize HR system
hr_system = HRManagementSystem()

# --- Define Tools using proper @tool decorator ---

@tool
def add_employee(
    emp_id: Annotated[str, "Employee ID"],
    name: Annotated[str, "Employee full name"],
    department: Annotated[str, "Department name"],
    role: Annotated[str, "Job role/title"],
    salary: Annotated[str, "Annual salary (can include commas or currency symbols)"]
) -> str:
    """Add a new employee to the HR database.
    
    Use this tool when the user wants to create or add a new employee record.
    All fields are required: emp_id, name, department, role, and salary.
    """
    try:
        salary_val = sanitize_salary_input(salary)
        emp = Employee(
            emp_id=emp_id.strip(),
            name=name.strip(),
            department=department.strip(),
            role=role.strip(),
            salary=salary_val
        )
        ok, msg = hr_system.add_employee(emp)
        return msg
    except ValueError as e:
        return f"Error: Invalid salary format - {str(e)}"
    except Exception as e:
        return f"Error creating employee: {str(e)}"


@tool
def view_all_employees() -> str:
    """Retrieve and list all employees in the system.
    
    Use this tool when the user wants to see all employees, list employees,
    or get an overview of the workforce.
    """
    employees = hr_system.get_all_employees()
    if not employees:
        return "The employee database is currently empty."
    
    lines = ["### Current Employees:"]
    for e in employees:
        lines.append(
            f"- **{e.emp_id}**: {e.name}, {e.department}, {e.role}, "
            f"Salary: ${e.salary:,.2f}"
        )
    return "\n".join(lines)


@tool
def search_employee(
    search_by: Annotated[str, "Search type: 'id' or 'name'"],
    query: Annotated[str, "The ID or name to search for"]
) -> str:
    """Search for an employee by ID or name.
    
    Use this tool when the user wants to find or look up a specific employee.
    search_by must be either 'id' (to search by employee ID) or 'name' 
    (to search by employee name).
    """
    if search_by.lower() == "id":
        emp = hr_system.find_employee_by_id(query.strip())
        if emp:
            return (
                f"**Found Employee**:\n"
                f"- **ID**: {emp.emp_id}\n"
                f"- **Name**: {emp.name}\n"
                f"- **Department**: {emp.department}\n"
                f"- **Role**: {emp.role}\n"
                f"- **Salary**: ${emp.salary:,.2f}"
            )
        return f"No employee found with ID: {query}"
    
    elif search_by.lower() == "name":
        results = hr_system.find_employees_by_name(query.strip())
        if results:
            lines = [f"Found {len(results)} employee(s):"]
            for e in results:
                lines.append(
                    f"- **{e.emp_id}**: {e.name} ({e.department}, {e.role})"
                )
            return "\n".join(lines)
        return f"No employees found with name containing: {query}"
    
    return "Error: search_by must be 'id' or 'name'."


@tool
def update_employee(
    emp_id: Annotated[str, "Employee ID to update"],
    name: Annotated[Optional[str], "New name (optional)"] = None,
    department: Annotated[Optional[str], "New department (optional)"] = None,
    role: Annotated[Optional[str], "New role (optional)"] = None,
    salary: Annotated[Optional[str], "New salary (optional)"] = None
) -> str:
    """Update an employee's details.
    
    Use this tool when the user wants to modify or change an employee's information.
    Provide the emp_id and at least one field to update.
    """
    # Check if employee exists
    existing = hr_system.find_employee_by_id(emp_id.strip())
    if not existing:
        return f"Error: No employee found with ID {emp_id}"
    
    # Process salary if provided
    salary_val = None
    if salary is not None:
        try:
            salary_val = sanitize_salary_input(salary)
        except ValueError:
            return "Error: Invalid salary format."
    
    # Prepare update parameters
    update_kwargs = {}
    if name is not None:
        update_kwargs['name'] = name.strip()
    if department is not None:
        update_kwargs['department'] = department.strip()
    if role is not None:
        update_kwargs['role'] = role.strip()
    if salary_val is not None:
        update_kwargs['salary'] = salary_val
    
    if not update_kwargs:
        return "Error: No fields provided for update."
    
    # Perform update
    success = hr_system.update_employee(emp_id.strip(), **update_kwargs)
    if success:
        updated_fields = ', '.join(update_kwargs.keys())
        return f"✓ Successfully updated employee {emp_id}. Changed: {updated_fields}"
    return f"Failed to update employee {emp_id}."


@tool
def delete_employee(
    emp_id: Annotated[str, "Employee ID to delete"]
) -> str:
    """Delete an employee from the system.
    
    Use this tool when the user wants to remove or delete an employee record.
    This action is permanent.
    """
    # Check if employee exists
    existing = hr_system.find_employee_by_id(emp_id.strip())
    if not existing:
        return f"Error: No employee found with ID {emp_id}"
    
    success = hr_system.delete_employee(emp_id.strip())
    if success:
        return f"✓ Successfully deleted employee {emp_id}."
    return f"Failed to delete employee {emp_id}."


@tool
def salary_report() -> str:
    """Generate a salary report with total payout and department averages.
    
    Use this tool when the user wants salary statistics, payroll information,
    or department salary analysis.
    """
    total, dept_avgs = hr_system.salary_report()
    
    lines = [
        "### Salary Report",
        f"**Total Salary Payout**: ${total:,.2f}"
    ]
    
    if dept_avgs:
        lines.append("\n**Average Salary by Department**:")
        for dept, avg in dept_avgs:
            lines.append(f"- **{dept}**: ${avg:,.2f}")
    else:
        lines.append("\nNo department data available.")
    
    return "\n".join(lines)


# --- Create Agent ---

# Initialize the LLM
try:
    # Try to use environment variable, fallback to prompt user
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    model = init_chat_model(
        "google_genai:gemini-1.5-flash",
        temperature=0.1,
    )
    
    # Define tools list
    tools = [
        add_employee,
        view_all_employees,
        search_employee,
        update_employee,
        delete_employee,
        salary_report
    ]
    
    # Create system prompt
    system_prompt = """You are a helpful HR assistant with access to an employee database.

Your job is to help users manage employee records efficiently and accurately.

IMPORTANT GUIDELINES:
1. Always be clear and professional in your responses.
2. When users ask to add, update, delete, or search for employees, use the appropriate tools.
3. If you need more information (like a missing employee ID), politely ask the user.
4. For salary inputs, users can provide numbers with commas or currency symbols.
5. When showing employee lists, present information in a clear, readable format.
6. Always confirm successful operations to the user.

Available tools:
- add_employee: Create a new employee record
- view_all_employees: List all employees  
- search_employee: Find employees by ID or name
- update_employee: Modify employee information
- delete_employee: Remove an employee record
- salary_report: Generate salary statistics

Be helpful, accurate, and efficient!"""
    
    # Create the agent using LangChain 1.1+ API
    agent = create_agent(
        model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    agent_initialized = True

except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None
    agent_initialized = False


# --- Main chat function ---

def chat_with_hr(user_input: str) -> str:
    """Main function to interact with the HR agent."""
    
    if not agent_initialized:
        return (
            "❌ Agent not initialized. Please ensure:\n"
            "1. GEMINI_API_KEY is set in your .env file\n"
            "2. You have installed: pip install langchain langchain-google-genai\n"
            "3. Get your API key from: https://makersuite.google.com/app/apikey"
        )
    
    try:
        # Invoke the agent with the user input
        response = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
        
        # Extract the final message
        if "messages" in response:
            last_message = response["messages"][-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            return str(last_message)
        
        return str(response)
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "API key" in error_msg or "GEMINI_API_KEY" in error_msg:
            return (
                "❌ API Key Error: Please check your GEMINI_API_KEY in the .env file.\n"
                "Get a free key from: https://makersuite.google.com/app/apikey"
            )
        elif "rate limit" in error_msg.lower():
            return "❌ Rate limit exceeded. Please wait a moment and try again."
        elif "timeout" in error_msg.lower():
            return "❌ Request timed out. Please try again."
        else:
            return f"❌ An error occurred: {error_msg}\n\nPlease try rephrasing your request."