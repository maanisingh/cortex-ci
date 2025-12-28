"""Seed demo tenant and user."""
import asyncio
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import select
from app.core.database import async_session_maker
from app.core.security import hash_password
from app.models import User, Tenant


async def seed_demo():
    """Create demo tenant and user if not exists."""
    async with async_session_maker() as db:
        # Check if default tenant exists
        result = await db.execute(
            select(Tenant).where(Tenant.slug == "default")
        )
        tenant = result.scalar_one_or_none()

        if not tenant:
            tenant = Tenant(
                id=uuid4(),
                name="Demo Organization",
                slug="default",
                is_active=True,
                settings={
                    "features": ["compliance", "sanctions", "aml", "kyc"],
                    "modules": ["frameworks", "customers", "transactions", "cases"]
                },
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
            print(f"Created tenant: {tenant.name} ({tenant.slug})")
        else:
            print(f"Tenant exists: {tenant.name}")

        # Check if demo user exists
        result = await db.execute(
            select(User).where(
                User.email == "demo@cortex.ai",
                User.tenant_id == tenant.id
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=uuid4(),
                tenant_id=tenant.id,
                email="demo@cortex.ai",
                hashed_password=hash_password("demo1234"),
                full_name="Demo User",
                role="ADMIN",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(user)
            await db.commit()
            print(f"Created user: {user.email}")
        else:
            print(f"User exists: {user.email}")

        print("\n=== Demo Credentials ===")
        print("Email: demo@cortex.ai")
        print("Password: demo1234")
        print("Tenant: default")


if __name__ == "__main__":
    asyncio.run(seed_demo())
