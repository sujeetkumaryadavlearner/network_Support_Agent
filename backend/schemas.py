"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from backend.database import TicketStatus, TicketPriority


# ─── Request Schemas ───────────────────────────────────────────────

class TicketCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50, description="Employee ID")
    employee_name: str = Field(..., min_length=2, max_length=150, description="Full name of employee")
    department: str = Field(..., min_length=2, max_length=100, description="Department name")
    subject: str = Field(..., min_length=5, max_length=255, description="Brief subject of the ticket")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    category: Optional[str] = Field(None, max_length=100)
    assigned_to: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("employee_name", "department")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip()


class TicketUpdate(BaseModel):
    employee_name: Optional[str] = Field(None, min_length=2, max_length=150)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    subject: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = Field(None, max_length=100)
    assigned_to: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = Field(None, max_length=2000)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    notes: Optional[str] = Field(None, max_length=2000)


# ─── Response Schemas ──────────────────────────────────────────────

class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    employee_id: str
    employee_name: str
    department: str
    subject: str
    description: Optional[str]
    status: TicketStatus
    priority: TicketPriority
    category: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    notes: Optional[str]

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    on_hold_tickets: int
    critical_tickets: int
    high_tickets: int
    medium_tickets: int
    low_tickets: int
    tickets_today: int
    tickets_this_week: int


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
