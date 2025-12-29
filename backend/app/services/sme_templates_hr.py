"""
Phase 8: HR & Employment Document Templates
20 templates for full employee lifecycle management.
"""

from typing import Dict, List, Any

HR_TEMPLATES = {
    # =========================================================================
    # EMPLOYMENT CONTRACTS
    # =========================================================================

    "employment_contract": {
        "id": "employment_contract",
        "name": "Трудовой договор",
        "name_en": "Employment Contract",
        "category": "hr",
        "subcategory": "contracts",
        "description": "Стандартный трудовой договор с работником",
        "required_fields": [
            {"name": "company_name", "label": "Наименование работодателя", "type": "text", "required": True},
            {"name": "company_inn", "label": "ИНН работодателя", "type": "text", "required": True},
            {"name": "company_address", "label": "Адрес работодателя", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "employee_passport", "label": "Паспорт работника", "type": "text", "required": True},
            {"name": "employee_address", "label": "Адрес работника", "type": "text", "required": True},
            {"name": "employee_inn", "label": "ИНН работника", "type": "text", "required": False},
            {"name": "employee_snils", "label": "СНИЛС работника", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "department", "label": "Подразделение", "type": "text", "required": False},
            {"name": "start_date", "label": "Дата начала работы", "type": "date", "required": True},
            {"name": "contract_type", "label": "Тип договора", "type": "select", "options": ["Бессрочный", "Срочный"], "required": True},
            {"name": "end_date", "label": "Дата окончания (для срочного)", "type": "date", "required": False},
            {"name": "probation_months", "label": "Испытательный срок (мес.)", "type": "number", "required": False},
            {"name": "salary", "label": "Оклад (руб.)", "type": "number", "required": True},
            {"name": "work_schedule", "label": "Режим работы", "type": "text", "required": True},
            {"name": "vacation_days", "label": "Отпуск (дней)", "type": "number", "required": True, "default": 28},
        ],
        "template_content": """
ТРУДОВОЙ ДОГОВОР № ___

г. Москва                                                     «{{start_date|format_date}}»

{{company_name}}, ИНН {{company_inn}}, в лице Генерального директора {{director_name}}, действующего на основании Устава, именуемое в дальнейшем «Работодатель», с одной стороны, и

{{employee_name}}, паспорт {{employee_passport}}, СНИЛС {{employee_snils}}, проживающий(ая) по адресу: {{employee_address}}, именуемый(ая) в дальнейшем «Работник», с другой стороны,

заключили настоящий трудовой договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Работник принимается на работу в {{company_name}} на должность {{position}}{% if department %} в {{department}}{% endif %}.

1.2. Настоящий договор является договором по основному месту работы.

1.3. Дата начала работы: «{{start_date|format_date}}».

{% if contract_type == "Срочный" %}
1.4. Настоящий договор заключен на определенный срок до «{{end_date|format_date}}».
{% else %}
1.4. Настоящий договор заключен на неопределенный срок.
{% endif %}

{% if probation_months %}
1.5. Работнику устанавливается испытательный срок продолжительностью {{probation_months}} месяца(ев).
{% endif %}

2. ПРАВА И ОБЯЗАННОСТИ РАБОТНИКА

2.1. Работник имеет право на:
- предоставление работы, обусловленной настоящим договором;
- рабочее место, соответствующее требованиям охраны труда;
- своевременную и в полном объеме выплату заработной платы;
- отдых, обеспечиваемый установлением нормальной продолжительности рабочего времени;
- обязательное социальное страхование.

2.2. Работник обязан:
- добросовестно исполнять трудовые обязанности;
- соблюдать правила внутреннего трудового распорядка;
- соблюдать трудовую дисциплину;
- выполнять установленные нормы труда;
- соблюдать требования охраны труда;
- бережно относиться к имуществу Работодателя.

3. ПРАВА И ОБЯЗАННОСТИ РАБОТОДАТЕЛЯ

3.1. Работодатель имеет право:
- требовать от Работника исполнения трудовых обязанностей;
- привлекать Работника к дисциплинарной ответственности;
- поощрять Работника за добросовестный труд.

3.2. Работодатель обязан:
- предоставить Работнику работу по настоящему договору;
- обеспечить безопасные условия труда;
- выплачивать заработную плату в установленные сроки;
- осуществлять обязательное социальное страхование.

4. ОПЛАТА ТРУДА

4.1. Работнику устанавливается должностной оклад в размере {{salary}} ({{salary_words}}) рублей в месяц.

4.2. Заработная плата выплачивается два раза в месяц: 25 числа текущего месяца (аванс) и 10 числа следующего месяца (окончательный расчет).

4.3. Заработная плата перечисляется на банковскую карту Работника.

5. РАБОЧЕЕ ВРЕМЯ И ВРЕМЯ ОТДЫХА

5.1. Работнику устанавливается {{work_schedule}}.

5.2. Работнику предоставляется ежегодный оплачиваемый отпуск продолжительностью {{vacation_days}} календарных дней.

6. СОЦИАЛЬНОЕ СТРАХОВАНИЕ

6.1. Работник подлежит обязательному социальному страхованию в соответствии с законодательством РФ.

7. ОТВЕТСТВЕННОСТЬ СТОРОН

7.1. Стороны несут ответственность за неисполнение обязательств в соответствии с законодательством РФ.

8. ИЗМЕНЕНИЕ И ПРЕКРАЩЕНИЕ ДОГОВОРА

8.1. Изменение условий договора допускается по соглашению сторон.

8.2. Договор может быть прекращен по основаниям, предусмотренным ТК РФ.

9. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

9.1. Настоящий договор составлен в двух экземплярах, имеющих одинаковую юридическую силу.

9.2. Споры разрешаются путем переговоров или в судебном порядке.

РЕКВИЗИТЫ И ПОДПИСИ СТОРОН:

РАБОТОДАТЕЛЬ:                              РАБОТНИК:
{{company_name}}                           {{employee_name}}
ИНН {{company_inn}}                        Паспорт {{employee_passport}}
Адрес: {{company_address}}                 СНИЛС {{employee_snils}}
                                           Адрес: {{employee_address}}

___________________/{{director_name}}/     ___________________/{{employee_name}}/

Экземпляр трудового договора получил(а): ___________________/{{employee_name}}/
Дата: «___» ___________ 20___ г.
        """,
        "workflow": ["generate", "sign_both", "register_hr", "archive"],
        "output_format": "docx"
    },

    "contractor_agreement": {
        "id": "contractor_agreement",
        "name": "Договор ГПХ (гражданско-правовой)",
        "name_en": "Civil Contract (GPC Agreement)",
        "category": "hr",
        "subcategory": "contracts",
        "description": "Договор гражданско-правового характера на оказание услуг",
        "required_fields": [
            {"name": "company_name", "label": "Наименование заказчика", "type": "text", "required": True},
            {"name": "contractor_name", "label": "ФИО исполнителя", "type": "text", "required": True},
            {"name": "contractor_passport", "label": "Паспорт исполнителя", "type": "text", "required": True},
            {"name": "contractor_inn", "label": "ИНН исполнителя", "type": "text", "required": False},
            {"name": "services_description", "label": "Описание услуг", "type": "textarea", "required": True},
            {"name": "contract_amount", "label": "Сумма договора", "type": "number", "required": True},
            {"name": "start_date", "label": "Дата начала", "type": "date", "required": True},
            {"name": "end_date", "label": "Дата окончания", "type": "date", "required": True},
        ],
        "template_content": """
ДОГОВОР
на оказание услуг № ___

г. Москва                                                     «{{start_date|format_date}}»

{{company_name}}, именуемое в дальнейшем «Заказчик», в лице Генерального директора, действующего на основании Устава, с одной стороны, и

{{contractor_name}}, паспорт {{contractor_passport}}{% if contractor_inn %}, ИНН {{contractor_inn}}{% endif %}, именуемый(ая) в дальнейшем «Исполнитель», с другой стороны,

заключили настоящий Договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Исполнитель обязуется оказать Заказчику следующие услуги:
{{services_description}}

1.2. Срок оказания услуг: с «{{start_date|format_date}}» по «{{end_date|format_date}}».

2. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЕТОВ

2.1. Стоимость услуг составляет {{contract_amount}} ({{contract_amount_words}}) рублей.

2.2. Оплата производится после подписания акта оказанных услуг в течение 5 рабочих дней.

2.3. Заказчик удерживает НДФЛ в соответствии с законодательством РФ.

3. ОБЯЗАННОСТИ СТОРОН

3.1. Исполнитель обязан:
- оказать услуги качественно и в срок;
- предоставить отчет о выполненной работе.

3.2. Заказчик обязан:
- обеспечить необходимые условия для оказания услуг;
- принять и оплатить услуги.

4. СДАЧА-ПРИЕМКА УСЛУГ

4.1. По завершении оказания услуг составляется акт оказанных услуг.

4.2. Заказчик обязан рассмотреть акт в течение 5 рабочих дней.

5. ОТВЕТСТВЕННОСТЬ СТОРОН

5.1. За неисполнение обязательств стороны несут ответственность в соответствии с законодательством РФ.

6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

6.1. Договор составлен в двух экземплярах.

6.2. Споры разрешаются путем переговоров или в судебном порядке.

ПОДПИСИ СТОРОН:

ЗАКАЗЧИК:                                  ИСПОЛНИТЕЛЬ:
{{company_name}}                           {{contractor_name}}

_____________________                      _____________________
        """,
        "workflow": ["generate", "sign_both", "track_execution", "sign_act", "pay"],
        "output_format": "docx"
    },

    "self_employed_contract": {
        "id": "self_employed_contract",
        "name": "Договор с самозанятым",
        "name_en": "Self-Employed Contract",
        "category": "hr",
        "subcategory": "contracts",
        "description": "Договор на оказание услуг с плательщиком НПД",
        "required_fields": [
            {"name": "company_name", "label": "Наименование заказчика", "type": "text", "required": True},
            {"name": "self_employed_name", "label": "ФИО самозанятого", "type": "text", "required": True},
            {"name": "self_employed_inn", "label": "ИНН самозанятого", "type": "text", "required": True},
            {"name": "services_description", "label": "Описание услуг", "type": "textarea", "required": True},
            {"name": "contract_amount", "label": "Сумма договора", "type": "number", "required": True},
        ],
        "template_content": """
ДОГОВОР
на оказание услуг с самозанятым № ___

Настоящий договор заключен между {{company_name}} («Заказчик») и {{self_employed_name}}, ИНН {{self_employed_inn}}, являющимся плательщиком налога на профессиональный доход («Исполнитель»).

1. ПРЕДМЕТ ДОГОВОРА
Исполнитель обязуется оказать услуги: {{services_description}}

2. СТОИМОСТЬ: {{contract_amount}} рублей.

3. ОСОБЫЕ УСЛОВИЯ
3.1. Исполнитель подтверждает статус плательщика НПД.
3.2. Исполнитель самостоятельно уплачивает налог на профессиональный доход.
3.3. Исполнитель обязан предоставить чек из приложения «Мой налог».

ПОДПИСИ СТОРОН:
_____________________                      _____________________
        """,
        "workflow": ["generate", "verify_npd_status", "sign_both", "receive_check", "pay"],
        "output_format": "docx"
    },

    # =========================================================================
    # HIRING ORDERS
    # =========================================================================

    "hiring_order": {
        "id": "hiring_order",
        "name": "Приказ о приеме на работу (Т-1)",
        "name_en": "Hiring Order",
        "category": "hr",
        "subcategory": "orders",
        "description": "Унифицированная форма Т-1 приказа о приеме на работу",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "order_number", "label": "Номер приказа", "type": "text", "required": True},
            {"name": "order_date", "label": "Дата приказа", "type": "date", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "employee_tab_number", "label": "Табельный номер", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "department", "label": "Структурное подразделение", "type": "text", "required": False},
            {"name": "start_date", "label": "Дата приема", "type": "date", "required": True},
            {"name": "end_date", "label": "По (для срочного)", "type": "date", "required": False},
            {"name": "probation_period", "label": "Испытательный срок", "type": "text", "required": False},
            {"name": "salary", "label": "Оклад", "type": "number", "required": True},
            {"name": "allowance", "label": "Надбавка", "type": "number", "required": False},
            {"name": "contract_number", "label": "№ трудового договора", "type": "text", "required": True},
            {"name": "contract_date", "label": "Дата трудового договора", "type": "date", "required": True},
            {"name": "director_name", "label": "ФИО руководителя", "type": "text", "required": True},
        ],
        "template_content": """
                                                           Унифицированная форма № Т-1
                                                           Утверждена Постановлением Госкомстата
                                                           России от 05.01.2004 № 1

{{company_name}}
─────────────────────────────────────────────────────
                    наименование организации

                                                           ОКПО ____________

                                                           Номер документа    Дата составления
                                                           ─────────────────  ─────────────────
                                                              {{order_number}}     {{order_date|format_date}}

                              ПРИКАЗ
                     (распоряжение)
               о приеме работника на работу

                                                           Дата
                                              Принять на работу    с    {{start_date|format_date}}
                                                                   по   {{end_date|format_date if end_date else "────────────"}}

                                                           Табельный номер
{{employee_name}}                                          {{employee_tab_number}}
─────────────────────────────────────────────────────
                    фамилия, имя, отчество

в ___________________________________________________________________________
            структурное подразделение
{{department if department else "────────────────────────────────"}}

{{position}}
─────────────────────────────────────────────────────
             должность (специальность, профессия), разряд, класс (категория) квалификации

условия приема на работу, характер работы: _________________________________
                                           (по совместительству, в порядке перевода и др.)

с тарифной ставкой (окладом) {{salary}} руб. 00 коп.
                              ─────────────────────
надбавкой {{allowance if allowance else "────"}} руб. 00 коп.
          ─────────────────────

с испытанием на срок {{probation_period if probation_period else "────────────"}} месяца(ев)

Основание: Трудовой договор от «{{contract_date|format_date}}» № {{contract_number}}

Руководитель организации _________________ {{director_name}}
                          подпись             расшифровка подписи

С приказом (распоряжением) работник ознакомлен _________________ «___»________ 20__ г.
                                                   подпись
        """,
        "workflow": ["generate", "sign_director", "employee_acknowledge", "register_hr", "archive"],
        "output_format": "docx"
    },

    "termination_order": {
        "id": "termination_order",
        "name": "Приказ об увольнении (Т-8)",
        "name_en": "Termination Order",
        "category": "hr",
        "subcategory": "orders",
        "description": "Унифицированная форма Т-8 приказа об увольнении",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "order_number", "label": "Номер приказа", "type": "text", "required": True},
            {"name": "order_date", "label": "Дата приказа", "type": "date", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "employee_tab_number", "label": "Табельный номер", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "department", "label": "Структурное подразделение", "type": "text", "required": False},
            {"name": "termination_date", "label": "Дата увольнения", "type": "date", "required": True},
            {"name": "termination_reason", "label": "Основание увольнения", "type": "text", "required": True},
            {"name": "termination_article", "label": "Статья ТК РФ", "type": "text", "required": True},
            {"name": "basis_document", "label": "Документ-основание", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО руководителя", "type": "text", "required": True},
        ],
        "template_content": """
                                                           Унифицированная форма № Т-8
{{company_name}}

                                                           Номер документа    Дата составления
                                                              {{order_number}}     {{order_date|format_date}}

                              ПРИКАЗ
                     (распоряжение)
           о прекращении (расторжении) трудового
            договора с работником (увольнении)

Прекратить действие трудового договора от «___» _________ 20__ г. № ______,
уволить «{{termination_date|format_date}}»

                                                           Табельный номер
{{employee_name}}                                          {{employee_tab_number}}
─────────────────────────────────────────────────────
                    фамилия, имя, отчество

{{department}}
─────────────────────────────────────────────────────
            структурное подразделение

{{position}}
─────────────────────────────────────────────────────
             должность (специальность, профессия), разряд, класс (категория)

{{termination_reason}}, {{termination_article}}
─────────────────────────────────────────────────────
            основание прекращения (расторжения) трудового договора (увольнения)

Основание (документ, номер, дата): {{basis_document}}
─────────────────────────────────────────────────────

Руководитель организации _________________ {{director_name}}
                          подпись             расшифровка подписи

С приказом (распоряжением) работник ознакомлен _________________ «___»________ 20__ г.
                                                   подпись
        """,
        "workflow": ["generate", "sign_director", "employee_acknowledge", "calculate_final_pay", "issue_documents", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # LEAVE MANAGEMENT
    # =========================================================================

    "leave_request": {
        "id": "leave_request",
        "name": "Заявление на отпуск",
        "name_en": "Leave Request",
        "category": "hr",
        "subcategory": "leave",
        "description": "Заявление работника на предоставление отпуска",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "leave_type", "label": "Вид отпуска", "type": "select", "options": ["Ежегодный оплачиваемый", "Без сохранения заработной платы", "Учебный", "По беременности и родам", "По уходу за ребенком"], "required": True},
            {"name": "start_date", "label": "Дата начала", "type": "date", "required": True},
            {"name": "end_date", "label": "Дата окончания", "type": "date", "required": True},
            {"name": "days_count", "label": "Количество дней", "type": "number", "required": True},
            {"name": "request_date", "label": "Дата заявления", "type": "date", "required": True},
        ],
        "template_content": """
                                                Генеральному директору
                                                {{company_name}}
                                                {{director_name}}

                                                от {{position}}
                                                {{employee_name}}

                              ЗАЯВЛЕНИЕ

Прошу предоставить мне {{leave_type}} отпуск с «{{start_date|format_date}}» по «{{end_date|format_date}}» продолжительностью {{days_count}} календарных дней.

«{{request_date|format_date}}»                            _______________ / {{employee_name}} /
        """,
        "workflow": ["generate", "submit_to_hr", "approve_manager", "approve_director", "create_order"],
        "output_format": "docx"
    },

    "leave_order": {
        "id": "leave_order",
        "name": "Приказ о предоставлении отпуска (Т-6)",
        "name_en": "Leave Order",
        "category": "hr",
        "subcategory": "leave",
        "description": "Приказ о предоставлении отпуска работнику",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "order_number", "label": "Номер приказа", "type": "text", "required": True},
            {"name": "order_date", "label": "Дата приказа", "type": "date", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "employee_tab_number", "label": "Табельный номер", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "department", "label": "Подразделение", "type": "text", "required": False},
            {"name": "leave_type", "label": "Вид отпуска", "type": "text", "required": True},
            {"name": "period_start", "label": "За период работы с", "type": "date", "required": True},
            {"name": "period_end", "label": "За период работы по", "type": "date", "required": True},
            {"name": "leave_start", "label": "Дата начала отпуска", "type": "date", "required": True},
            {"name": "leave_end", "label": "Дата окончания отпуска", "type": "date", "required": True},
            {"name": "days_count", "label": "Количество дней", "type": "number", "required": True},
            {"name": "director_name", "label": "ФИО руководителя", "type": "text", "required": True},
        ],
        "template_content": """
                                                           Унифицированная форма № Т-6
{{company_name}}

                                                           Номер документа    Дата составления
                                                              {{order_number}}     {{order_date|format_date}}

                              ПРИКАЗ
                     (распоряжение)
            о предоставлении отпуска работнику

Предоставить отпуск                                        Табельный номер
{{employee_name}}                                          {{employee_tab_number}}
─────────────────────────────────────────────────────
                    фамилия, имя, отчество

{{department}}
─────────────────────────────────────────────────────
            структурное подразделение

{{position}}
─────────────────────────────────────────────────────
                         должность

за период работы с «{{period_start|format_date}}» по «{{period_end|format_date}}»

А. {{leave_type}}
   на {{days_count}} календарных дней
   с «{{leave_start|format_date}}» по «{{leave_end|format_date}}»

Руководитель организации _________________ {{director_name}}

С приказом ознакомлен _________________ «___» ________ 20__ г.
        """,
        "workflow": ["generate", "sign_director", "employee_acknowledge", "payroll", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # JOB DESCRIPTIONS & POLICIES
    # =========================================================================

    "job_description": {
        "id": "job_description",
        "name": "Должностная инструкция",
        "name_en": "Job Description",
        "category": "hr",
        "subcategory": "policies",
        "description": "Должностная инструкция работника",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "department", "label": "Подразделение", "type": "text", "required": False},
            {"name": "reports_to", "label": "Подчиняется", "type": "text", "required": True},
            {"name": "requirements", "label": "Требования к квалификации", "type": "textarea", "required": True},
            {"name": "duties", "label": "Должностные обязанности", "type": "textarea", "required": True},
            {"name": "rights", "label": "Права", "type": "textarea", "required": True},
            {"name": "responsibilities", "label": "Ответственность", "type": "textarea", "required": True},
            {"name": "approval_date", "label": "Дата утверждения", "type": "date", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
        ],
        "template_content": """
                                                           УТВЕРЖДАЮ
                                                           Генеральный директор
                                                           {{company_name}}
                                                           __________ / {{director_name}} /
                                                           «{{approval_date|format_date}}»

                         ДОЛЖНОСТНАЯ ИНСТРУКЦИЯ
                              {{position}}
                    {% if department %}{{department}}{% endif %}

1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. {{position}} относится к категории специалистов.
1.2. На должность {{position}} назначается лицо, отвечающее следующим требованиям:
{{requirements}}
1.3. {{position}} подчиняется непосредственно {{reports_to}}.
1.4. На время отсутствия {{position}} его обязанности исполняет лицо, назначенное приказом руководителя.

2. ДОЛЖНОСТНЫЕ ОБЯЗАННОСТИ

{{duties}}

3. ПРАВА

{{position}} имеет право:
{{rights}}

4. ОТВЕТСТВЕННОСТЬ

{{position}} несет ответственность:
{{responsibilities}}

5. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

5.1. Настоящая инструкция разработана в соответствии с законодательством РФ.
5.2. Ознакомление работника с инструкцией производится под роспись.

С должностной инструкцией ознакомлен(а):

_________________ / _________________ /
    подпись              ФИО

«___» _____________ 20___ г.
        """,
        "workflow": ["generate", "approve_director", "employee_sign", "archive"],
        "output_format": "docx"
    },

    "internal_labor_rules": {
        "id": "internal_labor_rules",
        "name": "Правила внутреннего трудового распорядка",
        "name_en": "Internal Labor Regulations",
        "category": "hr",
        "subcategory": "policies",
        "description": "ПВТР организации",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "work_start_time", "label": "Начало рабочего дня", "type": "time", "required": True},
            {"name": "work_end_time", "label": "Окончание рабочего дня", "type": "time", "required": True},
            {"name": "lunch_start", "label": "Начало обеда", "type": "time", "required": True},
            {"name": "lunch_end", "label": "Окончание обеда", "type": "time", "required": True},
            {"name": "work_days", "label": "Рабочие дни", "type": "text", "required": True},
            {"name": "approval_date", "label": "Дата утверждения", "type": "date", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
        ],
        "template_content": """
                                                           УТВЕРЖДАЮ
                                                           Генеральный директор
                                                           {{company_name}}
                                                           __________ / {{director_name}} /
                                                           «{{approval_date|format_date}}»

              ПРАВИЛА ВНУТРЕННЕГО ТРУДОВОГО РАСПОРЯДКА
                          {{company_name}}

1. ОБЩИЕ ПОЛОЖЕНИЯ
1.1. Настоящие Правила определяют внутренний трудовой распорядок в {{company_name}}.
1.2. Правила обязательны для всех работников организации.

2. ПОРЯДОК ПРИЕМА И УВОЛЬНЕНИЯ
2.1. Прием на работу оформляется трудовым договором.
2.2. При приеме работник предъявляет документы согласно ст. 65 ТК РФ.
2.3. Увольнение производится по основаниям, предусмотренным ТК РФ.

3. РАБОЧЕЕ ВРЕМЯ
3.1. В организации устанавливается следующий режим работы:
    - Рабочие дни: {{work_days}}
    - Начало работы: {{work_start_time}}
    - Окончание работы: {{work_end_time}}
    - Перерыв на обед: с {{lunch_start}} до {{lunch_end}}

3.2. Продолжительность рабочей недели - 40 часов.

4. ВРЕМЯ ОТДЫХА
4.1. Работникам предоставляется ежегодный оплачиваемый отпуск 28 календарных дней.
4.2. Выходные дни: суббота, воскресенье.

5. ОПЛАТА ТРУДА
5.1. Заработная плата выплачивается 2 раза в месяц.
5.2. Размер оплаты определяется трудовым договором.

6. ПООЩРЕНИЯ И ВЗЫСКАНИЯ
6.1. За добросовестный труд применяются поощрения.
6.2. За нарушение дисциплины применяются взыскания согласно ТК РФ.

7. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ
7.1. Правила вступают в силу с момента утверждения.
7.2. Изменения вносятся приказом руководителя.

С Правилами ознакомлен(а): _________________ / _________________ / «___» ________ 20__ г.
        """,
        "workflow": ["generate", "approve_director", "all_employees_sign", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # NDA & LIABILITY
    # =========================================================================

    "employee_nda": {
        "id": "employee_nda",
        "name": "Соглашение о неразглашении (для сотрудников)",
        "name_en": "Employee NDA",
        "category": "hr",
        "subcategory": "confidentiality",
        "description": "NDA для работников организации",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "confidential_info_types", "label": "Виды конфиденциальной информации", "type": "textarea", "required": True},
            {"name": "validity_years", "label": "Срок действия после увольнения (лет)", "type": "number", "required": True},
            {"name": "penalty_amount", "label": "Штраф за нарушение", "type": "number", "required": False},
            {"name": "agreement_date", "label": "Дата соглашения", "type": "date", "required": True},
        ],
        "template_content": """
                 СОГЛАШЕНИЕ О НЕРАЗГЛАШЕНИИ
             КОНФИДЕНЦИАЛЬНОЙ ИНФОРМАЦИИ № ___

г. Москва                                                     «{{agreement_date|format_date}}»

{{company_name}} («Работодатель») и {{employee_name}}, {{position}} («Работник»),

заключили настоящее Соглашение о нижеследующем:

1. ПРЕДМЕТ СОГЛАШЕНИЯ

1.1. Работник обязуется не разглашать конфиденциальную информацию Работодателя.

1.2. К конфиденциальной информации относится:
{{confidential_info_types}}

2. ОБЯЗАТЕЛЬСТВА РАБОТНИКА

2.1. Работник обязуется:
- не разглашать конфиденциальную информацию третьим лицам;
- не использовать информацию в личных целях;
- не копировать информацию без разрешения;
- возвратить все носители информации при увольнении.

3. СРОК ДЕЙСТВИЯ

3.1. Обязательства действуют в течение {{validity_years}} лет после прекращения трудовых отношений.

4. ОТВЕТСТВЕННОСТЬ

4.1. За нарушение настоящего Соглашения Работник несет ответственность в соответствии с законодательством РФ.
{% if penalty_amount %}
4.2. Штраф за нарушение составляет {{penalty_amount}} рублей.
{% endif %}

ПОДПИСИ СТОРОН:

РАБОТОДАТЕЛЬ:                              РАБОТНИК:
{{company_name}}                           {{employee_name}}

_____________________                      _____________________
        """,
        "workflow": ["generate", "sign_both", "archive"],
        "output_format": "docx"
    },

    "material_liability_agreement": {
        "id": "material_liability_agreement",
        "name": "Договор о полной материальной ответственности",
        "name_en": "Full Material Liability Agreement",
        "category": "hr",
        "subcategory": "liability",
        "description": "Договор о полной индивидуальной материальной ответственности",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "property_description", "label": "Описание вверенного имущества", "type": "textarea", "required": True},
            {"name": "agreement_date", "label": "Дата договора", "type": "date", "required": True},
        ],
        "template_content": """
                              ДОГОВОР
            О ПОЛНОЙ ИНДИВИДУАЛЬНОЙ МАТЕРИАЛЬНОЙ
                       ОТВЕТСТВЕННОСТИ

г. Москва                                                     «{{agreement_date|format_date}}»

{{company_name}} в лице Генерального директора («Работодатель») и {{employee_name}}, {{position}} («Работник»),

заключили настоящий Договор о нижеследующем:

1. Работник принимает на себя полную материальную ответственность за обеспечение сохранности вверенных ему Работодателем материальных ценностей:
{{property_description}}

2. Работник обязуется:
- бережно относиться к вверенному имуществу;
- своевременно сообщать об угрозе сохранности;
- вести учет имущества;
- участвовать в инвентаризации.

3. Работодатель обязуется:
- создать условия для сохранности имущества;
- ознакомить с правилами хранения;
- проводить инвентаризацию.

4. Работник несет полную материальную ответственность за недостачу вверенного имущества.

5. Работник освобождается от ответственности, если ущерб причинен не по его вине.

ПОДПИСИ СТОРОН:

РАБОТОДАТЕЛЬ:                              РАБОТНИК:
_____________________                      _____________________
        """,
        "workflow": ["generate", "sign_both", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # PERSONNEL CARDS & RECORDS
    # =========================================================================

    "personal_card_t2": {
        "id": "personal_card_t2",
        "name": "Личная карточка работника (Т-2)",
        "name_en": "Personal Employee Card T-2",
        "category": "hr",
        "subcategory": "records",
        "description": "Унифицированная форма Т-2 личной карточки",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО", "type": "text", "required": True},
            {"name": "birth_date", "label": "Дата рождения", "type": "date", "required": True},
            {"name": "birth_place", "label": "Место рождения", "type": "text", "required": True},
            {"name": "citizenship", "label": "Гражданство", "type": "text", "required": True},
            {"name": "education", "label": "Образование", "type": "text", "required": True},
            {"name": "specialty", "label": "Специальность", "type": "text", "required": True},
            {"name": "marital_status", "label": "Семейное положение", "type": "text", "required": True},
            {"name": "passport", "label": "Паспорт", "type": "text", "required": True},
            {"name": "address", "label": "Адрес регистрации", "type": "text", "required": True},
            {"name": "phone", "label": "Телефон", "type": "text", "required": True},
            {"name": "inn", "label": "ИНН", "type": "text", "required": True},
            {"name": "snils", "label": "СНИЛС", "type": "text", "required": True},
        ],
        "template_content": """
                                                           Унифицированная форма № Т-2
{{company_name}}
                              ЛИЧНАЯ КАРТОЧКА РАБОТНИКА

I. ОБЩИЕ СВЕДЕНИЯ

1. Фамилия, имя, отчество: {{employee_name}}
2. Дата рождения: {{birth_date|format_date}}
3. Место рождения: {{birth_place}}
4. Гражданство: {{citizenship}}
5. Образование: {{education}}
6. Специальность: {{specialty}}
7. Семейное положение: {{marital_status}}
8. Паспорт: {{passport}}
9. Адрес регистрации: {{address}}
10. Телефон: {{phone}}
11. ИНН: {{inn}}
12. СНИЛС: {{snils}}

II. СВЕДЕНИЯ О ВОИНСКОМ УЧЕТЕ
_______________________________________________

III. ПРИЕМ НА РАБОТУ И ПЕРЕВОДЫ
_______________________________________________

IV. ОТПУСКА
_______________________________________________

V. ДОПОЛНИТЕЛЬНЫЕ СВЕДЕНИЯ
_______________________________________________

Работник кадровой службы: _________________ / _________________ /
        """,
        "workflow": ["generate", "fill_data", "update_regularly", "archive_on_termination"],
        "output_format": "docx"
    },

    "reference_2ndfl": {
        "id": "reference_2ndfl",
        "name": "Справка 2-НДФЛ",
        "name_en": "2-NDFL Tax Certificate",
        "category": "hr",
        "subcategory": "references",
        "description": "Справка о доходах физического лица",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "company_inn", "label": "ИНН организации", "type": "text", "required": True},
            {"name": "company_kpp", "label": "КПП организации", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "employee_inn", "label": "ИНН работника", "type": "text", "required": True},
            {"name": "year", "label": "Отчетный год", "type": "number", "required": True},
            {"name": "monthly_income", "label": "Доходы по месяцам", "type": "array", "required": True},
            {"name": "total_income", "label": "Общая сумма дохода", "type": "number", "required": True},
            {"name": "tax_withheld", "label": "Сумма налога удержанная", "type": "number", "required": True},
        ],
        "template_content": """
                    СПРАВКА О ДОХОДАХ ФИЗИЧЕСКОГО ЛИЦА
                               за {{year}} год

1. Данные о налоговом агенте
Наименование: {{company_name}}
ИНН: {{company_inn}} КПП: {{company_kpp}}

2. Данные о физическом лице
ФИО: {{employee_name}}
ИНН: {{employee_inn}}

3. Доходы, облагаемые по ставке 13%

Месяц | Код дохода | Сумма дохода
{% for income in monthly_income %}
{{income.month}} | 2000 | {{income.amount}}
{% endfor %}

Общая сумма дохода: {{total_income}} руб.
Налоговая база: {{total_income}} руб.
Сумма налога исчисленная: {{(total_income * 0.13)|int}} руб.
Сумма налога удержанная: {{tax_withheld}} руб.

Руководитель: _________________ / _________________ /

М.П.                                          Дата: «___» ________ 20__ г.
        """,
        "workflow": ["generate", "sign", "stamp", "issue"],
        "output_format": "docx"
    },

    "income_reference": {
        "id": "income_reference",
        "name": "Справка о доходах",
        "name_en": "Income Reference",
        "category": "hr",
        "subcategory": "references",
        "description": "Справка о заработной плате для предоставления в банк или госорганы",
        "required_fields": [
            {"name": "company_name", "label": "Наименование организации", "type": "text", "required": True},
            {"name": "company_address", "label": "Адрес организации", "type": "text", "required": True},
            {"name": "company_phone", "label": "Телефон организации", "type": "text", "required": True},
            {"name": "employee_name", "label": "ФИО работника", "type": "text", "required": True},
            {"name": "position", "label": "Должность", "type": "text", "required": True},
            {"name": "hire_date", "label": "Дата приема на работу", "type": "date", "required": True},
            {"name": "monthly_salary", "label": "Среднемесячный доход", "type": "number", "required": True},
            {"name": "period_months", "label": "За период (мес.)", "type": "number", "required": True},
            {"name": "purpose", "label": "Цель справки", "type": "text", "required": True},
        ],
        "template_content": """
{{company_name}}
Адрес: {{company_address}}
Тел.: {{company_phone}}

                              СПРАВКА

Выдана {{employee_name}} в том, что он(а) действительно работает в {{company_name}} в должности {{position}} с «{{hire_date|format_date}}» по настоящее время.

Среднемесячный доход за последние {{period_months}} месяцев составляет {{monthly_salary}} ({{monthly_salary_words}}) рублей.

Справка выдана для предоставления {{purpose}}.

Генеральный директор _________________ / _________________ /

Главный бухгалтер _________________ / _________________ /

М.П.                                          «___» ________ 20__ г.
        """,
        "workflow": ["generate", "sign_director", "sign_accountant", "stamp", "issue"],
        "output_format": "docx"
    },
}


