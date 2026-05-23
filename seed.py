"""
Database initialization and optional seed data script.
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import init_db, SessionLocal
from backend.schemas import TicketCreate
from backend.crud import create_ticket


SAMPLE_TICKETS = [
    {
        "employee_id": "EMP-001",
        "employee_name": "Rohan Sharma",
        "department": "IT",
        "subject": "Unable to connect to VPN after system update",
        "description": "After the latest Windows update, I'm unable to connect to the company VPN. Error code: 800.",
        "priority": "high",
        "category": "Network Issue",
        "assigned_to": "Network Team",
    },
    {
        "employee_id": "EMP-042",
        "employee_name": "Priya Nair",
        "department": "Finance",
        "subject": "Excel macros not running — security policy blocked",
        "description": "The finance reporting macros stopped working after a Group Policy update. Need urgent resolution before month-end.",
        "priority": "critical",
        "category": "Software",
        "assigned_to": "Support Desk",
    },
    {
        "employee_id": "EMP-017",
        "employee_name": "Amit Patel",
        "department": "HR",
        "subject": "Password reset request for HRMS portal",
        "description": "Locked out of the HRMS portal. Please reset my account.",
        "priority": "medium",
        "category": "Access Request",
    },
    {
        "employee_id": "EMP-098",
        "employee_name": "Sneha Kulkarni",
        "department": "Engineering",
        "subject": "Shared drive inaccessible — permission denied",
        "description": "Cannot access the \\\\server\\projects shared drive. Was working fine last week.",
        "priority": "high",
        "category": "Access Request",
        "assigned_to": "Infra Team",
    },
    {
        "employee_id": "EMP-055",
        "employee_name": "Vikram Joshi",
        "department": "Sales",
        "subject": "CRM application throwing 500 error on login",
        "description": "Our Salesforce integration keeps throwing server errors when logging in from the office network.",
        "priority": "critical",
        "category": "Software",
    },
    {
        "employee_id": "EMP-031",
        "employee_name": "Deepa Menon",
        "department": "Marketing",
        "subject": "Printer on 3rd floor not responding",
        "description": "Canon MF4800 on the 3rd floor marketing area is not responding to print jobs.",
        "priority": "low",
        "category": "Hardware",
    },
    {
        "employee_id": "EMP-073",
        "employee_name": "Rahul Gupta",
        "department": "IT",
        "subject": "Email attachments blocked by spam filter",
        "description": "Legitimate PDF reports from vendor xyz.com are being blocked by the email gateway.",
        "priority": "medium",
        "category": "Email / Communication",
        "assigned_to": "Mail Admin",
    },
]


if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()

    seed = "--seed" in sys.argv or "-s" in sys.argv
    if seed:
        db = SessionLocal()
        print(f"🌱 Seeding {len(SAMPLE_TICKETS)} sample tickets...")
        for data in SAMPLE_TICKETS:
            ticket = create_ticket(db, TicketCreate(**data))
            print(f"   ✅ Created {ticket.ticket_number}: {ticket.subject[:50]}")
        db.close()
        print("\n✅ Seed complete!")
    else:
        print("✅ Database ready. Run with --seed to add sample data.")
        print("   python seed.py --seed")
