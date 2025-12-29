"""
Celery Tasks for CORTEX-CI
"""

from app.workers import app
import structlog

logger = structlog.get_logger()


@app.task(bind=True, name="app.workers.tasks.sync_sanctions")
def sync_sanctions(self):
    """Sync sanctions data from external sources."""
    logger.info("Starting sanctions sync task")
    try:
        # TODO: Implement actual sync logic
        # This would call the sanctions sync service
        logger.info("Sanctions sync completed")
        return {"status": "success", "message": "Sanctions sync completed"}
    except Exception as e:
        logger.error("Sanctions sync failed", error=str(e))
        raise self.retry(exc=e, countdown=300, max_retries=3)


@app.task(bind=True, name="app.workers.tasks.recalculate_risks")
def recalculate_risks(self):
    """Recalculate risk scores for all entities."""
    logger.info("Starting risk recalculation task")
    try:
        # TODO: Implement actual risk calculation logic
        # This would call the risk calculation service
        logger.info("Risk recalculation completed")
        return {"status": "success", "message": "Risk recalculation completed"}
    except Exception as e:
        logger.error("Risk recalculation failed", error=str(e))
        raise self.retry(exc=e, countdown=60, max_retries=3)


@app.task(bind=True, name="app.workers.tasks.send_compliance_reminders")
def send_compliance_reminders(self):
    """Send compliance task reminders for upcoming deadlines."""
    import asyncio
    from app.core.database import async_session_maker

    logger.info("Starting compliance reminders task")

    async def _send():
        from app.services.notifications import NotificationScheduler

        async with async_session_maker() as db:
            scheduler = NotificationScheduler(db_session=db)
            result = await scheduler.send_deadline_reminders(
                days_before=[7, 3, 1],
                db=db,
            )
            return result

    try:
        result = asyncio.run(_send())
        logger.info("Compliance reminders sent", result=result)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Compliance reminders failed", error=str(e))
        raise self.retry(exc=e, countdown=60, max_retries=3)


@app.task(bind=True, name="app.workers.tasks.send_weekly_digest")
def send_weekly_digest(self):
    """Send weekly compliance digest to all users."""
    import asyncio
    from app.core.database import async_session_maker

    logger.info("Starting weekly digest task")

    async def _send():
        from app.services.notifications import NotificationScheduler

        async with async_session_maker() as db:
            scheduler = NotificationScheduler(db_session=db)
            result = await scheduler.send_weekly_digest(db=db)
            return result

    try:
        result = asyncio.run(_send())
        logger.info("Weekly digest sent", result=result)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Weekly digest failed", error=str(e))
        raise self.retry(exc=e, countdown=300, max_retries=3)


@app.task(bind=True, name="app.workers.tasks.send_document_expiry_alerts")
def send_document_expiry_alerts(self, days_before: int = 30):
    """Send alerts for documents expiring soon."""
    import asyncio
    from app.core.database import async_session_maker

    logger.info("Starting document expiry alerts task", days_before=days_before)

    async def _send():
        from app.services.notifications import NotificationScheduler

        async with async_session_maker() as db:
            scheduler = NotificationScheduler(db_session=db)
            result = await scheduler.send_document_expiry_alerts(
                days_before=days_before,
                db=db,
            )
            return result

    try:
        result = asyncio.run(_send())
        logger.info("Document expiry alerts sent", result=result)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Document expiry alerts failed", error=str(e))
        raise self.retry(exc=e, countdown=300, max_retries=3)


@app.task(name="app.workers.tasks.generate_document")
def generate_document(company_id: str, template_id: str):
    """Generate a compliance document from template."""
    logger.info("Generating document", company_id=company_id, template_id=template_id)
    try:
        # TODO: Implement document generation
        return {"status": "success", "company_id": company_id, "template_id": template_id}
    except Exception as e:
        logger.error("Document generation failed", error=str(e))
        raise


@app.task(name="app.workers.tasks.export_document")
def export_document(document_id: str, format: str = "docx"):
    """Export a document to specified format."""
    logger.info("Exporting document", document_id=document_id, format=format)
    try:
        # TODO: Implement document export
        return {"status": "success", "document_id": document_id, "format": format}
    except Exception as e:
        logger.error("Document export failed", error=str(e))
        raise


@app.task(bind=True, name="app.workers.tasks.sync_egrul_data")
def sync_egrul_data(self, inns: list[str] | None = None):
    """
    Sync EGRUL company data.

    If inns provided: Fetch specific companies
    Otherwise: Refresh stale entries (older than 7 days)
    """
    import asyncio
    from app.core.database import async_session_maker

    logger.info("Starting EGRUL sync task", inns=inns)

    async def _sync():
        from app.services.egrul_scraper import EGRULScraperService

        async with async_session_maker() as db:
            service = EGRULScraperService(db)

            if inns:
                # Fetch specific companies
                results = []
                for inn in inns:
                    company = await service.fetch_company_by_inn(inn)
                    results.append({
                        "inn": inn,
                        "success": company is not None,
                        "name": company.display_name if company else None,
                    })
                return {"status": "success", "fetched": results}
            else:
                # Mark old entries as stale and refresh
                stale_count = await service.mark_old_entries_stale(days=7)
                refreshed = await service.refresh_stale_companies(limit=50)
                return {
                    "status": "success",
                    "marked_stale": stale_count,
                    "refreshed": refreshed,
                }

    try:
        result = asyncio.run(_sync())
        logger.info("EGRUL sync completed", result=result)
        return result
    except Exception as e:
        logger.error("EGRUL sync failed", error=str(e))
        raise self.retry(exc=e, countdown=300, max_retries=3)


@app.task(bind=True, name="app.workers.tasks.fetch_company_by_inn")
def fetch_company_by_inn(self, inn: str, force_refresh: bool = False):
    """Fetch a single company by INN."""
    import asyncio
    from app.core.database import async_session_maker

    logger.info("Fetching company by INN", inn=inn)

    async def _fetch():
        from app.services.egrul_scraper import EGRULScraperService

        async with async_session_maker() as db:
            service = EGRULScraperService(db)
            company = await service.fetch_company_by_inn(inn, force_refresh=force_refresh)

            if company:
                return {
                    "status": "success",
                    "inn": company.inn,
                    "name": company.display_name,
                    "ogrn": company.ogrn,
                    "address": company.legal_address,
                }
            return {"status": "not_found", "inn": inn}

    try:
        result = asyncio.run(_fetch())
        logger.info("Company fetch completed", result=result)
        return result
    except Exception as e:
        logger.error("Company fetch failed", error=str(e), inn=inn)
        raise self.retry(exc=e, countdown=60, max_retries=3)
