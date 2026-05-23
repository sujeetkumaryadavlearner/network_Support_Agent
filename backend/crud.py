"""
CRUD operations and business logic for Ticket service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date
from datetime import datetime, timedelta
from typing import Optional
import random
import string

from backend.database import Ticket, TicketStatus, TicketPriority
from backend.schemas import TicketCreate, TicketUpdate, TicketStatusUpdate


def generate_ticket_number() -> str:
    """Generate a unique ticket number like NSA-20240522-XXXX."""
    date_str = datetime.utcnow().strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"NSA-{date_str}-{suffix}"


# ─── CREATE ────────────────────────────────────────────────────────

def create_ticket(db: Session, payload: TicketCreate) -> Ticket:
    ticket_number = generate_ticket_number()
    # Ensure uniqueness
    while db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first():
        ticket_number = generate_ticket_number()

    ticket = Ticket(
        ticket_number=ticket_number,
        employee_id=payload.employee_id,
        employee_name=payload.employee_name,
        department=payload.department,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
        category=payload.category,
        assigned_to=payload.assigned_to,
        notes=payload.notes,
        status=TicketStatus.OPEN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


# ─── READ ──────────────────────────────────────────────────────────

def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[Ticket]:
    return db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()


def get_tickets(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    department: Optional[str] = None,
    employee_id: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Ticket], int]:
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if department:
        query = query.filter(Ticket.department.ilike(f"%{department}%"))
    if employee_id:
        query = query.filter(Ticket.employee_id.ilike(f"%{employee_id}%"))
    if search:
        query = query.filter(
            (Ticket.subject.ilike(f"%{search}%")) |
            (Ticket.employee_name.ilike(f"%{search}%")) |
            (Ticket.ticket_number.ilike(f"%{search}%")) |
            (Ticket.description.ilike(f"%{search}%"))
        )

    total = query.count()
    tickets = (
        query.order_by(Ticket.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return tickets, total


# ─── UPDATE ────────────────────────────────────────────────────────

def update_ticket(db: Session, ticket_id: int, payload: TicketUpdate) -> Optional[Ticket]:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    # Auto-set resolved_at when resolving
    if "status" in update_data:
        if update_data["status"] == TicketStatus.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        elif update_data["status"] != TicketStatus.RESOLVED:
            ticket.resolved_at = None

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket_id: int, payload: TicketStatusUpdate) -> Optional[Ticket]:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return None

    ticket.status = payload.status
    if payload.notes:
        existing = ticket.notes or ""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        ticket.notes = f"{existing}\n[{timestamp}] {payload.notes}".strip()

    if payload.status == TicketStatus.RESOLVED and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    elif payload.status != TicketStatus.RESOLVED:
        ticket.resolved_at = None

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


# ─── DELETE ────────────────────────────────────────────────────────

def delete_ticket(db: Session, ticket_id: int) -> bool:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True


# ─── STATS ─────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    def count_by_status(s): return db.query(Ticket).filter(Ticket.status == s).count()
    def count_by_priority(p): return db.query(Ticket).filter(Ticket.priority == p).count()

    return {
        "total_tickets": db.query(Ticket).count(),
        "open_tickets": count_by_status(TicketStatus.OPEN),
        "in_progress_tickets": count_by_status(TicketStatus.IN_PROGRESS),
        "resolved_tickets": count_by_status(TicketStatus.RESOLVED),
        "closed_tickets": count_by_status(TicketStatus.CLOSED),
        "on_hold_tickets": count_by_status(TicketStatus.ON_HOLD),
        "critical_tickets": count_by_priority(TicketPriority.CRITICAL),
        "high_tickets": count_by_priority(TicketPriority.HIGH),
        "medium_tickets": count_by_priority(TicketPriority.MEDIUM),
        "low_tickets": count_by_priority(TicketPriority.LOW),
        "tickets_today": db.query(Ticket).filter(Ticket.created_at >= today_start).count(),
        "tickets_this_week": db.query(Ticket).filter(Ticket.created_at >= week_start).count(),
    }


def get_departments(db: Session) -> list[str]:
    rows = db.query(Ticket.department).distinct().all()
    return sorted([r[0] for r in rows])
