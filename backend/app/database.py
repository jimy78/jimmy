import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

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
    hire_date = Column(DateTime)
    is_active = Column(Boolean, default=True)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False, default=2026)
    total_days = Column(Integer, default=25)
    used_days = Column(Integer, default=0)
    sick_days_used = Column(Integer, default=0)


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    category = Column(String(100))
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


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
    """Insert demo data if tables are empty."""
    db = SessionLocal()
    try:
        if db.query(Employee).count() > 0:
            return

        employees = [
            Employee(employee_id="EMP001", name="Marie Dupont", department="Engineering", position="Senior Developer", email="m.dupont@company.fr", hire_date=datetime(2021, 3, 15), is_active=True),
            Employee(employee_id="EMP002", name="Jean Martin", department="Marketing", position="Marketing Manager", email="j.martin@company.fr", hire_date=datetime(2019, 7, 1), is_active=True),
            Employee(employee_id="EMP003", name="Sophie Leroy", department="HR", position="HR Specialist", email="s.leroy@company.fr", hire_date=datetime(2022, 1, 10), is_active=True),
            Employee(employee_id="EMP004", name="Pierre Bernard", department="Engineering", position="DevOps Engineer", email="p.bernard@company.fr", hire_date=datetime(2023, 6, 20), is_active=True),
            Employee(employee_id="EMP005", name="Claire Moreau", department="Finance", position="Accountant", email="c.moreau@company.fr", hire_date=datetime(2020, 11, 5), is_active=False),
        ]
        db.add_all(employees)

        balances = [
            LeaveBalance(employee_id="EMP001", year=2026, total_days=25, used_days=8, sick_days_used=2),
            LeaveBalance(employee_id="EMP002", year=2026, total_days=25, used_days=12, sick_days_used=1),
            LeaveBalance(employee_id="EMP003", year=2026, total_days=25, used_days=5, sick_days_used=0),
            LeaveBalance(employee_id="EMP004", year=2026, total_days=25, used_days=3, sick_days_used=3),
            LeaveBalance(employee_id="EMP005", year=2026, total_days=25, used_days=25, sick_days_used=5),
        ]
        db.add_all(balances)

        policies = [
            Policy(title="Politique de conges payes", category="conges", content="Chaque salarie a droit a 25 jours ouvrables de conges payes par an. Les conges doivent etre poses au moins 2 semaines a l'avance. Le report est autorise jusqu'au 31 mars de l'annee suivante (max 5 jours)."),
            Policy(title="Teletravail", category="teletravail", content="Le teletravail est autorise jusqu'a 3 jours par semaine. Une demande formelle doit etre soumise au manager. L'entreprise fournit l'equipement necessaire. Une indemnite de 2.70 EUR/jour est versee."),
            Policy(title="Arret maladie", category="maladie", content="En cas d'arret maladie, le salarie doit fournir un certificat medical sous 48h. Le maintien de salaire est assure a 100% pendant 90 jours, puis a 80% les 90 jours suivants."),
            Policy(title="Formation professionnelle", category="formation", content="Chaque salarie dispose d'un budget formation annuel de 1500 EUR. Les demandes sont soumises via le portail RH. Les formations doivent etre en lien avec le poste ou l'evolution professionnelle."),
        ]
        db.add_all(policies)

        db.commit()
    finally:
        db.close()
