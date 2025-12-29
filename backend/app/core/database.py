from collections.abc import AsyncGenerator
from uuid import uuid4

from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables and seed essential data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default tenant, admin user, and frameworks
    await _seed_default_data()


async def _seed_default_data() -> None:
    """Seed default tenant, admin user, and compliance frameworks."""
    # Import here to avoid circular imports
    from app.core.security import hash_password
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.compliance.framework import Framework, FrameworkType

    async with AsyncSessionLocal() as session:
        try:
            # Check if default tenant exists
            result = await session.execute(
                select(Tenant).where(Tenant.slug == "default")
            )
            tenant = result.scalar_one_or_none()

            if tenant is None:
                # Create default tenant
                tenant_id = uuid4()
                tenant = Tenant(
                    id=tenant_id,
                    name="Default Organization",
                    slug="default",
                    description="Default organization for Cortex GRC",
                    is_active=True,
                )
                session.add(tenant)

                # Create admin user
                admin = User(
                    id=uuid4(),
                    email="admin@cortex.local",
                    hashed_password=hash_password("admin123"),
                    full_name="System Administrator",
                    role="admin",
                    tenant_id=tenant_id,
                    is_active=True,
                    is_verified=True,
                )
                session.add(admin)

                # Create Russian compliance frameworks
                frameworks_data = [
                    {
                        "type": FrameworkType.FZ_152,
                        "name": "152-ФЗ",
                        "version": "2024",
                        "description": "Федеральный закон о персональных данных",
                        "publisher": "Государственная Дума РФ",
                    },
                    {
                        "type": FrameworkType.FZ_187,
                        "name": "187-ФЗ",
                        "version": "2024",
                        "description": "Федеральный закон о безопасности КИИ",
                        "publisher": "Государственная Дума РФ",
                    },
                    {
                        "type": FrameworkType.GOST_57580,
                        "name": "ГОСТ 57580",
                        "version": "2017",
                        "description": "Безопасность финансовых операций",
                        "publisher": "Росстандарт",
                    },
                    {
                        "type": FrameworkType.FSTEC_21,
                        "name": "ФСТЭК Приказ 21",
                        "version": "2013",
                        "description": "Меры защиты персональных данных",
                        "publisher": "ФСТЭК России",
                    },
                ]

                for fw_data in frameworks_data:
                    framework = Framework(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        is_active=True,
                        **fw_data,
                    )
                    session.add(framework)

                await session.commit()
                print("✓ Default tenant, admin user, and frameworks created successfully")
                print("  Login: admin@cortex.local / admin123")
            else:
                print("✓ Default data already exists, skipping seed")

        except Exception as e:
            await session.rollback()
            print(f"✗ Error seeding default data: {e}")
            raise
