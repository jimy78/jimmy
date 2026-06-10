"""Complete HR tools for the Claude agent."""

import json
from datetime import datetime, date
from .database import (
    SessionLocal, Employee, LeaveBalance, LeaveRequest, Absence, Policy,
    Payslip, Training, TrainingEnrollment, TrainingBudget, Expense,
    JobOpening, PerformanceReview, OnboardingChecklist,
)

TOOLS = [
    {
        "name": "lookup_employee",
        "description": "Search for an employee by name or employee ID. Returns profile: name, department, position, hire date, contract type, manager, active status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Employee name (partial match) or employee ID (e.g. EMP001)"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_leave_balance",
        "description": "Get leave balance for an employee: vacation days (total/used/remaining), RTT days, and sick days used for the current year.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID, e.g. EMP001"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "request_leave",
        "description": "Submit a leave request for an employee. Types: conges_payes, rtt, conges_sans_solde, conge_special.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "leave_type": {"type": "string", "enum": ["conges_payes", "rtt", "conges_sans_solde", "conge_special"], "description": "Type of leave"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "reason": {"type": "string", "description": "Optional reason for the leave"},
            },
            "required": ["employee_id", "leave_type", "start_date", "end_date"],
        },
    },
    {
        "name": "get_leave_requests",
        "description": "List leave requests for an employee, optionally filtered by status (pending, approved, rejected).",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "status": {"type": "string", "enum": ["pending", "approved", "rejected", "all"], "description": "Filter by status (default: all)"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "log_absence",
        "description": "Declare an absence (sick leave, child sick, work accident, other) for an employee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "absence_type": {"type": "string", "enum": ["maladie", "enfant_malade", "accident_travail", "autre"], "description": "Type of absence"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "medical_certificate": {"type": "boolean", "description": "Whether a medical certificate was provided"},
                "notes": {"type": "string", "description": "Additional notes"},
            },
            "required": ["employee_id", "absence_type", "start_date", "end_date"],
        },
    },
    {
        "name": "get_absences",
        "description": "List absences for an employee or the whole company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID (optional, omit for all)"},
            },
            "required": [],
        },
    },
    {
        "name": "search_policy",
        "description": "Search company HR policies by keyword or category. Categories: conges, teletravail, maladie, formation, frais, contrat, ethique, rgpd, bien-etre, organisation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keyword or category to search for"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_department_employees",
        "description": "List all active employees in a department.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {"type": "string", "description": "Department name: Engineering, Marketing, HR, Finance"}
            },
            "required": ["department"],
        },
    },
    {
        "name": "get_org_chart",
        "description": "Get the organizational chart: manager, direct reports, and team structure for an employee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "get_payslip_info",
        "description": "Get payslip information for an employee for a given month/year. Shows gross/net salary, bonuses, deductions, employer contributions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "month": {"type": "integer", "description": "Month (1-12), defaults to current month"},
                "year": {"type": "integer", "description": "Year, defaults to current year"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "get_contract_info",
        "description": "Get contract details: type (CDI/CDD/Stage), trial period, end date, seniority.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "get_training_catalog",
        "description": "List available trainings. Optionally filter by category: technique, management, bien-etre, bureautique, langues, juridique.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter by category (optional)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_training_budget",
        "description": "Get training budget for an employee: total/used/remaining budget and enrollment history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "enroll_training",
        "description": "Enroll an employee in a training from the catalog.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "training_id": {"type": "integer", "description": "Training ID from the catalog"},
            },
            "required": ["employee_id", "training_id"],
        },
    },
    {
        "name": "submit_expense",
        "description": "Submit an expense report for an employee.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "category": {"type": "string", "enum": ["repas", "transport", "deplacement", "materiel", "hotel", "autre"], "description": "Expense category"},
                "description": {"type": "string", "description": "Description of the expense"},
                "amount": {"type": "number", "description": "Amount in EUR"},
                "receipt_date": {"type": "string", "description": "Date of the receipt (YYYY-MM-DD)"},
            },
            "required": ["employee_id", "category", "description", "amount", "receipt_date"],
        },
    },
    {
        "name": "get_expenses",
        "description": "List expense reports for an employee, optionally filtered by status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "status": {"type": "string", "enum": ["pending", "approved", "rejected", "all"], "description": "Filter by status (default: all)"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "search_job_openings",
        "description": "Search open job positions (internal mobility and external). Optionally filter by department.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {"type": "string", "description": "Filter by department (optional)"},
                "internal_only": {"type": "boolean", "description": "Only show internal mobility positions (default: false)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_performance_review",
        "description": "Get performance reviews for an employee: objectives, achievements, rating, improvement areas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"},
                "year": {"type": "integer", "description": "Year of the review (optional, defaults to all)"},
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "get_onboarding_checklist",
        "description": "Get the onboarding checklist for an employee: tasks, completion status, due dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "calculate_seniority",
        "description": "Calculate seniority: years of service, additional leave days earned, next milestone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "string", "description": "Employee ID"}
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "team_analytics",
        "description": "Get team/department analytics: headcount, absence rate, turnover, average seniority, leave usage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {"type": "string", "description": "Department name (optional, omit for company-wide)"},
            },
            "required": [],
        },
    },
    {
        "name": "search_directory",
        "description": "Search the employee directory by name, position, department, or keyword to find the right contact.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query: name, job title, department, or keyword"}
            },
            "required": ["query"],
        },
    },
]


