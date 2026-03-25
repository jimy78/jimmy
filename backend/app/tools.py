"""HR tools for the Claude agent.

Each tool is defined as an Anthropic tool schema + an execute function
that queries the database.
"""

import json
from datetime import datetime
from .database import SessionLocal, Employee, LeaveBalance, Policy

# ---------------------------------------------------------------------------
# Tool definitions (sent to the Claude API)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "lookup_employee",
        "description": "Search for an employee by name or employee ID. Returns basic info: name, department, position, hire date, active status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Employee name (partial match) or employee ID (e.g. EMP001)",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_leave_balance",
        "description": "Get the leave (vacation) balance for an employee: total days, used days, remaining days, and sick days used.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The employee ID, e.g. EMP001",
                }
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "search_policy",
        "description": "Search company HR policies by keyword or category. Categories: conges, teletravail, maladie, formation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword or category to search for in HR policies",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_department_employees",
        "description": "List all active employees in a given department.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name, e.g. Engineering, Marketing, HR, Finance",
                }
            },
            "required": ["department"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool by name and return a JSON string result."""
    db = SessionLocal()
    try:
        if name == "lookup_employee":
            return _lookup_employee(db, tool_input["query"])
        elif name == "get_leave_balance":
            return _get_leave_balance(db, tool_input["employee_id"])
        elif name == "search_policy":
            return _search_policy(db, tool_input["query"])
        elif name == "list_department_employees":
            return _list_department_employees(db, tool_input["department"])
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    finally:
        db.close()


def _lookup_employee(db, query: str) -> str:
    query_upper = query.upper()
    # Try exact ID match first
    emp = db.query(Employee).filter(Employee.employee_id == query_upper).first()
    if not emp:
        # Partial name search (case-insensitive)
        employees = db.query(Employee).filter(
            Employee.name.ilike(f"%{query}%")
        ).all()
        if not employees:
            return json.dumps({"message": f"Aucun employe trouve pour '{query}'."})
        results = [
            {
                "employee_id": e.employee_id,
                "name": e.name,
                "department": e.department,
                "position": e.position,
                "hire_date": e.hire_date.strftime("%Y-%m-%d") if e.hire_date else None,
                "is_active": e.is_active,
            }
            for e in employees
        ]
        return json.dumps(results, ensure_ascii=False)

    return json.dumps(
        {
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "position": emp.position,
            "hire_date": emp.hire_date.strftime("%Y-%m-%d") if emp.hire_date else None,
            "is_active": emp.is_active,
        },
        ensure_ascii=False,
    )


def _get_leave_balance(db, employee_id: str) -> str:
    balance = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id.upper())
        .filter(LeaveBalance.year == datetime.now().year)
        .first()
    )
    if not balance:
        return json.dumps({"message": f"Aucun solde de conges trouve pour {employee_id}."})

    return json.dumps(
        {
            "employee_id": balance.employee_id,
            "year": balance.year,
            "total_days": balance.total_days,
            "used_days": balance.used_days,
            "remaining_days": balance.total_days - balance.used_days,
            "sick_days_used": balance.sick_days_used,
        }
    )


def _search_policy(db, query: str) -> str:
    # Search by category or keyword in title/content
    policies = (
        db.query(Policy)
        .filter(
            (Policy.category.ilike(f"%{query}%"))
            | (Policy.title.ilike(f"%{query}%"))
            | (Policy.content.ilike(f"%{query}%"))
        )
        .all()
    )
    if not policies:
        return json.dumps({"message": f"Aucune politique trouvee pour '{query}'."})

    results = [
        {
            "title": p.title,
            "category": p.category,
            "content": p.content,
        }
        for p in policies
    ]
    return json.dumps(results, ensure_ascii=False)


def _list_department_employees(db, department: str) -> str:
    employees = (
        db.query(Employee)
        .filter(Employee.department.ilike(f"%{department}%"))
        .filter(Employee.is_active.is_(True))
        .all()
    )
    if not employees:
        return json.dumps({"message": f"Aucun employe actif dans le departement '{department}'."})

    results = [
        {
            "employee_id": e.employee_id,
            "name": e.name,
            "position": e.position,
        }
        for e in employees
    ]
    return json.dumps(results, ensure_ascii=False)
