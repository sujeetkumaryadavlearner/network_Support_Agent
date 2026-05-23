"""
Database configuration and models for Network Support Ticket Dashboard
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, Enum as SAEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from datetime import datetime
import enum
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/Network_Support_Agent"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ON_HOLD = "on_hold"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum(TicketStatus, name="ticket_status_enum"),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )
    priority = Column(
        SAEnum(TicketPriority, name="ticket_priority_enum"),
        default=TicketPriority.MEDIUM,
        nullable=False
    )
    category = Column(String(100), nullable=True)
    assigned_to = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_tickets_employee_id", "employee_id"),
        Index("idx_tickets_status", "status"),
        Index("idx_tickets_department", "department"),
        Index("idx_tickets_created_at", "created_at"),
    )


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
