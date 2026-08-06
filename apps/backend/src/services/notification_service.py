# ============================================================
# CodeWhisper PR - Notification Service
# ============================================================

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.notification import Notification


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_notification(self, user_id: str, notif_type: str, payload: Dict[str, Any]) -> Notification:
        n = Notification(user_id=user_id, type=notif_type, payload=payload)
        self.db.add(n)
        await self.db.commit()
        await self.db.refresh(n)
        return n
