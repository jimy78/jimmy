import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, Date, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, date

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hragent:hrpass@db:5432/hragent",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100))
    position = Column(String(200))
    email = Column(String(200))
    phone = Column(String(30))
    hire_date = Column(DateTime)
    birth_date = Column(Date)
    manager_id = Column(String(20), ForeignKey("employees.employee_id"), nullable=True)
    contract_type = Column(String(50), default="CDI")
    contract_end_date = Column(Date, nullable=True)
    trial_end_date = Column(Date, nullable=True)
    salary_gross = Column(Numeric(10, 2), nullable=True)
    salary_net = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False, default=2026)
    total_days = Column(Integer, default=25)
    used_days = Column(Integer, default=0)
    sick_days_used = Column(Integer, default=0)
    rtt_total = Column(Integer, default=10)
    rtt_used = Column(Integer, default=0)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(20), nullable=True)


class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    absence_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    medical_certificate = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    category = Column(String(100))
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    salary_gross = Column(Numeric(10, 2))
    salary_net = Column(Numeric(10, 2))
    bonus = Column(Numeric(10, 2), default=0)
    deductions = Column(Numeric(10, 2), default=0)
    employer_contributions = Column(Numeric(10, 2), default=0)
    overtime_hours = Column(Float, default=0)
    overtime_amount = Column(Numeric(10, 2), default=0)


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    duration_days = Column(Integer, default=1)
    cost = Column(Numeric(10, 2), default=0)
    provider = Column(String(200))
    is_available = Column(Boolean, default=True)


class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)
    status = Column(String(20), default="pending")
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    budget_year = Column(Integer, default=2026)


class TrainingBudget(Base):
    __tablename__ = "training_budgets"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    total_budget = Column(Numeric(10, 2), default=1500)
    used_budget = Column(Numeric(10, 2), default=0)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(10, 2), nullable=False)
    receipt_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(20), nullable=True)


class JobOpening(Base):
    __tablename__ = "job_openings"

    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    department = Column(String(100))
    description = Column(Text)
    contract_type = Column(String(50), default="CDI")
    location = Column(String(100), default="Paris")
    salary_range = Column(String(100))
    is_internal = Column(Boolean, default=True)
    is_open = Column(Boolean, default=True)
    posted_at = Column(DateTime, default=datetime.utcnow)
    hiring_manager_id = Column(String(20), nullable=True)


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    reviewer_id = Column(String(20), nullable=True)
    year = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=True)
    objectives = Column(Text)
    achievements = Column(Text)
    areas_of_improvement = Column(Text)
    comments = Column(Text)
    status = Column(String(20), default="draft")
    review_date = Column(Date, nullable=True)


class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    task = Column(String(300), nullable=False)
    category = Column(String(100))
    is_completed = Column(Boolean, default=False)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)


