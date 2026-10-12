from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="open")
    severity: Mapped[int] = mapped_column(Integer, default=3)
    report: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    alerts: Mapped[list["Alert"]] = relationship(back_populates="incident")


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    signature: Mapped[str] = mapped_column(String(512))
    severity: Mapped[int] = mapped_column(Integer)
    src_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    dest_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="new")
    raw: Mapped[dict] = mapped_column(JSONB)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id"), nullable=True)
    incident: Mapped["Incident | None"] = relationship(back_populates="alerts")


class Event(Base):
    """Time-series table; becomes a TimescaleDB hypertable. PK must include the time column."""
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)
    src_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    dest_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    raw: Mapped[dict] = mapped_column(JSONB)


class IOC(Base):
    __tablename__ = "iocs"
    __table_args__ = (UniqueConstraint("type", "value"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(String(1024))
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    opencti_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AttackPattern(Base):
    __tablename__ = "attack_patterns"
    id: Mapped[int] = mapped_column(primary_key=True)
    mitre_id: Mapped[str | None] = mapped_column(String(16), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opencti_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
