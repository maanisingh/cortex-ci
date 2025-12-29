"""
Email Notification System
Uses standard SMTP (built-in Python smtplib) - no external services required.

Supports:
- Deadline reminders
- Task assignments
- Document approval requests
- Consent requests
- Training reminders
- Audit notifications
"""

import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Any
from jinja2 import Environment, BaseLoader

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel


# SMTP Configuration (environment variables)
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@cortex-grc.local")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Cortex GRC")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


class EmailMessage(BaseModel):
    to: list[str]
    cc: list[str] = []
    bcc: list[str] = []
    subject: str
    body_html: str
    body_text: str | None = None
    attachments: list[str] = []  # file paths


class NotificationRequest(BaseModel):
    notification_type: str
    recipients: list[str]
    data: dict[str, Any]


# Email Templates (Russian)
EMAIL_TEMPLATES = {
    "deadline_reminder": {
        "subject": "⚠️ Напоминание о сроке: {{task_title}}",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }
        .btn { display: inline-block; background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Напоминание о сроке</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <div class="warning">
                <strong>Задача:</strong> {{task_title}}<br>
                <strong>Срок выполнения:</strong> {{due_date}}<br>
                <strong>Осталось дней:</strong> {{days_remaining}}
            </div>

            <p>Пожалуйста, выполните задачу в установленный срок.</p>

            <p><a href="{{task_url}}" class="btn">Открыть задачу</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
        "body_text": """
Напоминание о сроке

Уважаемый(ая) {{recipient_name}},

Задача: {{task_title}}
Срок выполнения: {{due_date}}
Осталось дней: {{days_remaining}}

Пожалуйста, выполните задачу в установленный срок.

Ссылка на задачу: {{task_url}}
        """,
    },
    "task_assigned": {
        "subject": "📋 Вам назначена задача: {{task_title}}",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .task-info { background: white; border: 1px solid #e5e7eb; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Новая задача</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <p>Вам назначена новая задача:</p>

            <div class="task-info">
                <strong>Задача:</strong> {{task_title}}<br>
                <strong>Описание:</strong> {{task_description}}<br>
                <strong>Приоритет:</strong> {{priority}}<br>
                <strong>Срок выполнения:</strong> {{due_date}}<br>
                <strong>Назначил:</strong> {{assigned_by}}
            </div>

            <p><a href="{{task_url}}" class="btn">Открыть задачу</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "document_approval": {
        "subject": "📄 Требуется утверждение документа: {{document_title}}",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #059669; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .doc-info { background: white; border: 1px solid #e5e7eb; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #059669; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px; }
        .btn-reject { background: #dc2626; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Требуется утверждение</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <p>Документ ожидает вашего утверждения:</p>

            <div class="doc-info">
                <strong>Документ:</strong> {{document_title}}<br>
                <strong>Тип:</strong> {{document_type}}<br>
                <strong>Нормативный акт:</strong> {{framework}}<br>
                <strong>Подготовил:</strong> {{prepared_by}}<br>
                <strong>Дата:</strong> {{created_date}}
            </div>

            <p>
                <a href="{{approve_url}}" class="btn">Утвердить</a>
                <a href="{{reject_url}}" class="btn btn-reject">Отклонить</a>
            </p>

            <p><a href="{{document_url}}">Просмотреть документ</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "consent_request": {
        "subject": "✍️ Запрос на подписание согласия на обработку ПДн",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #7c3aed; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .info { background: #ede9fe; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #7c3aed; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Согласие на обработку персональных данных</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <p>В соответствии с требованиями Федерального закона от 27.07.2006 № 152-ФЗ «О персональных данных», просим вас подписать согласие на обработку персональных данных.</p>

            <div class="info">
                <strong>Организация:</strong> {{company_name}}<br>
                <strong>Цель обработки:</strong> {{processing_purpose}}<br>
                <strong>Срок действия согласия:</strong> {{validity_period}}
            </div>

            <p><a href="{{consent_url}}" class="btn">Подписать согласие</a></p>

            <p style="font-size: 12px; color: #6b7280;">
                Вы имеете право отказаться от подписания согласия. В этом случае обработка ваших персональных данных будет осуществляться только в случаях, предусмотренных законодательством.
            </p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "training_reminder": {
        "subject": "📚 Напоминание: необходимо пройти обучение",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #0891b2; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .course-info { background: white; border: 1px solid #e5e7eb; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #0891b2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Обучение по информационной безопасности</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <p>Напоминаем о необходимости пройти обязательное обучение:</p>

            <div class="course-info">
                <strong>Курс:</strong> {{course_title}}<br>
                <strong>Продолжительность:</strong> {{duration}} часов<br>
                <strong>Срок прохождения:</strong> до {{deadline}}<br>
                <strong>Статус:</strong> {{status}}
            </div>

            <p><a href="{{training_url}}" class="btn">Начать обучение</a></p>

            <p style="font-size: 12px; color: #6b7280;">
                Прохождение обучения является обязательным в соответствии с требованиями законодательства о защите информации.
            </p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "audit_notification": {
        "subject": "🔍 Уведомление о проведении аудита",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #ea580c; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .audit-info { background: #fff7ed; border-left: 4px solid #ea580c; padding: 15px; margin: 15px 0; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Уведомление о проведении аудита</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <p>Информируем вас о запланированном аудите:</p>

            <div class="audit-info">
                <strong>Тип аудита:</strong> {{audit_type}}<br>
                <strong>Нормативный акт:</strong> {{framework}}<br>
                <strong>Дата проведения:</strong> {{audit_date}}<br>
                <strong>Аудитор:</strong> {{auditor_name}}<br>
                <strong>Область проверки:</strong> {{scope}}
            </div>

            <p><strong>Подготовьте следующие документы:</strong></p>
            <ul>
                {% for doc in required_documents %}
                <li>{{doc}}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "document_expiry": {
        "subject": "📄 Срок действия документа истекает: {{document_title}}",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f59e0b; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }
        .btn { display: inline-block; background: #f59e0b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Срок действия документа истекает</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <div class="warning">
                <strong>Документ:</strong> {{document_title}}<br>
                <strong>Срок действия до:</strong> {{expiry_date}}<br>
                <strong>Осталось дней:</strong> {{days_remaining}}
            </div>

            <p>Пожалуйста, обновите или продлите документ до истечения срока.</p>

            <p><a href="{{document_url}}" class="btn">Открыть документ</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "weekly_digest": {
        "subject": "📊 Еженедельный отчет по комплаенсу ({{week_start}} - {{week_end}})",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .summary { background: white; border: 1px solid #e5e7eb; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .task-list { background: #f0f9ff; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Еженедельный отчет</h1>
            <p>{{week_start}} - {{week_end}}</p>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{recipient_name}},</p>

            <div class="summary">
                <h3>Ваши задачи на неделю</h3>
                <p>Всего задач: <strong>{{task_count}}</strong></p>
            </div>

            <div class="task-list">
                <h4>Предстоящие задачи:</h4>
                <pre>{{task_list}}</pre>
            </div>

            <p><a href="/compliance-tasks" class="btn">Открыть список задач</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
    "incident_alert": {
        "subject": "🚨 ВНИМАНИЕ: Зарегистрирован инцидент ИБ",
        "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #dc2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .alert { background: #fef2f2; border: 2px solid #dc2626; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .btn { display: inline-block; background: #dc2626; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ ИНЦИДЕНТ ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ</h1>
        </div>
        <div class="content">
            <div class="alert">
                <strong>Критичность:</strong> {{severity}}<br>
                <strong>Тип инцидента:</strong> {{incident_type}}<br>
                <strong>Время обнаружения:</strong> {{detected_at}}<br>
                <strong>Затронутые системы:</strong> {{affected_systems}}
            </div>

            <p><strong>Описание:</strong></p>
            <p>{{description}}</p>

            <p><strong>Требуемые действия:</strong></p>
            <ul>
                {% for action in required_actions %}
                <li>{{action}}</li>
                {% endfor %}
            </ul>

            <p><a href="{{incident_url}}" class="btn">Открыть карточку инцидента</a></p>
        </div>
        <div class="footer">
            <p>Cortex GRC — Система управления соответствием</p>
        </div>
    </div>
</body>
</html>
        """,
    },
}


class EmailService:
    """SMTP-based email service."""

    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())

    def send_email(self, message: EmailMessage) -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            msg["To"] = ", ".join(message.to)
            if message.cc:
                msg["Cc"] = ", ".join(message.cc)

            # Attach text part
            if message.body_text:
                text_part = MIMEText(message.body_text, "plain", "utf-8")
                msg.attach(text_part)

            # Attach HTML part
            html_part = MIMEText(message.body_html, "html", "utf-8")
            msg.attach(html_part)

            # Attach files
            for file_path in message.attachments:
                self._attach_file(msg, file_path)

            # Send email
            all_recipients = message.to + message.cc + message.bcc

            if SMTP_USE_TLS:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    server.starttls()
                    if SMTP_USER and SMTP_PASSWORD:
                        server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(SMTP_FROM_EMAIL, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    if SMTP_USER and SMTP_PASSWORD:
                        server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(SMTP_FROM_EMAIL, all_recipients, msg.as_string())

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach file to email."""
        path = Path(file_path)
        if not path.exists():
            return

        with open(path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={path.name}",
            )
            msg.attach(part)

    def send_notification(
        self,
        notification_type: str,
        recipients: list[str],
        data: dict[str, Any],
    ) -> bool:
        """Send notification using template."""
        template = EMAIL_TEMPLATES.get(notification_type)
        if not template:
            raise ValueError(f"Unknown notification type: {notification_type}")

        # Render subject
        subject_template = self.jinja_env.from_string(template["subject"])
        subject = subject_template.render(**data)

        # Render HTML body
        html_template = self.jinja_env.from_string(template["body_html"])
        body_html = html_template.render(**data)

        # Render text body if available
        body_text = None
        if "body_text" in template:
            text_template = self.jinja_env.from_string(template["body_text"])
            body_text = text_template.render(**data)

        message = EmailMessage(
            to=recipients,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
        )

        return self.send_email(message)


class NotificationScheduler:
    """Schedules and manages notifications."""

    def __init__(self, db_session=None):
        self.email_service = EmailService()
        self.db = db_session

    async def send_deadline_reminders(
        self,
        days_before: list[int] = [7, 3, 1],
        db=None,
    ) -> dict[str, int]:
        """
        Send reminders for upcoming task deadlines.

        Args:
            days_before: List of days before deadline to send reminders
            db: Database session

        Returns:
            Dict with count of reminders sent for each day threshold
        """
        from sqlalchemy import select, and_
        from app.models.compliance.russian import RuComplianceTask, TaskStatus
        from app.models.user import User

        if db is None and self.db is None:
            return {"error": "No database session provided"}

        session = db or self.db
        results = {}

        try:
            for days in days_before:
                target_date = datetime.now().date() + timedelta(days=days)

                # Find tasks due on target date that are not completed
                query = select(RuComplianceTask).where(
                    and_(
                        RuComplianceTask.due_date == target_date,
                        RuComplianceTask.status.notin_([
                            TaskStatus.COMPLETED,
                            TaskStatus.CANCELLED,
                        ]),
                    )
                )

                result = await session.execute(query)
                tasks = result.scalars().all()

                sent_count = 0
                for task in tasks:
                    # Get assigned user
                    if task.assigned_to:
                        user = await session.get(User, task.assigned_to)
                        if user and user.email:
                            success = self.email_service.send_notification(
                                "deadline_reminder",
                                [user.email],
                                {
                                    "recipient_name": user.full_name or user.email,
                                    "task_title": task.title,
                                    "due_date": target_date.strftime("%d.%m.%Y"),
                                    "days_remaining": days,
                                    "task_url": f"/compliance-tasks/{task.id}",
                                },
                            )
                            if success:
                                sent_count += 1

                results[f"days_{days}"] = sent_count

            return results

        except Exception as e:
            return {"error": str(e)}

    async def send_document_expiry_alerts(
        self,
        days_before: int = 30,
        db=None,
    ) -> dict[str, int]:
        """
        Send alerts for documents expiring soon.

        Args:
            days_before: Days before expiry to send alert
            db: Database session

        Returns:
            Dict with count of alerts sent
        """
        from sqlalchemy import select, and_
        from app.models.compliance.russian import RuComplianceDocument, DocumentStatus

        if db is None and self.db is None:
            return {"error": "No database session provided"}

        session = db or self.db
        target_date = datetime.now().date() + timedelta(days=days_before)

        try:
            # Find documents expiring around target date
            query = select(RuComplianceDocument).where(
                and_(
                    RuComplianceDocument.due_date <= target_date,
                    RuComplianceDocument.due_date >= datetime.now().date(),
                    RuComplianceDocument.status != DocumentStatus.APPROVED,
                )
            )

            result = await session.execute(query)
            documents = result.scalars().all()

            sent_count = 0
            for doc in documents:
                # Get responsible persons
                company = doc.company
                if company and hasattr(company, "responsible_persons"):
                    for person in company.responsible_persons:
                        if person.email:
                            days_left = (doc.due_date - datetime.now().date()).days
                            success = self.email_service.send_notification(
                                "document_expiry",
                                [person.email],
                                {
                                    "recipient_name": person.full_name,
                                    "document_title": doc.title,
                                    "expiry_date": doc.due_date.strftime("%d.%m.%Y"),
                                    "days_remaining": days_left,
                                    "document_url": f"/documents/{doc.id}",
                                },
                            )
                            if success:
                                sent_count += 1

            return {"alerts_sent": sent_count}

        except Exception as e:
            return {"error": str(e)}

    async def send_weekly_digest(self, db=None) -> dict[str, int]:
        """
        Send weekly compliance digest to all users.

        Returns:
            Dict with count of digests sent
        """
        from sqlalchemy import select, func
        from app.models.compliance.russian import RuComplianceTask, RuComplianceDocument, TaskStatus
        from app.models.user import User

        if db is None and self.db is None:
            return {"error": "No database session provided"}

        session = db or self.db

        try:
            # Get all active users
            users_query = select(User).where(User.is_active == True)
            users_result = await session.execute(users_query)
            users = users_result.scalars().all()

            sent_count = 0
            week_start = datetime.now().date()
            week_end = week_start + timedelta(days=7)

            for user in users:
                if not user.email:
                    continue

                # Get user's tasks due this week
                tasks_query = select(RuComplianceTask).where(
                    and_(
                        RuComplianceTask.assigned_to == user.id,
                        RuComplianceTask.due_date >= week_start,
                        RuComplianceTask.due_date <= week_end,
                        RuComplianceTask.status.notin_([
                            TaskStatus.COMPLETED,
                            TaskStatus.CANCELLED,
                        ]),
                    )
                )
                tasks_result = await session.execute(tasks_query)
                tasks = tasks_result.scalars().all()

                if not tasks:
                    continue

                task_list = [
                    f"- {t.title} (до {t.due_date.strftime('%d.%m.%Y')})"
                    for t in tasks
                ]

                success = self.email_service.send_notification(
                    "weekly_digest",
                    [user.email],
                    {
                        "recipient_name": user.full_name or user.email,
                        "week_start": week_start.strftime("%d.%m.%Y"),
                        "week_end": week_end.strftime("%d.%m.%Y"),
                        "task_count": len(tasks),
                        "task_list": "\n".join(task_list),
                    },
                )
                if success:
                    sent_count += 1

            return {"digests_sent": sent_count}

        except Exception as e:
            return {"error": str(e)}

    def send_training_reminders(self):
        """Send reminders for incomplete training."""
        # TODO: Implement when training module is fully integrated
        pass

    def send_consent_reminders(self):
        """Send reminders for unsigned consents."""
        # TODO: Implement when consent module is fully integrated
        pass


# API Router
router = APIRouter()
email_service = EmailService()
scheduler = NotificationScheduler()


@router.post("/send")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
):
    """Send notification."""
    try:
        # Send in background to not block response
        background_tasks.add_task(
            email_service.send_notification,
            request.notification_type,
            request.recipients,
            request.data,
        )
        return {"success": True, "message": "Notification queued"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-deadline-reminders")
async def send_deadline_reminders(background_tasks: BackgroundTasks):
    """Trigger deadline reminder emails."""
    background_tasks.add_task(scheduler.send_deadline_reminders)
    return {"success": True, "message": "Deadline reminders queued"}


@router.post("/send-training-reminders")
async def send_training_reminders(background_tasks: BackgroundTasks):
    """Trigger training reminder emails."""
    background_tasks.add_task(scheduler.send_training_reminders)
    return {"success": True, "message": "Training reminders queued"}


@router.get("/templates")
async def list_templates():
    """List available notification templates."""
    return {
        "templates": [
            {"type": key, "subject": val["subject"]}
            for key, val in EMAIL_TEMPLATES.items()
        ]
    }


@router.post("/test")
async def send_test_email(to: str, template: str = "deadline_reminder"):
    """Send test email to verify SMTP configuration."""
    test_data = {
        "recipient_name": "Тестовый пользователь",
        "task_title": "Тестовая задача",
        "due_date": "01.02.2024",
        "days_remaining": 3,
        "task_url": "https://example.com/tasks/1",
    }

    success = email_service.send_notification(template, [to], test_data)
    if success:
        return {"success": True, "message": f"Test email sent to {to}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email")
