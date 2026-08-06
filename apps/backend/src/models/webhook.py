# ============================================================
# CodeWhisper PR - Webhook Models
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class WebhookEndpoint(Base):
    """Stores registered webhook endpoints per organization/provider."""

    __tablename__ = "webhook_endpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)
    events = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    events_log = relationship("WebhookEvent", back_populates="endpoint", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="webhook_endpoints")

    def __repr__(self):
        return f"<WebhookEndpoint {self.provider} {self.url}>"


class WebhookEvent(Base):
    """Records incoming webhook deliveries."""

    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String(36), ForeignKey("webhook_endpoints.id"), nullable=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=True, index=True)
    payload = Column(JSON, nullable=False)
    signature_valid = Column(Boolean, default=False, nullable=False)
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True, index=True)

    endpoint = relationship("WebhookEndpoint", back_populates="events_log")

    def __repr__(self):
        return f"<WebhookEvent {self.provider}/{self.event_type} action={self.action}>"
