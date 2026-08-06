# ============================================================
# CodeWhisper PR - Security Scan Service
# ============================================================

import asyncio
import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.security_scan import SecurityScan
from loguru import logger


class SecurityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_dependency_audit(self, user_id: str) -> SecurityScan:
        scan = SecurityScan(user_id=user_id, status="running")
        self.db.add(scan)
        await self.db.commit()
        await self.db.refresh(scan)

        try:
            # Attempt to run pip-audit
            proc = await asyncio.create_subprocess_exec(
                "pip-audit", "-f", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                result = {"error": stderr.decode()}
                scan.status = "failed"
            else:
                result = json.loads(stdout.decode() or "[]")
                scan.status = "completed"

            scan.result = result
            self.db.add(scan)
            await self.db.commit()
            await self.db.refresh(scan)

        except FileNotFoundError:
            scan.status = "unavailable"
            scan.result = {"error": "pip-audit not installed"}
            self.db.add(scan)
            await self.db.commit()
            await self.db.refresh(scan)
        except Exception as e:
            logger.exception(e)
            scan.status = "error"
            scan.result = {"error": str(e)}
            self.db.add(scan)
            await self.db.commit()
            await self.db.refresh(scan)

        return scan
