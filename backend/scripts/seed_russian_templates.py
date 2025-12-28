#!/usr/bin/env python3
"""
Seed script for Russian compliance document templates.
Populates ru_document_templates and ru_email_templates tables.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.compliance.russian import RuDocumentTemplate, RuEmailTemplate
from app.services.russian_compliance import RU_EMAIL_TEMPLATES
from app.services.ru_templates_152fz import FZ152_DOCUMENT_TEMPLATES


async def seed_document_templates(session: AsyncSession) -> int:
    """Seed 152-FZ document templates from complete package."""
    count = 0

    for template_data in FZ152_DOCUMENT_TEMPLATES:
        # Check if template exists
        result = await session.execute(
            select(RuDocumentTemplate).where(
                RuDocumentTemplate.template_code == template_data["template_code"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  - Template {template_data['template_code']} already exists, skipping")
            continue

        # Create template
        template = RuDocumentTemplate(
            template_code=template_data["template_code"],
            title=template_data["title"],
            title_en=template_data.get("title_en"),
            document_type=template_data["document_type"],
            framework=template_data.get("framework", "152-ФЗ"),
            requirement_ref=template_data.get("requirement_ref"),
            description=template_data.get("description"),
            template_content=template_data.get("template_content", ""),
            form_fields=template_data.get("form_fields", []),
            category=template_data.get("category"),
            is_mandatory=template_data.get("is_mandatory", True),
            display_order=template_data.get("display_order", 0),
            applicable_uz=template_data.get("applicable_uz", ["УЗ-1", "УЗ-2", "УЗ-3", "УЗ-4"]),
            is_active=True,
        )

        session.add(template)
        count += 1
        print(f"  + Created template: {template_data['template_code']} - {template_data['title'][:50]}...")

    return count


async def seed_email_templates(session: AsyncSession) -> int:
    """Seed Russian email templates."""
    count = 0

    for template_data in RU_EMAIL_TEMPLATES:
        # Check if template exists
        result = await session.execute(
            select(RuEmailTemplate).where(
                RuEmailTemplate.template_code == template_data["template_code"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  - Email template {template_data['template_code']} already exists, skipping")
            continue

        # Create template
        template = RuEmailTemplate(
            template_code=template_data["template_code"],
            name=template_data["name"],
            category=template_data["category"],
            subject=template_data["subject"],
            body_text=template_data["body_text"],
            variables=template_data.get("variables", []),
            is_active=True,
        )

        session.add(template)
        count += 1
        print(f"  + Created email template: {template_data['template_code']} - {template_data['name']}")

    return count


async def main():
    """Main seed function."""
    print("=" * 60)
    print("Russian Compliance Template Seeder")
    print("=" * 60)

    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Seed document templates
            print("\n[1/2] Seeding 152-FZ document templates...")
            doc_count = await seed_document_templates(session)

            # Seed email templates
            print("\n[2/2] Seeding Russian email templates...")
            email_count = await seed_email_templates(session)

            # Commit
            await session.commit()

            print("\n" + "=" * 60)
            print(f"Seeding complete!")
            print(f"  - Document templates created: {doc_count}")
            print(f"  - Email templates created: {email_count}")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"\nError during seeding: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
