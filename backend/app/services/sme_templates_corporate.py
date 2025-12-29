"""
Phase 7: Corporate & Shareholder Document Templates
15 templates for company formation, governance, and shareholder management.
"""

from typing import Dict, List, Any
from datetime import date

CORPORATE_TEMPLATES = {
    # =========================================================================
    # COMPANY FORMATION
    # =========================================================================

    "charter_ooo": {
        "id": "charter_ooo",
        "name": "Устав ООО",
        "name_en": "LLC Charter",
        "category": "corporate",
        "subcategory": "formation",
        "description": "Учредительный документ общества с ограниченной ответственностью",
        "required_fields": [
            {"name": "company_name", "label": "Полное наименование", "type": "text", "required": True},
            {"name": "short_name", "label": "Сокращенное наименование", "type": "text", "required": True},
            {"name": "legal_address", "label": "Юридический адрес", "type": "text", "required": True},
            {"name": "authorized_capital", "label": "Уставный капитал (руб.)", "type": "number", "required": True, "min": 10000},
            {"name": "activities", "label": "Виды деятельности", "type": "textarea", "required": True},
            {"name": "founder_names", "label": "ФИО учредителей", "type": "array", "required": True},
            {"name": "founder_shares", "label": "Доли учредителей (%)", "type": "array", "required": True},
        ],
        "template_content": """
УСТАВ
ОБЩЕСТВА С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ
«{{company_name}}»

г. Москва
{{current_year}} год

1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Общество с ограниченной ответственностью «{{company_name}}», именуемое в дальнейшем «Общество», создано в соответствии с Гражданским кодексом Российской Федерации и Федеральным законом «Об обществах с ограниченной ответственностью».

1.2. Полное фирменное наименование Общества: Общество с ограниченной ответственностью «{{company_name}}».

1.3. Сокращенное фирменное наименование Общества: ООО «{{short_name}}».

1.4. Место нахождения Общества: {{legal_address}}.

2. ЦЕЛИ И ПРЕДМЕТ ДЕЯТЕЛЬНОСТИ

2.1. Целью деятельности Общества является извлечение прибыли.

2.2. Предметом деятельности Общества являются:
{{activities}}

3. УСТАВНЫЙ КАПИТАЛ

3.1. Уставный капитал Общества составляет {{authorized_capital}} ({{authorized_capital_words}}) рублей.

3.2. Уставный капитал Общества разделен на доли следующим образом:
{% for i in range(founder_names|length) %}
- {{founder_names[i]}}: {{founder_shares[i]}}% уставного капитала, номинальной стоимостью {{(authorized_capital * founder_shares[i] / 100)|int}} рублей.
{% endfor %}

4. ПРАВА И ОБЯЗАННОСТИ УЧАСТНИКОВ

4.1. Участники Общества имеют право:
- участвовать в управлении делами Общества;
- получать информацию о деятельности Общества;
- принимать участие в распределении прибыли;
- продать или осуществить отчуждение иным образом своей доли;
- выйти из Общества независимо от согласия других участников;
- получить в случае ликвидации часть имущества.

4.2. Участники Общества обязаны:
- оплачивать доли в уставном капитале;
- не разглашать конфиденциальную информацию;
- соблюдать положения настоящего Устава.

5. ОРГАНЫ УПРАВЛЕНИЯ

5.1. Высшим органом управления Общества является Общее собрание участников.

5.2. Руководство текущей деятельностью Общества осуществляется единоличным исполнительным органом – Генеральным директором.

5.3. Генеральный директор избирается Общим собранием участников сроком на 5 (пять) лет.

6. ОБЩЕЕ СОБРАНИЕ УЧАСТНИКОВ

6.1. К компетенции Общего собрания участников относятся:
- определение основных направлений деятельности Общества;
- изменение Устава, включая изменение размера уставного капитала;
- избрание Генерального директора и досрочное прекращение его полномочий;
- утверждение годовых отчетов и бухгалтерских балансов;
- принятие решения о распределении чистой прибыли;
- принятие решения о реорганизации или ликвидации Общества.

7. ГЕНЕРАЛЬНЫЙ ДИРЕКТОР

7.1. Генеральный директор:
- без доверенности действует от имени Общества;
- представляет интересы Общества;
- распоряжается имуществом Общества;
- заключает договоры, выдает доверенности;
- издает приказы, дает указания;
- осуществляет иные полномочия.

8. РАСПРЕДЕЛЕНИЕ ПРИБЫЛИ

8.1. Общество вправе ежеквартально, раз в полгода или раз в год принимать решение о распределении чистой прибыли между участниками.

8.2. Часть прибыли, подлежащая распределению, распределяется пропорционально долям участников в уставном капитале.

9. ПЕРЕХОД ДОЛИ

9.1. Участник вправе продать или осуществить отчуждение иным образом своей доли другим участникам Общества.

9.2. Продажа доли третьим лицам допускается с согласия остальных участников.

9.3. Участники пользуются преимущественным правом покупки доли.

10. ВЫХОД УЧАСТНИКА

10.1. Участник вправе выйти из Общества независимо от согласия других участников путем подачи заявления.

10.2. Доля переходит к Обществу с даты получения заявления.

10.3. Общество обязано выплатить действительную стоимость доли в течение трех месяцев.

11. РЕОРГАНИЗАЦИЯ И ЛИКВИДАЦИЯ

11.1. Общество может быть реорганизовано или ликвидировано по решению Общего собрания участников.

11.2. Ликвидация осуществляется ликвидационной комиссией.

12. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

12.1. Настоящий Устав вступает в силу с момента государственной регистрации Общества.

12.2. Изменения в Устав подлежат государственной регистрации.
        """,
        "workflow": ["generate", "sign_founders", "notarize", "submit_fns", "receive_registration"],
        "output_format": "docx",
        "legal_references": ["ГК РФ", "14-ФЗ Об ООО"]
    },

    "formation_decision_sole": {
        "id": "formation_decision_sole",
        "name": "Решение единственного учредителя о создании ООО",
        "name_en": "Sole Founder Decision to Form LLC",
        "category": "corporate",
        "subcategory": "formation",
        "description": "Решение о создании ООО одним учредителем",
        "required_fields": [
            {"name": "founder_name", "label": "ФИО учредителя", "type": "text", "required": True},
            {"name": "founder_passport", "label": "Паспортные данные", "type": "text", "required": True},
            {"name": "founder_address", "label": "Адрес регистрации", "type": "text", "required": True},
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "legal_address", "label": "Юридический адрес", "type": "text", "required": True},
            {"name": "authorized_capital", "label": "Уставный капитал", "type": "number", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "decision_date", "label": "Дата решения", "type": "date", "required": True},
        ],
        "template_content": """
РЕШЕНИЕ № 1
единственного учредителя
о создании Общества с ограниченной ответственностью
«{{company_name}}»

г. Москва                                                     «{{decision_date|format_date}}»

Я, {{founder_name}}, паспорт {{founder_passport}}, зарегистрированный(ая) по адресу: {{founder_address}}, являясь единственным учредителем,

РЕШИЛ(А):

1. Создать Общество с ограниченной ответственностью «{{company_name}}».

2. Определить место нахождения Общества: {{legal_address}}.

3. Утвердить Устав Общества.

4. Определить размер уставного капитала Общества в сумме {{authorized_capital}} ({{authorized_capital_words}}) рублей.

5. Оплатить уставный капитал денежными средствами в размере 100% в течение 4 (четырех) месяцев с момента государственной регистрации Общества.

6. Назначить на должность Генерального директора Общества {{director_name}} сроком на 5 (пять) лет.

7. Поручить Генеральному директору осуществить все необходимые действия, связанные с государственной регистрацией Общества.


Единственный учредитель: _____________________ / {{founder_name}} /
        """,
        "workflow": ["generate", "sign", "submit_fns"],
        "output_format": "docx"
    },

    "formation_decision_multiple": {
        "id": "formation_decision_multiple",
        "name": "Протокол собрания учредителей о создании ООО",
        "name_en": "Founders Meeting Minutes - LLC Formation",
        "category": "corporate",
        "subcategory": "formation",
        "description": "Протокол учредительного собрания при создании ООО несколькими учредителями",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "meeting_date", "label": "Дата собрания", "type": "date", "required": True},
            {"name": "meeting_address", "label": "Место проведения", "type": "text", "required": True},
            {"name": "founders", "label": "Учредители (ФИО, паспорт, доля %)", "type": "array", "required": True},
            {"name": "legal_address", "label": "Юридический адрес", "type": "text", "required": True},
            {"name": "authorized_capital", "label": "Уставный капитал", "type": "number", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "chairman_name", "label": "Председатель собрания", "type": "text", "required": True},
            {"name": "secretary_name", "label": "Секретарь собрания", "type": "text", "required": True},
        ],
        "template_content": """
ПРОТОКОЛ № 1
учредительного собрания
Общества с ограниченной ответственностью «{{company_name}}»

г. Москва                                                     «{{meeting_date|format_date}}»

Место проведения: {{meeting_address}}
Время начала: 10:00
Время окончания: 11:00

Присутствовали учредители:
{% for founder in founders %}
{{loop.index}}. {{founder.name}}, паспорт {{founder.passport}}
{% endfor %}

Кворум для принятия решений имеется. Собрание правомочно.

Председатель собрания: {{chairman_name}}
Секретарь собрания: {{secretary_name}}

ПОВЕСТКА ДНЯ:

1. Об учреждении ООО «{{company_name}}».
2. Об утверждении Устава Общества.
3. О размере и порядке оплаты уставного капитала.
4. Об избрании Генерального директора.
5. О государственной регистрации Общества.

СЛУШАЛИ: {{chairman_name}} - предложение создать ООО «{{company_name}}».

ПОСТАНОВИЛИ:

1. Создать Общество с ограниченной ответственностью «{{company_name}}».
Голосовали: «за» - единогласно.

2. Утвердить Устав ООО «{{company_name}}».
Голосовали: «за» - единогласно.

3. Определить размер уставного капитала - {{authorized_capital}} рублей. Распределение долей:
{% for founder in founders %}
- {{founder.name}}: {{founder.share}}%, номинальная стоимость {{(authorized_capital * founder.share / 100)|int}} руб.
{% endfor %}
Голосовали: «за» - единогласно.

4. Избрать Генеральным директором {{director_name}} сроком на 5 лет.
Голосовали: «за» - единогласно.

5. Определить место нахождения Общества: {{legal_address}}.
Голосовали: «за» - единогласно.

6. Поручить Генеральному директору осуществить государственную регистрацию Общества.
Голосовали: «за» - единогласно.

Председатель собрания: _____________________ / {{chairman_name}} /

Секретарь собрания: _____________________ / {{secretary_name}} /

Учредители:
{% for founder in founders %}
_____________________ / {{founder.name}} /
{% endfor %}
        """,
        "workflow": ["generate", "sign_all_founders", "submit_fns"],
        "output_format": "docx"
    },

    "founders_agreement": {
        "id": "founders_agreement",
        "name": "Договор об учреждении ООО",
        "name_en": "LLC Founders Agreement",
        "category": "corporate",
        "subcategory": "formation",
        "description": "Договор между учредителями о создании ООО",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "agreement_date", "label": "Дата договора", "type": "date", "required": True},
            {"name": "founders", "label": "Учредители", "type": "array", "required": True},
            {"name": "authorized_capital", "label": "Уставный капитал", "type": "number", "required": True},
            {"name": "payment_deadline_days", "label": "Срок оплаты долей (дней)", "type": "number", "required": True},
        ],
        "template_content": """
ДОГОВОР ОБ УЧРЕЖДЕНИИ
Общества с ограниченной ответственностью «{{company_name}}»

г. Москва                                                     «{{agreement_date|format_date}}»

Мы, нижеподписавшиеся:
{% for founder in founders %}
{{loop.index}}. {{founder.name}}, паспорт {{founder.passport}}, адрес: {{founder.address}},
{% endfor %}

именуемые в дальнейшем «Учредители», заключили настоящий Договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Учредители обязуются создать Общество с ограниченной ответственностью «{{company_name}}» (далее – Общество).

1.2. Учредители обязуются оплатить уставный капитал Общества в порядке и сроки, установленные настоящим Договором.

2. УСТАВНЫЙ КАПИТАЛ

2.1. Размер уставного капитала Общества составляет {{authorized_capital}} ({{authorized_capital_words}}) рублей.

2.2. Уставный капитал разделяется между Учредителями следующим образом:
{% for founder in founders %}
- {{founder.name}}: доля {{founder.share}}%, номинальная стоимость {{(authorized_capital * founder.share / 100)|int}} руб.
{% endfor %}

2.3. Оплата долей производится денежными средствами.

2.4. Срок оплаты: {{payment_deadline_days}} дней с момента государственной регистрации Общества.

3. ПОРЯДОК ДЕЯТЕЛЬНОСТИ УЧРЕДИТЕЛЕЙ

3.1. Учредители совместно:
- утверждают Устав Общества;
- избирают органы управления Общества;
- определяют порядок государственной регистрации.

4. РАСХОДЫ ПО СОЗДАНИЮ

4.1. Расходы по созданию Общества несут Учредители пропорционально их долям в уставном капитале.

5. ОТВЕТСТВЕННОСТЬ

5.1. За неисполнение обязательств Учредители несут ответственность в соответствии с законодательством РФ.

6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

6.1. Договор вступает в силу с момента подписания.

6.2. После государственной регистрации Общества настоящий Договор прекращает действие.

ПОДПИСИ УЧРЕДИТЕЛЕЙ:

{% for founder in founders %}
{{founder.name}}: _____________________
{% endfor %}
        """,
        "workflow": ["generate", "sign_all_founders", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # SHAREHOLDER MEETINGS
    # =========================================================================

    "shareholder_meeting_minutes": {
        "id": "shareholder_meeting_minutes",
        "name": "Протокол общего собрания участников",
        "name_en": "General Shareholder Meeting Minutes",
        "category": "corporate",
        "subcategory": "governance",
        "description": "Протокол очередного или внеочередного собрания участников ООО",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "meeting_number", "label": "Номер протокола", "type": "number", "required": True},
            {"name": "meeting_date", "label": "Дата собрания", "type": "date", "required": True},
            {"name": "meeting_type", "label": "Тип собрания", "type": "select", "options": ["Очередное", "Внеочередное"], "required": True},
            {"name": "participants", "label": "Участники", "type": "array", "required": True},
            {"name": "agenda_items", "label": "Вопросы повестки дня", "type": "array", "required": True},
            {"name": "decisions", "label": "Принятые решения", "type": "array", "required": True},
            {"name": "chairman", "label": "Председатель", "type": "text", "required": True},
            {"name": "secretary", "label": "Секретарь", "type": "text", "required": True},
        ],
        "template_content": """
ПРОТОКОЛ № {{meeting_number}}
{{meeting_type}} общего собрания участников
ООО «{{company_name}}»

г. Москва                                                     «{{meeting_date|format_date}}»

Присутствовали участники, обладающие в совокупности 100% голосов:
{% for p in participants %}
- {{p.name}} (доля {{p.share}}%)
{% endfor %}

Кворум имеется. Собрание правомочно принимать решения по всем вопросам повестки дня.

Председатель собрания: {{chairman}}
Секретарь собрания: {{secretary}}

ПОВЕСТКА ДНЯ:
{% for item in agenda_items %}
{{loop.index}}. {{item}}
{% endfor %}

{% for decision in decisions %}
По {{loop.index}} вопросу повестки дня:

СЛУШАЛИ: {{decision.speaker}} - {{decision.topic}}

ПОСТАНОВИЛИ: {{decision.resolution}}

Голосовали: «за» - {{decision.votes_for}}%, «против» - {{decision.votes_against}}%, воздержались - {{decision.abstained}}%.
Решение принято.

{% endfor %}

Председатель собрания: _____________________ / {{chairman}} /

Секретарь собрания: _____________________ / {{secretary}} /
        """,
        "workflow": ["generate", "sign_chairman_secretary", "archive"],
        "output_format": "docx"
    },

    "sole_participant_decision": {
        "id": "sole_participant_decision",
        "name": "Решение единственного участника",
        "name_en": "Sole Participant Decision",
        "category": "corporate",
        "subcategory": "governance",
        "description": "Решение единственного участника ООО по текущим вопросам",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "decision_number", "label": "Номер решения", "type": "number", "required": True},
            {"name": "decision_date", "label": "Дата решения", "type": "date", "required": True},
            {"name": "participant_name", "label": "ФИО участника", "type": "text", "required": True},
            {"name": "participant_share", "label": "Размер доли (%)", "type": "number", "required": True},
            {"name": "decisions", "label": "Принятые решения", "type": "array", "required": True},
        ],
        "template_content": """
РЕШЕНИЕ № {{decision_number}}
единственного участника
ООО «{{company_name}}»

г. Москва                                                     «{{decision_date|format_date}}»

Я, {{participant_name}}, являясь единственным участником ООО «{{company_name}}», владеющим долей в размере {{participant_share}}% уставного капитала,

РЕШИЛ:

{% for decision in decisions %}
{{loop.index}}. {{decision}}

{% endfor %}

Единственный участник: _____________________ / {{participant_name}} /
        """,
        "workflow": ["generate", "sign", "archive"],
        "output_format": "docx"
    },

    # =========================================================================
    # SHARE TRANSFERS
    # =========================================================================

    "share_sale_agreement": {
        "id": "share_sale_agreement",
        "name": "Договор купли-продажи доли в ООО",
        "name_en": "LLC Share Sale Agreement",
        "category": "corporate",
        "subcategory": "shares",
        "description": "Договор продажи доли в уставном капитале ООО",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "company_inn", "label": "ИНН компании", "type": "text", "required": True},
            {"name": "company_ogrn", "label": "ОГРН компании", "type": "text", "required": True},
            {"name": "seller_name", "label": "ФИО продавца", "type": "text", "required": True},
            {"name": "seller_passport", "label": "Паспорт продавца", "type": "text", "required": True},
            {"name": "buyer_name", "label": "ФИО покупателя", "type": "text", "required": True},
            {"name": "buyer_passport", "label": "Паспорт покупателя", "type": "text", "required": True},
            {"name": "share_percent", "label": "Размер доли (%)", "type": "number", "required": True},
            {"name": "share_nominal", "label": "Номинальная стоимость", "type": "number", "required": True},
            {"name": "sale_price", "label": "Цена продажи", "type": "number", "required": True},
            {"name": "agreement_date", "label": "Дата договора", "type": "date", "required": True},
        ],
        "template_content": """
ДОГОВОР
купли-продажи доли в уставном капитале
Общества с ограниченной ответственностью «{{company_name}}»

г. Москва                                                     «{{agreement_date|format_date}}»

{{seller_name}}, паспорт {{seller_passport}}, именуемый в дальнейшем «Продавец», с одной стороны, и

{{buyer_name}}, паспорт {{buyer_passport}}, именуемый в дальнейшем «Покупатель», с другой стороны,

заключили настоящий Договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Продавец продает, а Покупатель покупает долю в размере {{share_percent}}% в уставном капитале ООО «{{company_name}}» (ИНН {{company_inn}}, ОГРН {{company_ogrn}}).

1.2. Номинальная стоимость доли составляет {{share_nominal}} ({{share_nominal_words}}) рублей.

2. ЦЕНА И ПОРЯДОК РАСЧЕТОВ

2.1. Цена доли составляет {{sale_price}} ({{sale_price_words}}) рублей.

2.2. Покупатель обязуется оплатить стоимость доли в течение 5 (пяти) рабочих дней с момента нотариального удостоверения настоящего Договора.

3. ГАРАНТИИ ПРОДАВЦА

3.1. Продавец гарантирует, что:
- является законным владельцем отчуждаемой доли;
- доля полностью оплачена;
- доля не заложена и не обременена правами третьих лиц;
- получены все необходимые согласия на отчуждение.

4. ПЕРЕХОД ПРАВА

4.1. Право на долю переходит к Покупателю с момента внесения соответствующей записи в ЕГРЮЛ.

5. ОТВЕТСТВЕННОСТЬ СТОРОН

5.1. За неисполнение обязательств Стороны несут ответственность в соответствии с законодательством РФ.

6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

6.1. Настоящий Договор подлежит нотариальному удостоверению.

6.2. Расходы по нотариальному удостоверению несет Покупатель.

ПОДПИСИ СТОРОН:

Продавец: _____________________ / {{seller_name}} /

Покупатель: _____________________ / {{buyer_name}} /
        """,
        "workflow": ["generate", "sign_both", "notarize", "submit_fns", "update_egrul"],
        "output_format": "docx",
        "requires_notary": True
    },

    "participant_exit_application": {
        "id": "participant_exit_application",
        "name": "Заявление о выходе участника из ООО",
        "name_en": "LLC Participant Exit Application",
        "category": "corporate",
        "subcategory": "shares",
        "description": "Заявление участника о выходе из общества",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "participant_name", "label": "ФИО выходящего участника", "type": "text", "required": True},
            {"name": "participant_passport", "label": "Паспорт участника", "type": "text", "required": True},
            {"name": "share_percent", "label": "Размер доли (%)", "type": "number", "required": True},
            {"name": "exit_date", "label": "Дата заявления", "type": "date", "required": True},
        ],
        "template_content": """
                                                Генеральному директору
                                                ООО «{{company_name}}»
                                                {{director_name}}

                                                от участника
                                                {{participant_name}}
                                                паспорт {{participant_passport}}

ЗАЯВЛЕНИЕ
о выходе из состава участников общества

В соответствии со статьей 26 Федерального закона от 08.02.1998 № 14-ФЗ «Об обществах с ограниченной ответственностью» и Уставом ООО «{{company_name}}», настоящим заявляю о своем выходе из состава участников Общества.

Принадлежащая мне доля в размере {{share_percent}}% уставного капитала переходит к Обществу с момента получения настоящего заявления.

Прошу выплатить мне действительную стоимость принадлежавшей мне доли в порядке и сроки, установленные законодательством и Уставом Общества.

Реквизиты для перечисления денежных средств:
Банк: _________________________________
Р/с: _________________________________
БИК: _________________________________
Получатель: {{participant_name}}

Дата: «{{exit_date|format_date}}»

_____________________ / {{participant_name}} /
        """,
        "workflow": ["generate", "sign", "notarize", "submit_to_company", "await_payment"],
        "output_format": "docx",
        "requires_notary": True
    },

    # =========================================================================
    # DIRECTOR CHANGES
    # =========================================================================

    "director_appointment_order": {
        "id": "director_appointment_order",
        "name": "Приказ о вступлении в должность директора",
        "name_en": "Director Appointment Order",
        "category": "corporate",
        "subcategory": "governance",
        "description": "Приказ о вступлении в должность генерального директора",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "appointment_date", "label": "Дата вступления в должность", "type": "date", "required": True},
            {"name": "protocol_number", "label": "Номер протокола/решения", "type": "text", "required": True},
            {"name": "protocol_date", "label": "Дата протокола/решения", "type": "date", "required": True},
        ],
        "template_content": """
ООО «{{company_name}}»

ПРИКАЗ № 1

г. Москва                                                     «{{appointment_date|format_date}}»

О вступлении в должность Генерального директора

На основании Решения/Протокола № {{protocol_number}} от {{protocol_date|format_date}} общего собрания участников (единственного участника) ООО «{{company_name}}»

ПРИКАЗЫВАЮ:

1. Вступить в должность Генерального директора ООО «{{company_name}}» с «{{appointment_date|format_date}}».

2. Возложить на себя права и обязанности единоличного исполнительного органа Общества в соответствии с Уставом и действующим законодательством РФ.


Генеральный директор: _____________________ / {{director_name}} /
        """,
        "workflow": ["generate", "sign", "archive", "submit_fns_r13014"],
        "output_format": "docx"
    },

    "director_poa": {
        "id": "director_poa",
        "name": "Доверенность от имени директора",
        "name_en": "Director Power of Attorney",
        "category": "corporate",
        "subcategory": "governance",
        "description": "Доверенность на представление интересов компании",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "company_inn", "label": "ИНН", "type": "text", "required": True},
            {"name": "company_ogrn", "label": "ОГРН", "type": "text", "required": True},
            {"name": "company_address", "label": "Юридический адрес", "type": "text", "required": True},
            {"name": "director_name", "label": "ФИО директора", "type": "text", "required": True},
            {"name": "representative_name", "label": "ФИО представителя", "type": "text", "required": True},
            {"name": "representative_passport", "label": "Паспорт представителя", "type": "text", "required": True},
            {"name": "powers", "label": "Полномочия", "type": "textarea", "required": True},
            {"name": "validity_period", "label": "Срок действия", "type": "text", "required": True},
            {"name": "issue_date", "label": "Дата выдачи", "type": "date", "required": True},
        ],
        "template_content": """
ДОВЕРЕННОСТЬ

г. Москва                                                     «{{issue_date|format_date}}»

Общество с ограниченной ответственностью «{{company_name}}», ИНН {{company_inn}}, ОГРН {{company_ogrn}}, место нахождения: {{company_address}}, в лице Генерального директора {{director_name}}, действующего на основании Устава,

настоящей доверенностью уполномочивает

{{representative_name}}, паспорт {{representative_passport}},

представлять интересы ООО «{{company_name}}» со следующими полномочиями:

{{powers}}

Доверенность выдана сроком на {{validity_period}} без права передоверия.

Подпись представителя {{representative_name}} _____________________ удостоверяю.


Генеральный директор
ООО «{{company_name}}»         _____________________ / {{director_name}} /

                                            М.П.
        """,
        "workflow": ["generate", "sign_director", "stamp", "issue"],
        "output_format": "docx"
    },

    # =========================================================================
    # CAPITAL CHANGES
    # =========================================================================

    "capital_increase_decision": {
        "id": "capital_increase_decision",
        "name": "Решение об увеличении уставного капитала",
        "name_en": "Capital Increase Decision",
        "category": "corporate",
        "subcategory": "capital",
        "description": "Решение участников об увеличении уставного капитала",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "current_capital", "label": "Текущий уставный капитал", "type": "number", "required": True},
            {"name": "increase_amount", "label": "Сумма увеличения", "type": "number", "required": True},
            {"name": "new_capital", "label": "Новый размер УК", "type": "number", "required": True},
            {"name": "increase_method", "label": "Способ увеличения", "type": "select", "options": ["За счет имущества", "Дополнительные вклады участников", "Вклады третьих лиц"], "required": True},
            {"name": "decision_date", "label": "Дата решения", "type": "date", "required": True},
        ],
        "template_content": """
РЕШЕНИЕ № ___
общего собрания участников (единственного участника)
ООО «{{company_name}}»

г. Москва                                                     «{{decision_date|format_date}}»

ПОВЕСТКА ДНЯ:
1. Об увеличении уставного капитала Общества.
2. О внесении изменений в Устав Общества.

РЕШИЛИ:

1. Увеличить уставный капитал ООО «{{company_name}}» с {{current_capital}} рублей до {{new_capital}} рублей.

2. Способ увеличения: {{increase_method}}.

3. Срок внесения дополнительных вкладов: 6 (шесть) месяцев с даты принятия настоящего решения.

4. Внести соответствующие изменения в Устав Общества.

5. Поручить Генеральному директору осуществить государственную регистрацию изменений.

Решение принято единогласно.

Подписи участников:
_____________________
        """,
        "workflow": ["generate", "sign", "notarize", "submit_fns"],
        "output_format": "docx"
    },

    # =========================================================================
    # ADDRESS CHANGES
    # =========================================================================

    "address_change_decision": {
        "id": "address_change_decision",
        "name": "Решение о смене юридического адреса",
        "name_en": "Legal Address Change Decision",
        "category": "corporate",
        "subcategory": "changes",
        "description": "Решение о смене места нахождения общества",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "old_address", "label": "Старый адрес", "type": "text", "required": True},
            {"name": "new_address", "label": "Новый адрес", "type": "text", "required": True},
            {"name": "decision_date", "label": "Дата решения", "type": "date", "required": True},
        ],
        "template_content": """
РЕШЕНИЕ № ___
общего собрания участников (единственного участника)
ООО «{{company_name}}»

г. Москва                                                     «{{decision_date|format_date}}»

ПОВЕСТКА ДНЯ:
1. О смене места нахождения Общества.
2. О внесении изменений в Устав.

РЕШИЛИ:

1. Изменить место нахождения ООО «{{company_name}}»:
   - Старый адрес: {{old_address}}
   - Новый адрес: {{new_address}}

2. Внести соответствующие изменения в Устав Общества.

3. Поручить Генеральному директору:
   - осуществить государственную регистрацию изменений;
   - уведомить контрагентов о смене адреса;
   - внести изменения в банковские реквизиты.

Решение принято единогласно.

Подписи участников:
_____________________
        """,
        "workflow": ["generate", "sign", "submit_fns_step1", "await_15_days", "submit_fns_step2"],
        "output_format": "docx"
    },

    # =========================================================================
    # LIQUIDATION
    # =========================================================================

    "liquidation_decision": {
        "id": "liquidation_decision",
        "name": "Решение о ликвидации ООО",
        "name_en": "LLC Liquidation Decision",
        "category": "corporate",
        "subcategory": "liquidation",
        "description": "Решение участников о добровольной ликвидации общества",
        "required_fields": [
            {"name": "company_name", "label": "Наименование ООО", "type": "text", "required": True},
            {"name": "liquidator_name", "label": "ФИО ликвидатора", "type": "text", "required": True},
            {"name": "liquidator_passport", "label": "Паспорт ликвидатора", "type": "text", "required": True},
            {"name": "decision_date", "label": "Дата решения", "type": "date", "required": True},
            {"name": "liquidation_deadline", "label": "Срок ликвидации", "type": "text", "required": True},
        ],
        "template_content": """
РЕШЕНИЕ № ___
общего собрания участников (единственного участника)
ООО «{{company_name}}»

г. Москва                                                     «{{decision_date|format_date}}»

ПОВЕСТКА ДНЯ:
1. О добровольной ликвидации Общества.
2. О назначении ликвидатора.
3. О порядке и сроках ликвидации.

РЕШИЛИ:

1. Ликвидировать ООО «{{company_name}}» в добровольном порядке.

2. Назначить ликвидатором {{liquidator_name}}, паспорт {{liquidator_passport}}.

3. Установить срок ликвидации: {{liquidation_deadline}}.

4. Поручить ликвидатору:
   - уведомить регистрирующий орган о начале ликвидации;
   - опубликовать сведения о ликвидации в журнале «Вестник государственной регистрации»;
   - выявить кредиторов и уведомить их о ликвидации;
   - взыскать дебиторскую задолженность;
   - составить промежуточный и ликвидационный балансы;
   - произвести расчеты с кредиторами;
   - распределить оставшееся имущество между участниками.

Решение принято единогласно.

Подписи участников:
_____________________
        """,
        "workflow": ["generate", "sign", "notarize", "submit_fns_r15001", "publish_vestnik", "wait_creditors", "interim_balance", "final_balance", "close"],
        "output_format": "docx"
    },
}


