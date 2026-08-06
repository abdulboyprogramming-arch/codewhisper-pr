# ============================================================
# CodeWhisper PR - Organization Service
# ============================================================

from typing import Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.organization import Organization
from src.models.membership import OrganizationMembership
from src.models.team import Team


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, name: str, slug: str, domain: Optional[str], creator_id: str) -> Organization:
        org = Organization(id=str(uuid.uuid4()), name=name, slug=slug, domain=domain)
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)

        # create membership for creator as owner
        membership = OrganizationMembership(user_id=creator_id, organization_id=org.id, role="owner")
        self.db.add(membership)
        await self.db.commit()

        return org

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        result = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    async def list_organizations_for_user(self, user_id: str) -> List[Organization]:
        # join through memberships
        result = await self.db.execute(
            select(Organization).join(OrganizationMembership).where(OrganizationMembership.user_id == user_id)
        )
        return result.scalars().all()

    async def create_team(self, organization_id: str, name: str, slug: str, description: Optional[str] = None) -> Team:
        team = Team(organization_id=organization_id, name=name, slug=slug, description=description)
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def add_member_to_org(self, organization_id: str, user_id: str, role: str = "member") -> OrganizationMembership:
        membership = OrganizationMembership(user_id=user_id, organization_id=organization_id, role=role)
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership
