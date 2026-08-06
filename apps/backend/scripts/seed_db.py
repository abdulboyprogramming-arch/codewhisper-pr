#!/usr/bin/env python3
"""Database seed script for CodeWhisper PR."""

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import async_session_factory
from src.models.user import User
from src.models.review import Review
from src.models.token_usage import TokenUsage
from src.models.repository import Repository
from src.models.analytics import Analytics
from src.core.exceptions import DatabaseError


async def create_user(
    session: AsyncSession,
    email: str,
    username: str,
    password: str = "password123",
    full_name: str = None,
) -> User:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        username=username,
        full_name=full_name or username,
        hashed_password=pwd_context.hash(password),
        role="user",
        is_active=True,
        is_verified=True,
        total_tokens_saved=0,
        total_reviews_count=0,
    )
    session.add(user)
    await session.flush()
    return user


async def create_repository(
    session: AsyncSession,
    user_id: str,
    name: str = "test-repo",
    url: str = "https://github.com/test/test-repo",
) -> Repository:
    repo = Repository(
        id=str(uuid.uuid4()),
        user_id=user_id,
        url=url,
        name=name,
        full_name=f"test/{name}",
        default_branch="main",
        is_private=False,
    )
    session.add(repo)
    await session.flush()
    return repo


async def create_review(
    session: AsyncSession,
    user_id: str,
    repo_url: str,
    pr_number: int = 1,
    status: str = "completed",
) -> Review:
    review = Review(
        id=str(uuid.uuid4()),
        user_id=user_id,
        repository_url=repo_url,
        repository_name="test-repo",
        pr_number=pr_number,
        pr_title=f"Test PR #{pr_number}",
        status=status,
        original_tokens=15000,
        optimized_tokens=3900,
        tokens_saved_percentage=74.0,
        optimization_time_ms=245,
        review_output={
            "summary": "Code looks good with minor improvements needed.",
            "issues": [
                {
                    "id": "1",
                    "severity": "low",
                    "category": "style",
                    "title": "Style improvement",
                    "description": "Consider adding type hints",
                    "file_path": "test.py",
                    "line_numbers": [2],
                    "suggestion": "Add type hints",
                }
            ],
            "suggestions": ["Add documentation", "Use type hints"],
            "overall_assessment": "approved",
        },
        summary="Minor improvements needed",
        issues_found=[
            {
                "id": "1",
                "severity": "low",
                "category": "style",
                "title": "Style improvement",
                "description": "Consider adding type hints",
                "file_path": "test.py",
                "line_numbers": [2],
                "suggestion": "Add type hints",
            }
        ],
        model_used="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=4000,
        completed_at=datetime.utcnow(),
    )
    session.add(review)
    await session.flush()

    token_usage = TokenUsage(
        id=str(uuid.uuid4()),
        user_id=user_id,
        review_id=review.id,
        original_tokens=15000,
        optimized_tokens=3900,
        tokens_saved=11100,
        savings_percentage=74.0,
        model_used="gpt-4-turbo-preview",
        cost_saved=0.033,
    )
    session.add(token_usage)
    await session.flush()

    return review


async def create_analytics(
    session: AsyncSession,
    user_id: str,
    period: str = "daily",
) -> Analytics:
    analytics = Analytics(
        id=str(uuid.uuid4()),
        user_id=user_id,
        period=period,
        total_reviews=10,
        total_tokens_saved=111000,
        total_original_tokens=150000,
        total_optimized_tokens=39000,
        average_savings_percentage=74.0,
        total_cost_saved=0.33,
        date_range={"start": datetime.utcnow() - timedelta(days=1), "end": datetime.utcnow()},
        generated_at=datetime.utcnow(),
    )
    session.add(analytics)
    await session.flush()
    return analytics


async def seed_database():
    print("Seeding database...")

    async with async_session_factory() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        print("Creating test users...")
        user1 = await create_user(session, "test1@example.com", "testuser1", full_name="Test User 1")
        user2 = await create_user(session, "test2@example.com", "testuser2", full_name="Test User 2")

        print("Creating repositories...")
        repo1 = await create_repository(session, user1.id)
        repo2 = await create_repository(session, user2.id, name="another-project")

        print("Creating reviews...")
        for i in range(1, 6):
            await create_review(session, user1.id, repo1.url, pr_number=i)
        for i in range(1, 4):
            await create_review(session, user2.id, repo2.url, pr_number=i)

        print("Creating analytics...")
        await create_analytics(session, user1.id, "daily")
        await create_analytics(session, user1.id, "weekly")
        await create_analytics(session, user2.id, "daily")

        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
