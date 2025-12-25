"""
Pytest configuration and fixtures for CORTEX-CI tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.models import (
    User,
    Tenant,
    Entity,
    Dependency,
    DependencyLayer,
    EntityType,
    RelationshipType,
)
from app.core.security import get_password_hash


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_tenant(test_db: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        is_active=True,
    )
    test_db.add(tenant)
    await test_db.commit()
    await test_db.refresh(tenant)
    return tenant


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        role="admin",
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_entities(test_db: AsyncSession, test_tenant: Tenant) -> list[Entity]:
    """Create test entities for dependency testing."""
    entities = []
    for i in range(5):
        entity = Entity(
            id=uuid4(),
            tenant_id=test_tenant.id,
            type=EntityType.ORGANIZATION,
            name=f"Test Entity {i}",
            criticality=5,
            is_active=True,
        )
        test_db.add(entity)
        entities.append(entity)

    await test_db.commit()
    for e in entities:
        await test_db.refresh(e)
    return entities


@pytest_asyncio.fixture(scope="function")
async def test_dependencies(
    test_db: AsyncSession, test_tenant: Tenant, test_entities: list[Entity]
) -> list[Dependency]:
    """Create test dependencies across different layers."""
    dependencies = []
    layers = [
        DependencyLayer.LEGAL,
        DependencyLayer.FINANCIAL,
        DependencyLayer.OPERATIONAL,
        DependencyLayer.HUMAN,
        DependencyLayer.ACADEMIC,
    ]

    for i, layer in enumerate(layers):
        dep = Dependency(
            id=uuid4(),
            tenant_id=test_tenant.id,
            source_entity_id=test_entities[0].id,
            target_entity_id=test_entities[
                i + 1 if i + 1 < len(test_entities) else 1
            ].id,
            layer=layer,
            relationship_type=RelationshipType.DEPENDS_ON,
            criticality=5 + i,
            is_bidirectional=False,
            is_active=True,
        )
        test_db.add(dep)
        dependencies.append(dep)

    await test_db.commit()
    for d in dependencies:
        await test_db.refresh(d)
    return dependencies


@pytest_asyncio.fixture(scope="function")
async def test_app(test_db: AsyncSession) -> FastAPI:
    """Create a test FastAPI application."""
    from app.main import app

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest_asyncio.fixture(scope="function")
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
