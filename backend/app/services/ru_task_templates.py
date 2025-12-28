"""
152-ФЗ Compliance Task Templates
Pre-defined tasks for Russian personal data protection compliance
"""

from datetime import date, timedelta

# Task templates for 152-ФЗ compliance
# Each template can be used to auto-generate tasks for a company

FZ152_TASK_TEMPLATES = [
    # === INITIAL SETUP TASKS (One-time) ===
    {
        "title": "Назначить ответственного за обработку ПДн",
        "title_en": "Appoint DPO (Data Protection Officer)",
        "description": "Издать приказ о назначении ответственного за организацию обработки персональных данных",
        "task_type": "appointment",
        "priority": "CRITICAL",
        "category": "initial_setup",
        "days_from_start": 0,
        "is_recurring": False,
    },
    {
        "title": "Определить состав обрабатываемых ПДн",
        "title_en": "Define processed personal data categories",
        "description": "Составить перечень персональных данных, обрабатываемых в организации",
        "task_type": "documentation",
        "priority": "CRITICAL",
        "category": "initial_setup",
        "days_from_start": 3,
        "is_recurring": False,
    },
    {
        "title": "Определить цели обработки ПДн",
        "title_en": "Define data processing purposes",
        "description": "Документировать цели обработки персональных данных для каждой категории субъектов",
        "task_type": "documentation",
        "priority": "HIGH",
        "category": "initial_setup",
        "days_from_start": 5,
        "is_recurring": False,
    },
    {
        "title": "Классифицировать ИСПДн",
        "title_en": "Classify personal data information systems",
        "description": "Провести классификацию информационных систем персональных данных и определить уровень защищенности (УЗ)",
        "task_type": "assessment",
        "priority": "CRITICAL",
        "category": "initial_setup",
        "days_from_start": 7,
        "is_recurring": False,
    },
    {
        "title": "Разработать модель угроз",
        "title_en": "Develop threat model",
        "description": "Разработать модель угроз безопасности персональных данных",
        "task_type": "documentation",
        "priority": "HIGH",
        "category": "initial_setup",
        "days_from_start": 10,
        "is_recurring": False,
    },
    {
        "title": "Утвердить Политику обработки ПДн",
        "title_en": "Approve Personal Data Processing Policy",
        "description": "Разработать и утвердить Политику в отношении обработки персональных данных",
        "task_type": "approval",
        "priority": "CRITICAL",
        "category": "initial_setup",
        "days_from_start": 14,
        "is_recurring": False,
    },
    {
        "title": "Опубликовать Политику на сайте",
        "title_en": "Publish Policy on website",
        "description": "Разместить Политику обработки ПДн на официальном сайте организации",
        "task_type": "implementation",
        "priority": "HIGH",
        "category": "initial_setup",
        "days_from_start": 15,
        "is_recurring": False,
    },
    {
        "title": "Уведомить Роскомнадзор",
        "title_en": "Notify Roskomnadzor",
        "description": "Подать уведомление об обработке персональных данных в Роскомнадзор",
        "task_type": "submission",
        "priority": "CRITICAL",
        "category": "initial_setup",
        "days_from_start": 20,
        "is_recurring": False,
    },
    {
        "title": "Получить согласия работников на обработку ПДн",
        "title_en": "Obtain employee consent",
        "description": "Собрать письменные согласия всех работников на обработку их персональных данных",
        "task_type": "consent",
        "priority": "HIGH",
        "category": "initial_setup",
        "days_from_start": 21,
        "is_recurring": False,
    },
    {
        "title": "Провести первичный инструктаж по ИБ",
        "title_en": "Conduct initial security training",
        "description": "Провести инструктаж работников по информационной безопасности и работе с ПДн",
        "task_type": "training",
        "priority": "HIGH",
        "category": "initial_setup",
        "days_from_start": 25,
        "is_recurring": False,
    },

    # === RECURRING TASKS ===
    {
        "title": "Ежегодный пересмотр Политики ПДн",
        "title_en": "Annual Policy Review",
        "description": "Провести ежегодный пересмотр и актуализацию Политики обработки персональных данных",
        "task_type": "review",
        "priority": "HIGH",
        "category": "recurring",
        "days_from_start": 365,
        "is_recurring": True,
        "recurrence_days": 365,
    },
    {
        "title": "Квартальный аудит ИСПДн",
        "title_en": "Quarterly ISPDN Audit",
        "description": "Провести внутренний аудит информационных систем персональных данных",
        "task_type": "audit",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 90,
        "is_recurring": True,
        "recurrence_days": 90,
    },
    {
        "title": "Ежемесячный мониторинг инцидентов ИБ",
        "title_en": "Monthly Security Incident Review",
        "description": "Проанализировать журнал инцидентов информационной безопасности за прошедший месяц",
        "task_type": "review",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 30,
        "is_recurring": True,
        "recurrence_days": 30,
    },
    {
        "title": "Ежегодное обучение работников по ИБ",
        "title_en": "Annual Security Training",
        "description": "Провести ежегодное обучение работников по информационной безопасности и защите ПДн",
        "task_type": "training",
        "priority": "HIGH",
        "category": "recurring",
        "days_from_start": 365,
        "is_recurring": True,
        "recurrence_days": 365,
    },
    {
        "title": "Полугодовой отчёт руководству",
        "title_en": "Semi-annual Management Report",
        "description": "Подготовить отчёт руководству о состоянии защиты персональных данных",
        "task_type": "reporting",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 180,
        "is_recurring": True,
        "recurrence_days": 180,
    },
    {
        "title": "Проверка актуальности согласий",
        "title_en": "Consent Validity Check",
        "description": "Проверить актуальность и срок действия согласий субъектов ПДн",
        "task_type": "review",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 180,
        "is_recurring": True,
        "recurrence_days": 180,
    },
    {
        "title": "Обновление реестра ИСПДн",
        "title_en": "Update ISPDN Registry",
        "description": "Актуализировать реестр информационных систем персональных данных",
        "task_type": "documentation",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 90,
        "is_recurring": True,
        "recurrence_days": 90,
    },

    # === DOCUMENT-RELATED TASKS ===
    {
        "title": "Актуализировать перечень лиц с доступом к ПДн",
        "title_en": "Update PD Access List",
        "description": "Обновить список лиц, имеющих доступ к персональным данным",
        "task_type": "documentation",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 30,
        "is_recurring": True,
        "recurrence_days": 30,
    },
    {
        "title": "Проверить журнал учёта носителей ПДн",
        "title_en": "Check PD Media Log",
        "description": "Проверить актуальность журнала учёта материальных носителей персональных данных",
        "task_type": "review",
        "priority": "LOW",
        "category": "recurring",
        "days_from_start": 30,
        "is_recurring": True,
        "recurrence_days": 30,
    },
    {
        "title": "Обновить информацию на сайте о ПДн",
        "title_en": "Update Website PD Information",
        "description": "Проверить и актуализировать информацию об обработке ПДн на сайте",
        "task_type": "review",
        "priority": "MEDIUM",
        "category": "recurring",
        "days_from_start": 90,
        "is_recurring": True,
        "recurrence_days": 90,
    },
]