def execute_tool(name: str, tool_input: dict) -> str:
    db = SessionLocal()
    try:
        handler = _HANDLERS.get(name)
        if handler:
            return handler(db, tool_input)
        return json.dumps({"error": f"Unknown tool: {name}"})
    finally:
        db.close()


def _fmt(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def _emp_to_dict(e):
    return {
        "employee_id": e.employee_id, "name": e.name, "department": e.department,
        "position": e.position, "email": e.email, "phone": e.phone,
        "hire_date": str(e.hire_date.date()) if e.hire_date else None,
        "contract_type": e.contract_type, "manager_id": e.manager_id, "is_active": e.is_active,
    }


def _lookup_employee(db, inp):
    q = inp["query"]
    emp = db.query(Employee).filter(Employee.employee_id == q.upper()).first()
    if not emp:
        employees = db.query(Employee).filter(Employee.name.ilike(f"%{q}%")).all()
        if not employees:
            return _fmt({"message": f"Aucun employe trouve pour '{q}'."})
        return _fmt([_emp_to_dict(e) for e in employees])
    return _fmt(_emp_to_dict(emp))


def _get_leave_balance(db, inp):
    eid = inp["employee_id"].upper()
    bal = db.query(LeaveBalance).filter(LeaveBalance.employee_id == eid, LeaveBalance.year == datetime.now().year).first()
    if not bal:
        return _fmt({"message": f"Aucun solde de conges pour {eid}."})
    return _fmt({
        "employee_id": bal.employee_id, "year": bal.year,
        "conges_payes": {"total": bal.total_days, "used": bal.used_days, "remaining": bal.total_days - bal.used_days},
        "rtt": {"total": bal.rtt_total, "used": bal.rtt_used, "remaining": bal.rtt_total - bal.rtt_used},
        "sick_days_used": bal.sick_days_used,
    })


def _request_leave(db, inp):
    eid = inp["employee_id"].upper()
    emp = db.query(Employee).filter(Employee.employee_id == eid).first()
    if not emp:
        return _fmt({"error": f"Employe {eid} non trouve."})
    start = date.fromisoformat(inp["start_date"])
    end = date.fromisoformat(inp["end_date"])
    days = max(1, (end - start).days + 1)
    lr = LeaveRequest(employee_id=eid, leave_type=inp["leave_type"], start_date=start, end_date=end, days_count=days, status="pending", reason=inp.get("reason"))
    db.add(lr)
    db.commit()
    return _fmt({"message": f"Demande de conge soumise ({days} jours du {start} au {end}). Statut : en attente.", "request_id": lr.id})


def _get_leave_requests(db, inp):
    eid = inp["employee_id"].upper()
    q = db.query(LeaveRequest).filter(LeaveRequest.employee_id == eid)
    status = inp.get("status", "all")
    if status and status != "all":
        q = q.filter(LeaveRequest.status == status)
    rows = q.order_by(LeaveRequest.start_date.desc()).all()
    if not rows:
        return _fmt({"message": "Aucune demande de conge trouvee."})
    return _fmt([{"id": r.id, "type": r.leave_type, "start_date": str(r.start_date), "end_date": str(r.end_date), "days": r.days_count, "status": r.status, "reason": r.reason} for r in rows])


def _log_absence(db, inp):
    eid = inp["employee_id"].upper()
    a = Absence(employee_id=eid, absence_type=inp["absence_type"], start_date=date.fromisoformat(inp["start_date"]), end_date=date.fromisoformat(inp["end_date"]), medical_certificate=inp.get("medical_certificate", False), notes=inp.get("notes"))
    db.add(a)
    db.commit()
    return _fmt({"message": f"Absence declaree pour {eid} du {inp['start_date']} au {inp['end_date']}.", "absence_id": a.id})


def _get_absences(db, inp):
    q = db.query(Absence)
    eid = inp.get("employee_id")
    if eid:
        q = q.filter(Absence.employee_id == eid.upper())
    rows = q.order_by(Absence.start_date.desc()).all()
    if not rows:
        return _fmt({"message": "Aucune absence trouvee."})
    return _fmt([{"employee_id": a.employee_id, "type": a.absence_type, "start_date": str(a.start_date), "end_date": str(a.end_date), "medical_certificate": a.medical_certificate, "notes": a.notes} for a in rows])


def _search_policy(db, inp):
    q = inp["query"]
    policies = db.query(Policy).filter((Policy.category.ilike(f"%{q}%")) | (Policy.title.ilike(f"%{q}%")) | (Policy.content.ilike(f"%{q}%"))).all()
    if not policies:
        return _fmt({"message": f"Aucune politique trouvee pour '{q}'."})
    return _fmt([{"title": p.title, "category": p.category, "content": p.content} for p in policies])


def _list_department_employees(db, inp):
    dept = inp["department"]
    employees = db.query(Employee).filter(Employee.department.ilike(f"%{dept}%"), Employee.is_active.is_(True)).all()
    if not employees:
        return _fmt({"message": f"Aucun employe actif dans '{dept}'."})
    return _fmt([{"employee_id": e.employee_id, "name": e.name, "position": e.position, "manager_id": e.manager_id} for e in employees])


def _get_org_chart(db, inp):
    eid = inp["employee_id"].upper()
    emp = db.query(Employee).filter(Employee.employee_id == eid).first()
    if not emp:
        return _fmt({"error": f"Employe {eid} non trouve."})
    manager = None
    if emp.manager_id:
        mgr = db.query(Employee).filter(Employee.employee_id == emp.manager_id).first()
        if mgr:
            manager = {"employee_id": mgr.employee_id, "name": mgr.name, "position": mgr.position}
    reports = db.query(Employee).filter(Employee.manager_id == eid, Employee.is_active.is_(True)).all()
    colleagues = db.query(Employee).filter(Employee.department == emp.department, Employee.is_active.is_(True), Employee.employee_id != eid).all()
    return _fmt({
        "employee": {"employee_id": emp.employee_id, "name": emp.name, "position": emp.position, "department": emp.department},
        "manager": manager,
        "direct_reports": [{"employee_id": r.employee_id, "name": r.name, "position": r.position} for r in reports],
        "team_colleagues": [{"employee_id": c.employee_id, "name": c.name, "position": c.position} for c in colleagues],
    })


def _get_payslip_info(db, inp):
    eid = inp["employee_id"].upper()
    month = inp.get("month", datetime.now().month)
    year = inp.get("year", datetime.now().year)
    ps = db.query(Payslip).filter(Payslip.employee_id == eid, Payslip.month == month, Payslip.year == year).first()
    if not ps:
        return _fmt({"message": f"Aucun bulletin de paie pour {eid} en {month:02d}/{year}."})
    return _fmt({
        "employee_id": ps.employee_id, "period": f"{ps.month:02d}/{ps.year}",
        "salary_gross": float(ps.salary_gross), "salary_net": float(ps.salary_net),
        "bonus": float(ps.bonus), "deductions": float(ps.deductions),
        "employer_contributions": float(ps.employer_contributions),
        "overtime_hours": ps.overtime_hours, "overtime_amount": float(ps.overtime_amount),
    })


def _get_contract_info(db, inp):
    eid = inp["employee_id"].upper()
    emp = db.query(Employee).filter(Employee.employee_id == eid).first()
    if not emp:
        return _fmt({"error": f"Employe {eid} non trouve."})
    today = date.today()
    seniority_days = (today - emp.hire_date.date()).days if emp.hire_date else 0
    trial_status = "completed"
    if emp.trial_end_date and emp.trial_end_date > today:
        trial_status = "in_progress"
    return _fmt({
        "employee_id": emp.employee_id, "name": emp.name, "contract_type": emp.contract_type,
        "hire_date": str(emp.hire_date.date()) if emp.hire_date else None,
        "contract_end_date": str(emp.contract_end_date) if emp.contract_end_date else None,
        "trial_end_date": str(emp.trial_end_date) if emp.trial_end_date else None,
        "trial_status": trial_status, "seniority_years": round(seniority_days / 365.25, 1),
    })


def _get_training_catalog(db, inp):
    q = db.query(Training).filter(Training.is_available.is_(True))
    cat = inp.get("category")
    if cat:
        q = q.filter(Training.category.ilike(f"%{cat}%"))
    trainings = q.all()
    if not trainings:
        return _fmt({"message": "Aucune formation disponible."})
    return _fmt([{"id": t.id, "title": t.title, "category": t.category, "description": t.description, "duration_days": t.duration_days, "cost": float(t.cost), "provider": t.provider} for t in trainings])


def _get_training_budget(db, inp):
    eid = inp["employee_id"].upper()
    budget = db.query(TrainingBudget).filter(TrainingBudget.employee_id == eid, TrainingBudget.year == datetime.now().year).first()
    enrollments = db.query(TrainingEnrollment).filter(TrainingEnrollment.employee_id == eid).all()
    enrollment_list = []
    for e in enrollments:
        t = db.query(Training).filter(Training.id == e.training_id).first()
        enrollment_list.append({"training": t.title if t else "Unknown", "status": e.status, "completed_at": str(e.completed_at) if e.completed_at else None})
    return _fmt({
        "employee_id": eid,
        "budget": {"total": float(budget.total_budget) if budget else 1500, "used": float(budget.used_budget) if budget else 0, "remaining": float(budget.total_budget - budget.used_budget) if budget else 1500},
        "enrollments": enrollment_list,
    })


def _enroll_training(db, inp):
    eid = inp["employee_id"].upper()
    tid = inp["training_id"]
    training = db.query(Training).filter(Training.id == tid).first()
    if not training:
        return _fmt({"error": f"Formation {tid} non trouvee."})
    budget = db.query(TrainingBudget).filter(TrainingBudget.employee_id == eid, TrainingBudget.year == datetime.now().year).first()
    remaining = float(budget.total_budget - budget.used_budget) if budget else 1500
    if float(training.cost) > remaining:
        return _fmt({"error": f"Budget insuffisant. Reste {remaining} EUR, cout : {float(training.cost)} EUR."})
    enrollment = TrainingEnrollment(employee_id=eid, training_id=tid, status="pending", budget_year=datetime.now().year)
    db.add(enrollment)
    db.commit()
    return _fmt({"message": f"Inscription a '{training.title}' soumise. Statut : en attente de validation.", "enrollment_id": enrollment.id})


def _submit_expense(db, inp):
    eid = inp["employee_id"].upper()
    exp = Expense(employee_id=eid, category=inp["category"], description=inp["description"], amount=inp["amount"], receipt_date=date.fromisoformat(inp["receipt_date"]), status="pending")
    db.add(exp)
    db.commit()
    return _fmt({"message": f"Note de frais soumise ({inp['amount']} EUR). Statut : en attente.", "expense_id": exp.id})


def _get_expenses(db, inp):
    eid = inp["employee_id"].upper()
    q = db.query(Expense).filter(Expense.employee_id == eid)
    status = inp.get("status", "all")
    if status and status != "all":
        q = q.filter(Expense.status == status)
    rows = q.order_by(Expense.receipt_date.desc()).all()
    if not rows:
        return _fmt({"message": "Aucune note de frais trouvee."})
    return _fmt([{"id": e.id, "category": e.category, "description": e.description, "amount": float(e.amount), "receipt_date": str(e.receipt_date), "status": e.status} for e in rows])


def _search_job_openings(db, inp):
    q = db.query(JobOpening).filter(JobOpening.is_open.is_(True))
    dept = inp.get("department")
    if dept:
        q = q.filter(JobOpening.department.ilike(f"%{dept}%"))
    if inp.get("internal_only"):
        q = q.filter(JobOpening.is_internal.is_(True))
    jobs = q.all()
    if not jobs:
        return _fmt({"message": "Aucun poste ouvert."})
    return _fmt([{"id": j.id, "title": j.title, "department": j.department, "description": j.description, "contract_type": j.contract_type, "location": j.location, "salary_range": j.salary_range, "is_internal": j.is_internal} for j in jobs])


def _get_performance_review(db, inp):
    eid = inp["employee_id"].upper()
    q = db.query(PerformanceReview).filter(PerformanceReview.employee_id == eid)
    year = inp.get("year")
    if year:
        q = q.filter(PerformanceReview.year == year)
    reviews = q.order_by(PerformanceReview.year.desc()).all()
    if not reviews:
        return _fmt({"message": f"Aucune evaluation trouvee pour {eid}."})
    return _fmt([{"year": r.year, "rating": r.rating, "status": r.status, "objectives": r.objectives, "achievements": r.achievements, "areas_of_improvement": r.areas_of_improvement, "comments": r.comments, "review_date": str(r.review_date) if r.review_date else None, "reviewer_id": r.reviewer_id} for r in reviews])


def _get_onboarding_checklist(db, inp):
    eid = inp["employee_id"].upper()
    tasks = db.query(OnboardingChecklist).filter(OnboardingChecklist.employee_id == eid).order_by(OnboardingChecklist.due_date).all()
    if not tasks:
        return _fmt({"message": f"Aucune checklist d'integration pour {eid}."})
    total = len(tasks)
    completed = sum(1 for t in tasks if t.is_completed)
    return _fmt({
        "employee_id": eid, "progress": f"{completed}/{total} taches completees",
        "tasks": [{"task": t.task, "category": t.category, "is_completed": t.is_completed, "due_date": str(t.due_date) if t.due_date else None, "completed_at": str(t.completed_at) if t.completed_at else None} for t in tasks],
    })


def _calculate_seniority(db, inp):
    eid = inp["employee_id"].upper()
    emp = db.query(Employee).filter(Employee.employee_id == eid).first()
    if not emp or not emp.hire_date:
        return _fmt({"error": f"Employe {eid} non trouve ou date d'embauche manquante."})
    today = date.today()
    hire = emp.hire_date.date()
    total_days = (today - hire).days
    years = total_days / 365.25
    extra_leave = 3 if years >= 15 else 2 if years >= 10 else 1 if years >= 5 else 0
    next_milestone = None
    for m in [5, 10, 15]:
        if years < m:
            next_milestone = {"years": m, "extra_days": {5: 1, 10: 2, 15: 3}[m], "date": str(date(hire.year + m, hire.month, hire.day))}
            break
    return _fmt({"employee_id": eid, "name": emp.name, "hire_date": str(hire), "seniority_years": round(years, 1), "seniority_days": total_days, "additional_leave_days": extra_leave, "next_milestone": next_milestone})


def _team_analytics(db, inp):
    dept = inp.get("department")
    q = db.query(Employee)
    if dept:
        q = q.filter(Employee.department.ilike(f"%{dept}%"))
    all_emps = q.all()
    active = [e for e in all_emps if e.is_active]
    inactive = [e for e in all_emps if not e.is_active]
    today = date.today()
    avg_seniority = sum((today - e.hire_date.date()).days for e in active if e.hire_date) / max(len(active), 1) / 365.25
    year = datetime.now().year
    total_leave_used = total_leave_total = 0
    for e in active:
        bal = db.query(LeaveBalance).filter(LeaveBalance.employee_id == e.employee_id, LeaveBalance.year == year).first()
        if bal:
            total_leave_used += bal.used_days
            total_leave_total += bal.total_days
    absence_q = db.query(Absence).filter(Absence.start_date >= date(year, 1, 1))
    if dept:
        absence_q = absence_q.join(Employee, Absence.employee_id == Employee.employee_id).filter(Employee.department.ilike(f"%{dept}%"))
    absence_count = absence_q.count()
    label = dept if dept else "Entreprise"
    return _fmt({
        "scope": label, "headcount_active": len(active), "headcount_inactive": len(inactive),
        "turnover_rate": f"{len(inactive) / max(len(all_emps), 1) * 100:.1f}%",
        "average_seniority_years": round(avg_seniority, 1),
        "leave_usage": {"total_used": total_leave_used, "total_available": total_leave_total, "usage_rate": f"{total_leave_used / max(total_leave_total, 1) * 100:.1f}%"},
        "absences_this_year": absence_count,
    })


def _search_directory(db, inp):
    q = inp["query"]
    employees = db.query(Employee).filter(Employee.is_active.is_(True), (Employee.name.ilike(f"%{q}%")) | (Employee.position.ilike(f"%{q}%")) | (Employee.department.ilike(f"%{q}%"))).all()
    if not employees:
        return _fmt({"message": f"Aucun resultat pour '{q}'."})
    return _fmt([{"employee_id": e.employee_id, "name": e.name, "position": e.position, "department": e.department, "email": e.email, "phone": e.phone} for e in employees])


_HANDLERS = {
    "lookup_employee": _lookup_employee, "get_leave_balance": _get_leave_balance,
    "request_leave": _request_leave, "get_leave_requests": _get_leave_requests,
    "log_absence": _log_absence, "get_absences": _get_absences,
    "search_policy": _search_policy, "list_department_employees": _list_department_employees,
    "get_org_chart": _get_org_chart, "get_payslip_info": _get_payslip_info,
    "get_contract_info": _get_contract_info, "get_training_catalog": _get_training_catalog,
    "get_training_budget": _get_training_budget, "enroll_training": _enroll_training,
    "submit_expense": _submit_expense, "get_expenses": _get_expenses,
    "search_job_openings": _search_job_openings, "get_performance_review": _get_performance_review,
    "get_onboarding_checklist": _get_onboarding_checklist, "calculate_seniority": _calculate_seniority,
    "team_analytics": _team_analytics, "search_directory": _search_directory,
}
