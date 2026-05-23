"""
Ticket API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from backend.database import get_db, TicketStatus, TicketPriority
from backend.schemas import (
    TicketCreate, TicketUpdate, TicketStatusUpdate,
    TicketResponse, TicketListResponse, DashboardStats, APIResponse
)
from backend import crud

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


# ─── Dashboard Stats ────────────────────────────────────────────────

@router.get("/stats", response_model=DashboardStats, summary="Get dashboard statistics")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


# ─── List Departments ───────────────────────────────────────────────

@router.get("/departments", summary="Get list of all departments")
def get_departments(db: Session = Depends(get_db)):
    return {"departments": crud.get_departments(db)}


# ─── Create Ticket ──────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = crud.create_ticket(db, payload)
    return ticket


# ─── List Tickets ───────────────────────────────────────────────────

@router.get("/", response_model=TicketListResponse, summary="List all tickets with filters")
def list_tickets(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: Optional[TicketStatus] = Query(default=None),
    priority: Optional[TicketPriority] = Query(default=None),
    department: Optional[str] = Query(default=None),
    employee_id: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    tickets, total = crud.get_tickets(
        db, page=page, per_page=per_page,
        status=status, priority=priority,
        department=department, employee_id=employee_id,
        search=search,
    )
    return TicketListResponse(
        tickets=tickets,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=math.ceil(total / per_page) if total > 0 else 1,
    )


# ─── Get Single Ticket ──────────────────────────────────────────────

@router.get("/{ticket_id}", response_model=TicketResponse, summary="Get ticket by ID")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return ticket


@router.get("/number/{ticket_number}", response_model=TicketResponse, summary="Get ticket by ticket number")
def get_ticket_by_number(ticket_number: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket_by_number(db, ticket_number.upper())
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_number} not found")
    return ticket


# ─── Update Ticket ──────────────────────────────────────────────────

@router.put("/{ticket_id}", response_model=TicketResponse, summary="Update a ticket")
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = crud.update_ticket(db, ticket_id, payload)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse, summary="Update ticket status only")
def update_ticket_status(ticket_id: int, payload: TicketStatusUpdate, db: Session = Depends(get_db)):
    ticket = crud.update_ticket_status(db, ticket_id, payload)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return ticket


# ─── Delete Ticket ──────────────────────────────────────────────────

@router.delete("/{ticket_id}", response_model=APIResponse, summary="Delete a ticket")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return APIResponse(success=True, message=f"Ticket #{ticket_id} deleted successfully")