def get_task_templates_for_company(start_date: date = None) -> list[dict]:
    """
    Generate task instances from templates with calculated due dates.

    Args:
        start_date: Base date for calculating due dates (default: today)

    Returns:
        List of task dictionaries ready to be created
    """
    if start_date is None:
        start_date = date.today()

    tasks = []
    for template in FZ152_TASK_TEMPLATES:
        task = {
            "title": template["title"],
            "description": template["description"],
            "task_type": template["task_type"],
            "priority": template["priority"],
            "due_date": start_date + timedelta(days=template["days_from_start"]),
            "is_recurring": template.get("is_recurring", False),
            "recurrence_days": template.get("recurrence_days"),
            "framework": "FZ_152",
        }
        tasks.append(task)

    return tasks


# Task type categories for UI filtering
TASK_CATEGORIES = {
    "initial_setup": "Первоначальная настройка",
    "recurring": "Регулярные задачи",
    "documentation": "Документация",
    "training": "Обучение",
    "audit": "Аудит",
    "assessment": "Оценка",
    "approval": "Согласование",
    "implementation": "Внедрение",
    "review": "Проверка",
    "submission": "Подача документов",
    "consent": "Согласия",
    "reporting": "Отчётность",
}

# Priority labels in Russian
PRIORITY_LABELS = {
    "CRITICAL": "Критический",
    "HIGH": "Высокий",
    "MEDIUM": "Средний",
    "LOW": "Низкий",
}