def get_corporate_templates() -> Dict[str, Any]:
    """Return all corporate templates."""
    return CORPORATE_TEMPLATES


def get_template(template_id: str) -> Dict[str, Any]:
    """Get a specific template by ID."""
    return CORPORATE_TEMPLATES.get(template_id)


def list_templates_by_subcategory(subcategory: str) -> List[Dict[str, Any]]:
    """List templates by subcategory."""
    return [
        t for t in CORPORATE_TEMPLATES.values()
        if t.get("subcategory") == subcategory
    ]


from enum import Enum


class CorporateDocType(str, Enum):
    """Corporate document types."""
    CHARTER_OOO = "charter_ooo"
    FORMATION_DECISION_SOLE = "formation_decision_sole"
    FORMATION_DECISION_MULTIPLE = "formation_decision_multiple"
    FOUNDERS_AGREEMENT = "founders_agreement"
    CAPITAL_INCREASE_DECISION = "capital_increase_decision"
    SHARE_SALE_AGREEMENT = "share_sale_agreement"
    SHAREHOLDER_MEETING_MINUTES = "shareholder_meeting_minutes"
    DIVIDEND_RESOLUTION = "dividend_resolution"
    DIRECTOR_APPOINTMENT_ORDER = "director_appointment_order"
    POWER_OF_ATTORNEY = "power_of_attorney"
    CHARTER_AMENDMENTS = "charter_amendments"
    SUBSIDIARY_FORMATION = "subsidiary_formation"
    BRANCH_REGULATIONS = "branch_regulations"
    REORGANIZATION_DECISION = "reorganization_decision"
    VOLUNTARY_LIQUIDATION = "voluntary_liquidation"


class CorporateTemplateService:
    """Service for corporate document templates."""

    @staticmethod
    def list_templates() -> List[Dict[str, Any]]:
        """List all corporate templates."""
        return [
            {"type": tid, "name": t["name"], "category": "corporate"}
            for tid, t in CORPORATE_TEMPLATES.items()
        ]

    @staticmethod
    def get_template(doc_type: CorporateDocType) -> Dict[str, Any]:
        """Get template by document type."""
        return CORPORATE_TEMPLATES.get(doc_type.value)

    @staticmethod
    def generate(doc_type: CorporateDocType, data: Dict[str, Any]) -> str:
        """Generate document from template."""
        template = CORPORATE_TEMPLATES.get(doc_type.value)
        if not template:
            raise ValueError(f"Template not found: {doc_type}")

        from jinja2 import Template
        content = template.get("template_content", "")
        tpl = Template(content)
        return tpl.render(**data)

    @staticmethod
    def generate_document(doc_type: CorporateDocType, data: Dict[str, Any]) -> str:
        """Generate document from template (alias for generate)."""
        return CorporateTemplateService.generate(doc_type, data)
