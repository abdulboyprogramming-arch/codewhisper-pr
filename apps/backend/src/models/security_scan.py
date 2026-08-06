# ============================================================
# CodeWhisper PR - Security Scan Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, JSON

from src.core.database import Base


class SecurityScan(Base):
    __tablename__ = "security_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="pending")
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SecurityScan {self.id} status={self.status}>"