def get_hr_templates() -> Dict[str, Any]:
    """Return all HR templates."""
    return HR_TEMPLATES


def get_template(template_id: str) -> Dict[str, Any]:
    """Get a specific template by ID."""
    return HR_TEMPLATES.get(template_id)


from enum import Enum


class HRDocType(str, Enum):
    """HR document types."""
    EMPLOYMENT_CONTRACT = "employment_contract"
    DISMISSAL_ORDER = "dismissal_order"
    VACATION_ORDER = "vacation_order"
    INTERNAL_LABOR_RULES = "internal_labor_rules"
    JOB_DESCRIPTION = "job_description"
    NDA_EMPLOYEE = "nda_employee"
    CONTRACTOR_AGREEMENT = "contractor_agreement"


class HRTemplateService:
    """Service for HR document templates."""

    @staticmethod
    def list_templates() -> List[Dict[str, Any]]:
        """List all HR templates."""
        return [
            {"type": tid, "name": t["name"], "category": "hr"}
            for tid, t in HR_TEMPLATES.items()
        ]

    @staticmethod
    def get_template(doc_type: HRDocType) -> Dict[str, Any]:
        """Get template by document type."""
        return HR_TEMPLATES.get(doc_type.value)

    @staticmethod
    def generate(doc_type: HRDocType, data: Dict[str, Any]) -> str:
        """Generate document from template."""
        template = HR_TEMPLATES.get(doc_type.value)
        if not template:
            raise ValueError(f"Template not found: {doc_type}")

        from jinja2 import Template
        content = template.get("template_content", "")
        tpl = Template(content)
        return tpl.render(**data)

    @staticmethod
    def generate_document(doc_type: HRDocType, data: Dict[str, Any]) -> str:
        """Generate document from template (alias for generate)."""
        return HRTemplateService.generate(doc_type, data)
