# ============================================================
# CodeWhisper PR - Notification Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=True, index=True)
    type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
    review = relationship("Review", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.type} for {self.user_id}>"
# ============================================================
# CodeWhisper PR - Notification Model
# ============================================================

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class Notification(Base):
    """A notification delivered to a user (e.g. review completion)."""

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=True, index=True)

    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="review")
    data = Column(JSON, nullable=True)

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    delivered = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True, index=True)

    user = relationship("User", foreign_keys=[user_id])
    review = relationship("Review", foreign_keys=[review_id])

    def __repr__(self):
        return f"<Notification {self.category} unread={not self.is_read}>"