def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(Employee).count() > 0:
            return

        employees = [
            Employee(employee_id="EMP001", name="Marie Dupont", department="Engineering", position="Lead Developer", email="m.dupont@company.fr", phone="+33 6 12 34 56 78", hire_date=datetime(2021, 3, 15), birth_date=date(1988, 5, 22), manager_id=None, contract_type="CDI", trial_end_date=date(2021, 9, 15), salary_gross=5200, salary_net=4050, is_active=True),
            Employee(employee_id="EMP002", name="Jean Martin", department="Marketing", position="Marketing Manager", email="j.martin@company.fr", phone="+33 6 98 76 54 32", hire_date=datetime(2019, 7, 1), birth_date=date(1985, 11, 3), manager_id=None, contract_type="CDI", trial_end_date=date(2020, 1, 1), salary_gross=5800, salary_net=4520, is_active=True),
            Employee(employee_id="EMP003", name="Sophie Leroy", department="HR", position="HR Manager", email="s.leroy@company.fr", phone="+33 6 11 22 33 44", hire_date=datetime(2022, 1, 10), birth_date=date(1990, 8, 14), manager_id=None, contract_type="CDI", trial_end_date=date(2022, 7, 10), salary_gross=5500, salary_net=4290, is_active=True),
            Employee(employee_id="EMP004", name="Pierre Bernard", department="Engineering", position="DevOps Engineer", email="p.bernard@company.fr", phone="+33 6 55 66 77 88", hire_date=datetime(2023, 6, 20), birth_date=date(1992, 2, 28), manager_id="EMP001", contract_type="CDI", trial_end_date=date(2023, 12, 20), salary_gross=4500, salary_net=3510, is_active=True),
            Employee(employee_id="EMP005", name="Claire Moreau", department="Finance", position="Senior Accountant", email="c.moreau@company.fr", phone="+33 6 99 88 77 66", hire_date=datetime(2020, 11, 5), birth_date=date(1987, 4, 9), manager_id=None, contract_type="CDI", trial_end_date=date(2021, 5, 5), salary_gross=4800, salary_net=3744, is_active=False),
            Employee(employee_id="EMP006", name="Lucas Petit", department="Engineering", position="Junior Developer", email="l.petit@company.fr", phone="+33 6 22 33 44 55", hire_date=datetime(2024, 9, 1), birth_date=date(1998, 12, 1), manager_id="EMP001", contract_type="CDD", contract_end_date=date(2026, 8, 31), trial_end_date=date(2025, 3, 1), salary_gross=3200, salary_net=2496, is_active=True),
            Employee(employee_id="EMP007", name="Emma Girard", department="Marketing", position="Content Specialist", email="e.girard@company.fr", phone="+33 6 44 55 66 77", hire_date=datetime(2025, 1, 15), birth_date=date(1995, 7, 19), manager_id="EMP002", contract_type="CDI", trial_end_date=date(2025, 7, 15), salary_gross=3800, salary_net=2964, is_active=True),
            Employee(employee_id="EMP008", name="Thomas Roux", department="HR", position="Recruitment Officer", email="t.roux@company.fr", phone="+33 6 66 77 88 99", hire_date=datetime(2024, 3, 1), birth_date=date(1993, 10, 25), manager_id="EMP003", contract_type="CDI", trial_end_date=date(2024, 9, 1), salary_gross=3600, salary_net=2808, is_active=True),
            Employee(employee_id="EMP009", name="Julie Fontaine", department="Finance", position="Financial Controller", email="j.fontaine@company.fr", phone="+33 6 33 22 11 00", hire_date=datetime(2023, 11, 1), birth_date=date(1986, 1, 30), manager_id=None, contract_type="CDI", trial_end_date=date(2024, 5, 1), salary_gross=5000, salary_net=3900, is_active=True),
            Employee(employee_id="EMP010", name="Alexandre Blanc", department="Engineering", position="QA Engineer", email="a.blanc@company.fr", phone="+33 6 77 88 99 00", hire_date=datetime(2025, 4, 1), birth_date=date(1996, 6, 12), manager_id="EMP001", contract_type="CDI", trial_end_date=date(2025, 10, 1), salary_gross=3900, salary_net=3042, is_active=True),
        ]
        db.add_all(employees)

        balances = [
            LeaveBalance(employee_id="EMP001", year=2026, total_days=26, used_days=8, sick_days_used=2, rtt_total=10, rtt_used=4),
            LeaveBalance(employee_id="EMP002", year=2026, total_days=27, used_days=12, sick_days_used=1, rtt_total=10, rtt_used=6),
            LeaveBalance(employee_id="EMP003", year=2026, total_days=25, used_days=5, sick_days_used=0, rtt_total=10, rtt_used=2),
            LeaveBalance(employee_id="EMP004", year=2026, total_days=25, used_days=3, sick_days_used=3, rtt_total=10, rtt_used=1),
            LeaveBalance(employee_id="EMP005", year=2026, total_days=25, used_days=25, sick_days_used=5, rtt_total=10, rtt_used=10),
            LeaveBalance(employee_id="EMP006", year=2026, total_days=25, used_days=6, sick_days_used=0, rtt_total=10, rtt_used=3),
            LeaveBalance(employee_id="EMP007", year=2026, total_days=25, used_days=2, sick_days_used=1, rtt_total=10, rtt_used=0),
            LeaveBalance(employee_id="EMP008", year=2026, total_days=25, used_days=7, sick_days_used=2, rtt_total=10, rtt_used=5),
            LeaveBalance(employee_id="EMP009", year=2026, total_days=25, used_days=10, sick_days_used=0, rtt_total=10, rtt_used=4),
            LeaveBalance(employee_id="EMP010", year=2026, total_days=25, used_days=1, sick_days_used=0, rtt_total=10, rtt_used=0),
        ]
        db.add_all(balances)

        leave_requests = [
            LeaveRequest(employee_id="EMP001", leave_type="conges_payes", start_date=date(2026, 7, 14), end_date=date(2026, 7, 25), days_count=10, status="approved", approved_by="EMP003"),
            LeaveRequest(employee_id="EMP004", leave_type="rtt", start_date=date(2026, 6, 20), end_date=date(2026, 6, 20), days_count=1, status="pending"),
            LeaveRequest(employee_id="EMP007", leave_type="conges_payes", start_date=date(2026, 8, 3), end_date=date(2026, 8, 14), days_count=10, status="pending"),
            LeaveRequest(employee_id="EMP006", leave_type="conges_sans_solde", start_date=date(2026, 9, 1), end_date=date(2026, 9, 5), days_count=5, status="rejected", reason="Periode de forte activite"),
        ]
        db.add_all(leave_requests)

        absences = [
            Absence(employee_id="EMP004", absence_type="maladie", start_date=date(2026, 3, 10), end_date=date(2026, 3, 14), medical_certificate=True, notes="Grippe"),
            Absence(employee_id="EMP002", absence_type="maladie", start_date=date(2026, 5, 5), end_date=date(2026, 5, 5), medical_certificate=True),
            Absence(employee_id="EMP008", absence_type="enfant_malade", start_date=date(2026, 4, 22), end_date=date(2026, 4, 23), medical_certificate=False),
            Absence(employee_id="EMP001", absence_type="maladie", start_date=date(2026, 2, 3), end_date=date(2026, 2, 4), medical_certificate=True),
        ]
        db.add_all(absences)

        policies = [
            Policy(title="Politique de conges payes", category="conges", content="Chaque salarie a droit a 25 jours ouvrables de conges payes par an. Les conges doivent etre poses au moins 2 semaines a l'avance pour les absences de plus de 3 jours, 48h pour les absences courtes. Le report est autorise jusqu'au 31 mars de l'annee suivante (max 5 jours). Conges d'anciennete : +1 jour apres 5 ans, +2 jours apres 10 ans, +3 jours apres 15 ans."),
            Policy(title="RTT (Reduction du Temps de Travail)", category="conges", content="Les cadres au forfait jours beneficient de 10 jours de RTT par an. Les RTT doivent etre poses dans l'annee civile (pas de report). 5 RTT sont a l'initiative du salarie, 5 a l'initiative de l'employeur. Les RTT non pris au 31 decembre sont perdus."),
            Policy(title="Conges speciaux", category="conges", content="Mariage/PACS du salarie : 4 jours. Naissance/adoption : 3 jours. Deces d'un conjoint : 5 jours. Deces d'un parent : 3 jours. Demenagement : 1 jour/an. Enfant malade (< 16 ans) : 3 jours/an (sur justificatif). Conge parental : jusqu'a 3 ans (temps plein ou partiel)."),
            Policy(title="Teletravail", category="teletravail", content="Le teletravail est autorise jusqu'a 3 jours par semaine. Une demande formelle doit etre soumise au manager via le portail RH. L'entreprise fournit l'equipement necessaire (ecran, clavier, souris). Indemnite de 2.70 EUR/jour de teletravail. Le mardi et jeudi sont des jours de presence obligatoire au bureau."),
            Policy(title="Arret maladie", category="maladie", content="En cas d'arret maladie : 1) Prevenir son manager dans les 24h. 2) Fournir un certificat medical a la CPAM et a l'employeur sous 48h. Maintien de salaire a 100% pendant 90 jours, puis a 80% les 90 jours suivants (sous reserve d'un an d'anciennete). Les 3 premiers jours constituent le delai de carence."),
            Policy(title="Formation professionnelle", category="formation", content="Budget formation annuel de 1500 EUR par salarie. Demandes soumises via le portail RH et validees par le manager. CPF (Compte Personnel de Formation) independant : 500 EUR/an. Catalogue de formations internes et externes disponible. Les formations sont realisees sur le temps de travail."),
            Policy(title="Notes de frais", category="frais", content="Soumission dans les 30 jours suivant la depense. Justificatif obligatoire. Plafonds : repas 25 EUR, taxi/VTC 50 EUR, hotel 150 EUR/nuit (Paris), 120 EUR/nuit (province). Frais kilometriques : 0.55 EUR/km. Remboursement sous 15 jours apres validation."),
            Policy(title="Periode d'essai", category="contrat", content="CDI : 4 mois pour les cadres (renouvelable 4 mois), 3 mois pour les agents de maitrise, 2 mois pour les employes. CDD : 1 jour par semaine de contrat (max 2 semaines pour CDD < 6 mois, max 1 mois pour CDD > 6 mois). Preavis de rupture : 24h (< 8 jours), 48h (8 jours a 1 mois), 2 semaines (1 a 3 mois), 1 mois (> 3 mois)."),
            Policy(title="Demission et preavis", category="contrat", content="Preavis de demission : 3 mois pour les cadres, 1 mois pour les non-cadres. Lettre de demission en main propre ou recommande. L'employeur peut dispenser du preavis (avec maintien du salaire). Solde de tout compte verse au dernier jour du contrat."),
            Policy(title="Harcelement et discrimination", category="ethique", content="Tolerance zero envers le harcelement moral, sexuel et toute discrimination. Referent harcelement : Sophie Leroy (EMP003). Signalements anonymes via le portail ethique. Enquete interne sous 48h. Sanctions de l'avertissement au licenciement."),
            Policy(title="Protection des donnees (RGPD)", category="rgpd", content="Donnees personnelles traitees conformement au RGPD. Finalites : gestion administrative, paie, formation. Duree de conservation : 5 ans apres fin du contrat. Droits : acces, rectification, effacement, portabilite. DPO : dpo@company.fr."),
            Policy(title="Droit a la deconnexion", category="bien-etre", content="Droit a la deconnexion entre 20h et 8h en semaine et les week-ends. Aucun email ou message professionnel attendu hors heures de travail. Managers doivent utiliser l'envoi differe des emails. Exceptions pour astreintes planifiees."),
            Policy(title="Astreintes", category="organisation", content="Concernent les equipes Engineering et Support. Planning communique 15 jours a l'avance. Compensation : 150 EUR/semaine d'astreinte + heures d'intervention majorees a 150%. Maximum 1 semaine d'astreinte par mois. Repos compensateur obligatoire apres intervention nocturne."),
        ]
        db.add_all(policies)

        payslips = []
        salary_data = {
            "EMP001": (5200, 4050), "EMP002": (5800, 4520), "EMP003": (5500, 4290),
            "EMP004": (4500, 3510), "EMP006": (3200, 2496), "EMP007": (3800, 2964),
            "EMP008": (3600, 2808), "EMP009": (5000, 3900), "EMP010": (3900, 3042),
        }
        for emp_id, (gross, net) in salary_data.items():
            for month in [4, 5, 6]:
                bonus = 500 if month == 6 else 0
                payslips.append(Payslip(
                    employee_id=emp_id, month=month, year=2026,
                    salary_gross=gross, salary_net=net, bonus=bonus,
                    deductions=round(gross * 0.22, 2),
                    employer_contributions=round(gross * 0.42, 2),
                ))
        db.add_all(payslips)

        trainings = [
            Training(title="Python avance", category="technique", description="Decorateurs, metaclasses, asyncio, optimisation", duration_days=3, cost=1200, provider="FormaTech"),
            Training(title="Leadership et management", category="management", description="Techniques de leadership, gestion d'equipe, feedback constructif", duration_days=2, cost=900, provider="LeadAcademy"),
            Training(title="Securite informatique", category="technique", description="OWASP Top 10, securite des applications web, pentest basics", duration_days=2, cost=800, provider="CyberForm"),
            Training(title="Gestion du stress", category="bien-etre", description="Techniques de relaxation, gestion des priorites, equilibre vie pro/perso", duration_days=1, cost=400, provider="WellBeing Corp"),
            Training(title="Excel avance et Power BI", category="bureautique", description="Tableaux croises dynamiques, macros VBA, dashboards Power BI", duration_days=2, cost=700, provider="DataSkills"),
            Training(title="Anglais professionnel B2-C1", category="langues", description="Anglais des affaires, presentations, negociation", duration_days=5, cost=1500, provider="LangPro"),
            Training(title="Kubernetes et DevOps", category="technique", description="Conteneurs, orchestration, CI/CD, monitoring", duration_days=3, cost=1400, provider="CloudExpert"),
            Training(title="Droit du travail pour managers", category="juridique", description="Obligations legales, entretiens disciplinaires, rupture de contrat", duration_days=1, cost=500, provider="JuriFormation"),
        ]
        db.add_all(trainings)

        enrollments = [
            TrainingEnrollment(employee_id="EMP001", training_id=1, status="completed", completed_at=datetime(2026, 3, 15), budget_year=2026),
            TrainingEnrollment(employee_id="EMP004", training_id=7, status="enrolled", budget_year=2026),
            TrainingEnrollment(employee_id="EMP007", training_id=6, status="pending", budget_year=2026),
            TrainingEnrollment(employee_id="EMP008", training_id=2, status="completed", completed_at=datetime(2026, 2, 20), budget_year=2026),
        ]
        db.add_all(enrollments)

        training_budgets = [
            TrainingBudget(employee_id=eid, year=2026, total_budget=1500, used_budget=used)
            for eid, used in [("EMP001", 1200), ("EMP002", 0), ("EMP003", 500), ("EMP004", 0), ("EMP006", 0), ("EMP007", 0), ("EMP008", 900), ("EMP009", 0), ("EMP010", 0)]
        ]
        db.add_all(training_budgets)

        expenses = [
            Expense(employee_id="EMP001", category="repas", description="Dejeuner client", amount=45.50, receipt_date=date(2026, 5, 12), status="approved", approved_by="EMP003"),
            Expense(employee_id="EMP002", category="transport", description="Taxi salon professionnel", amount=38.00, receipt_date=date(2026, 5, 20), status="approved", approved_by="EMP003"),
            Expense(employee_id="EMP004", category="materiel", description="Cable HDMI teletravail", amount=15.99, receipt_date=date(2026, 6, 1), status="pending"),
            Expense(employee_id="EMP007", category="deplacement", description="Train Paris-Lyon conference", amount=89.00, receipt_date=date(2026, 6, 5), status="pending"),
            Expense(employee_id="EMP009", category="repas", description="Repas equipe", amount=120.00, receipt_date=date(2026, 5, 28), status="rejected", approved_by="EMP003"),
        ]
        db.add_all(expenses)

        job_openings = [
            JobOpening(title="Fullstack Developer", department="Engineering", description="Developpement d'applications web React/Python. 3 ans d'experience minimum.", contract_type="CDI", location="Paris", salary_range="42K-55K EUR", is_internal=True, is_open=True, hiring_manager_id="EMP001"),
            JobOpening(title="Data Analyst", department="Finance", description="Analyse de donnees financieres, creation de dashboards, reporting.", contract_type="CDI", location="Paris", salary_range="38K-48K EUR", is_internal=True, is_open=True, hiring_manager_id="EMP009"),
            JobOpening(title="Stagiaire Marketing Digital", department="Marketing", description="Stage de 6 mois en marketing digital. Community management, SEO, content.", contract_type="Stage", location="Paris", salary_range="1200 EUR/mois", is_internal=False, is_open=True, hiring_manager_id="EMP002"),
            JobOpening(title="Responsable Securite SI", department="Engineering", description="Definition et mise en oeuvre de la politique de securite. CISSP souhaite.", contract_type="CDI", location="Paris / Remote", salary_range="55K-70K EUR", is_internal=True, is_open=True, hiring_manager_id="EMP001"),
        ]
        db.add_all(job_openings)

        reviews = [
            PerformanceReview(employee_id="EMP001", reviewer_id=None, year=2025, rating=4, objectives="Livrer le projet API v2. Mentorer 2 juniors.", achievements="API v2 livree en avance. Mentorat de Lucas et Alexandre.", areas_of_improvement="Communication inter-equipes", comments="Excellente annee", status="completed", review_date=date(2026, 1, 15)),
            PerformanceReview(employee_id="EMP002", reviewer_id=None, year=2025, rating=3, objectives="Augmenter le trafic organique de 20%. Lancer 3 campagnes.", achievements="Trafic +15%. 4 campagnes lancees.", areas_of_improvement="Respect des budgets", comments="Bons resultats, marge de progression", status="completed", review_date=date(2026, 1, 20)),
            PerformanceReview(employee_id="EMP004", reviewer_id="EMP001", year=2025, rating=4, objectives="Mettre en place CI/CD. Reduire les incidents de 30%.", achievements="Pipeline CI/CD complet. Incidents -45%.", areas_of_improvement="Documentation", comments="Tres bon travail technique", status="completed", review_date=date(2026, 1, 18)),
            PerformanceReview(employee_id="EMP006", reviewer_id="EMP001", year=2025, rating=3, objectives="Monter en competence sur React. Contribuer a 5 features.", achievements="6 features livrees. React en progression.", areas_of_improvement="Tests unitaires, autonomie", comments="Bonne progression pour un junior", status="completed", review_date=date(2026, 1, 22)),
            PerformanceReview(employee_id="EMP001", reviewer_id=None, year=2026, rating=None, objectives="Migrer vers microservices. Recruter 2 developpeurs. Ameliorer le temps de reponse API de 40%.", achievements=None, areas_of_improvement=None, comments=None, status="draft", review_date=None),
        ]
        db.add_all(reviews)

        onboarding = [
            OnboardingChecklist(employee_id="EMP010", task="Signer le contrat de travail", category="administratif", is_completed=True, due_date=date(2025, 4, 1), completed_at=datetime(2025, 3, 28)),
            OnboardingChecklist(employee_id="EMP010", task="Recuperer le badge d'acces", category="administratif", is_completed=True, due_date=date(2025, 4, 1), completed_at=datetime(2025, 4, 1)),
            OnboardingChecklist(employee_id="EMP010", task="Configurer le poste de travail", category="technique", is_completed=True, due_date=date(2025, 4, 3), completed_at=datetime(2025, 4, 2)),
            OnboardingChecklist(employee_id="EMP010", task="Acceder aux outils (Slack, Jira, GitHub)", category="technique", is_completed=True, due_date=date(2025, 4, 3), completed_at=datetime(2025, 4, 2)),
            OnboardingChecklist(employee_id="EMP010", task="Formation securite informatique", category="formation", is_completed=True, due_date=date(2025, 4, 15), completed_at=datetime(2025, 4, 10)),
            OnboardingChecklist(employee_id="EMP010", task="Rencontre avec le manager (EMP001)", category="integration", is_completed=True, due_date=date(2025, 4, 1), completed_at=datetime(2025, 4, 1)),
            OnboardingChecklist(employee_id="EMP010", task="Rencontre avec l'equipe", category="integration", is_completed=True, due_date=date(2025, 4, 5), completed_at=datetime(2025, 4, 3)),
            OnboardingChecklist(employee_id="EMP010", task="Lire le reglement interieur", category="administratif", is_completed=False, due_date=date(2025, 4, 10)),
            OnboardingChecklist(employee_id="EMP010", task="Evaluation de fin de periode d'essai", category="rh", is_completed=False, due_date=date(2025, 10, 1)),
        ]
        db.add_all(onboarding)

        db.commit()
    finally:
        db.close()
