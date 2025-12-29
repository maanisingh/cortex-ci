"""
SME Document Templates - Phase 12: Legal and Intellectual Property Documents
Russian legal and IP protection templates

Document Types:
1. Trademark Application (Заявка на товарный знак)
2. Copyright Registration (Регистрация авторских прав)
3. Patent Application Cover (Заявка на патент)
4. Know-how Registration (Регистрация ноу-хау)
5. Cease and Desist Letter (Претензия о нарушении прав)
6. Claim/Lawsuit Draft (Исковое заявление)
7. Response to Claim (Отзыв на иск)
8. Settlement Agreement (Мировое соглашение)
9. Legal Opinion (Юридическое заключение)
10. Notarized Power of Attorney (Нотариальная доверенность)
11. Complaint to Government (Жалоба в госорган)
12. Appeal/Cassation (Апелляционная/кассационная жалоба)
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel


class LegalDocType(str, Enum):
    TRADEMARK_APPLICATION = "trademark_application"
    COPYRIGHT_REGISTRATION = "copyright_registration"
    PATENT_APPLICATION = "patent_application"
    KNOWHOW_REGISTRATION = "knowhow_registration"
    CEASE_DESIST = "cease_desist"
    LAWSUIT = "lawsuit"
    CLAIM_RESPONSE = "claim_response"
    SETTLEMENT = "settlement"
    LEGAL_OPINION = "legal_opinion"
    NOTARIZED_POA = "notarized_poa"
    GOVERNMENT_COMPLAINT = "government_complaint"
    APPEAL = "appeal"


class IPType(str, Enum):
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    PATENT = "patent"
    UTILITY_MODEL = "utility_model"
    INDUSTRIAL_DESIGN = "industrial_design"
    TRADE_SECRET = "trade_secret"


class CourtType(str, Enum):
    ARBITRATION = "arbitrazh"  # Арбитражный суд
    GENERAL = "general"  # Суд общей юрисдикции
    IP_COURT = "ip_court"  # Суд по интеллектуальным правам


# =============================================================================
# Template 1: Trademark Application
# =============================================================================

TRADEMARK_APPLICATION_TEMPLATE = """
                                             В Федеральный институт
                                             промышленной собственности (ФИПС)
                                             123995, Москва, Бережковская наб., 30, к.1

                         ЗАЯВКА НА РЕГИСТРАЦИЮ ТОВАРНОГО ЗНАКА
                                    (знака обслуживания)

┌───────────────────────────────────────────────────────────────────────────────┐
│                         1. ЗАЯВИТЕЛЬ                                          │
├───────────────────────────────────────────────────────────────────────────────┤
│ Полное наименование: {applicant_name}                                         │
│ Сокращённое наименование: {applicant_short_name}                              │
│ ОГРН: {ogrn}                            │ ИНН: {inn}                          │
│ Адрес места нахождения: {legal_address}                                       │
│ Адрес для переписки: {mailing_address}                                        │
│ Код страны: RU                                                                │
│ Телефон: {phone}                        │ E-mail: {email}                     │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                    2. ЗАЯВЛЯЕМОЕ ОБОЗНАЧЕНИЕ                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│ Вид товарного знака:                                                          │
│ [ ] Словесный   [ ] Изобразительный   [ ] Комбинированный                     │
│ [ ] Объёмный    [ ] Звуковой          [ ] Иной: ______________                │
│                                                                               │
│ Описание заявляемого обозначения:                                             │
│ {trademark_description}                                                       │
│                                                                               │
│ Изображение обозначения: [Приложение № 1]                                     │
│                                                                               │
│ Указание цвета или цветового сочетания: {colors}                              │
│                                                                               │
│ Транслитерация (для нелатинских букв): {transliteration}                      │
│ Перевод (для иностранных слов): {translation}                                 │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│              3. ПЕРЕЧЕНЬ ТОВАРОВ И УСЛУГ (по МКТУ)                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│ Класс {class_1}: {goods_services_1}                                           │
│                                                                               │
│ Класс {class_2}: {goods_services_2}                                           │
│                                                                               │
│ Класс {class_3}: {goods_services_3}                                           │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                    4. ДОПОЛНИТЕЛЬНЫЕ СВЕДЕНИЯ                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│ Приоритет испрашивается:                                                      │
│ [ ] по дате подачи заявки в Роспатент                                         │
│ [ ] по дате подачи первой заявки в государстве — участнике Парижской          │
│     конвенции (конвенционный приоритет)                                       │
│     Страна: _________ № заявки: _________ Дата подачи: _________              │
│ [ ] по дате начала открытого показа на выставке                               │
│     Название выставки: _________________________________________              │
│                                                                               │
│ Неохраняемые элементы: {disclaimers}                                          │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                         5. ПРИЛОЖЕНИЯ                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ [ ] Изображение заявляемого обозначения — {image_copies} экз.                 │
│ [ ] Документ об уплате пошлины                                                │
│ [ ] Доверенность (при подаче через представителя)                             │
│ [ ] Устав коллективного знака (для коллективного знака)                       │
│ [ ] Иные документы: {other_attachments}                                       │
└───────────────────────────────────────────────────────────────────────────────┘

Подпись заявителя / представителя: _____________________ / {signatory_name} /

Дата: «{day}» {month} {year} г.

М.П.
"""


# =============================================================================
# Template 2: Copyright Registration
# =============================================================================

COPYRIGHT_REGISTRATION_TEMPLATE = """
                         АКТ РЕГИСТРАЦИИ АВТОРСКОГО ПРОИЗВЕДЕНИЯ
                              (внутренний документ организации)

{organization_name}
ИНН: {inn}  ОГРН: {ogrn}
Адрес: {address}

                              АКТ № {act_number}
                    о создании и регистрации произведения

г. {city}                                           «{day}» {month} {year} г.

Настоящим подтверждается, что:

┌───────────────────────────────────────────────────────────────────────────────┐
│                    1. СВЕДЕНИЯ О ПРОИЗВЕДЕНИИ                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│ Название произведения: {work_title}                                           │
│                                                                               │
│ Вид произведения:                                                             │
│ [ ] Литературное   [ ] Программа для ЭВМ   [ ] База данных                    │
│ [ ] Аудиовизуальное [ ] Музыкальное        [ ] Фотографическое                │
│ [ ] Иное: {other_type}                                                        │
│                                                                               │
│ Краткое описание: {work_description}                                          │
│                                                                               │
│ Дата создания: {creation_date}                                                │
│ Дата первого обнародования: {publication_date}                                │
│ Место обнародования: {publication_place}                                      │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                    2. СВЕДЕНИЯ ОБ АВТОРЕ(АХ)                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│ Автор 1:                                                                      │
│ ФИО: {author1_name}                                                           │
│ Дата рождения: {author1_dob}                                                  │
│ Гражданство: {author1_citizenship}                                            │
│ Контактные данные: {author1_contacts}                                         │
│ Творческий вклад: {author1_contribution}                                      │
│                                                                               │
│ Автор 2 (при наличии):                                                        │
│ ФИО: {author2_name}                                                           │
│ Творческий вклад: {author2_contribution}                                      │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│              3. ПРАВООБЛАДАТЕЛЬ (ОБЛАДАТЕЛЬ ИСКЛЮЧИТЕЛЬНОГО ПРАВА)            │
├───────────────────────────────────────────────────────────────────────────────┤
│ Наименование/ФИО: {rights_holder}                                             │
│                                                                               │
│ Основание возникновения права:                                                │
│ [ ] Создание служебного произведения (ст. 1295 ГК РФ)                          │
│ [ ] Договор об отчуждении исключительного права                               │
│ [ ] Договор авторского заказа                                                 │
│ [ ] Иное: {rights_basis}                                                      │
│                                                                               │
│ Реквизиты договора: {contract_details}                                        │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                    4. ДЕПОНИРОВАНИЕ                                           │
├───────────────────────────────────────────────────────────────────────────────┤
│ Экземпляр произведения:                                                       │
│ [ ] На бумажном носителе — {paper_copies} экз.                                │
│ [ ] На электронном носителе — {digital_copies} экз.                           │
│                                                                               │
│ Место хранения: {storage_location}                                            │
│ Ответственный за хранение: {storage_responsible}                              │
│                                                                               │
│ Хэш-сумма файла (для электронных произведений):                               │
│ MD5: {md5_hash}                                                               │
│ SHA-256: {sha256_hash}                                                        │
└───────────────────────────────────────────────────────────────────────────────┘

Комиссия в составе:
- {commission_member1}
- {commission_member2}
- {commission_member3}

подтверждает факт создания указанного произведения и его регистрацию
во внутреннем реестре организации.

Подписи членов комиссии:

_____________________ / {member1_name} /
_____________________ / {member2_name} /
_____________________ / {member3_name} /

М.П.
"""


# =============================================================================
# Template 3: Cease and Desist Letter
# =============================================================================

CEASE_DESIST_TEMPLATE = """
                              ПРЕТЕНЗИЯ
              о нарушении исключительных прав на {ip_type}

                                             Кому: {recipient_name}
                                             Адрес: {recipient_address}
                                             ИНН: {recipient_inn}

От: {claimant_name}
ИНН: {claimant_inn}
Адрес: {claimant_address}
Тел.: {claimant_phone}
E-mail: {claimant_email}

                         Исх. № {outgoing_number}
                         от «{day}» {month} {year} г.

Уважаемые господа!

{claimant_name} является обладателем исключительного права на:
{ip_description}

Основание возникновения права:
{rights_basis}

1. СУТЬ НАРУШЕНИЯ:

Нами установлено, что {recipient_name} без согласия правообладателя
осуществляет следующие действия:

{violation_description}

Данные действия являются нарушением статей {violated_articles} Гражданского
кодекса Российской Федерации.

Доказательства нарушения:
{evidence_description}

2. ТРЕБОВАНИЯ:

На основании изложенного, в соответствии со статьями 12, 1250, 1252, {additional_articles}
Гражданского кодекса Российской Федерации, требуем:

{demands_list}

3. СУММА КОМПЕНСАЦИИ / ВОЗМЕЩЕНИЯ УБЫТКОВ:

В соответствии со ст. {compensation_article} ГК РФ требуем выплатить компенсацию
в размере {compensation_amount} ({compensation_amount_words}) рублей.

Расчёт компенсации/убытков:
{compensation_calculation}

4. СРОК ИСПОЛНЕНИЯ:

Требования должны быть выполнены в течение {response_period} календарных дней
с момента получения настоящей претензии.

5. ПОСЛЕДСТВИЯ НЕИСПОЛНЕНИЯ:

В случае неудовлетворения требований в установленный срок мы будем вынуждены
обратиться в {court_name} для защиты нарушенных прав.

Помимо указанных требований, мы будем требовать:
- возмещения судебных расходов;
- взыскания расходов на представителя;
- {additional_consequences}

6. ПРИЛОЖЕНИЯ:
{attachments_list}

Ответ на претензию просим направить по адресу: {response_address}
либо по электронной почте: {response_email}

С уважением,

{signatory_position}
_____________________ / {signatory_name} /

М.П.
"""


# =============================================================================
# Template 4: Lawsuit Draft (Исковое заявление)
# =============================================================================

LAWSUIT_TEMPLATE = """
                                             В {court_name}
                                             Адрес: {court_address}

                                             Истец: {plaintiff_name}
                                             ИНН: {plaintiff_inn}
                                             Адрес: {plaintiff_address}
                                             Тел.: {plaintiff_phone}
                                             E-mail: {plaintiff_email}

                                             Ответчик: {defendant_name}
                                             ИНН: {defendant_inn}
                                             Адрес: {defendant_address}

                                             Цена иска: {claim_amount} рублей
                                             Госпошлина: {state_duty} рублей

                         ИСКОВОЕ ЗАЯВЛЕНИЕ
                    {claim_subject}

{plaintiff_name} (далее — «Истец») обращается в суд с иском к {defendant_name}
(далее — «Ответчик») со следующими требованиями:

I. ОБСТОЯТЕЛЬСТВА ДЕЛА:

{case_circumstances}

II. ПРАВОВОЕ ОБОСНОВАНИЕ:

{legal_grounds}

На основании вышеизложенного, Истец имеет право требовать:
{rights_basis}

III. РАСЧЁТ ИСКОВЫХ ТРЕБОВАНИЙ:

{claim_calculation}

IV. СОБЛЮДЕНИЕ ДОСУДЕБНОГО ПОРЯДКА:

Истцом соблюдён обязательный досудебный порядок урегулирования спора:
{pretrial_procedure}

Претензия от {pretrial_date} оставлена без ответа / отклонена.

V. ИСКОВЫЕ ТРЕБОВАНИЯ:

На основании изложенного, руководствуясь статьями {legal_articles}
Гражданского кодекса РФ, статьями {procedure_articles} Арбитражного
процессуального кодекса РФ,

                              ПРОШУ:

{claim_demands}

VI. ПРИЛОЖЕНИЯ:

1. Копия искового заявления для Ответчика — {copies_count} экз.
2. Документ об уплате государственной пошлины.
3. Документы, подтверждающие соблюдение досудебного порядка.
4. Доверенность представителя (при необходимости).
5. Копия свидетельства о государственной регистрации Истца.
6. Выписка из ЕГРЮЛ на Истца и Ответчика.
{additional_attachments}

Истец: {plaintiff_name}

{signatory_position}
_____________________ / {signatory_name} /

«{day}» {month} {year} г.

М.П.
"""


# =============================================================================
# Template 5: Settlement Agreement (Мировое соглашение)
# =============================================================================

SETTLEMENT_AGREEMENT_TEMPLATE = """
                              МИРОВОЕ СОГЛАШЕНИЕ

по делу № {case_number}

г. {city}                                           «{day}» {month} {year} г.

{party1_name}, именуемое в дальнейшем «Сторона 1» (Истец/Ответчик),
в лице {party1_representative}, действующего на основании {party1_basis},
с одной стороны, и

{party2_name}, именуемое в дальнейшем «Сторона 2» (Ответчик/Истец),
в лице {party2_representative}, действующего на основании {party2_basis},
с другой стороны,

совместно именуемые «Стороны», являющиеся участниками дела № {case_number},
рассматриваемого {court_name},

в целях урегулирования спора заключили настоящее Мировое соглашение
о нижеследующем:

1. ПРЕДМЕТ МИРОВОГО СОГЛАШЕНИЯ:

1.1. Стороны договорились урегулировать спор на следующих условиях:
{settlement_terms}

2. ОБЯЗАТЕЛЬСТВА СТОРОН:

2.1. Сторона 1 обязуется:
{party1_obligations}

2.2. Сторона 2 обязуется:
{party2_obligations}

3. ПОРЯДОК И СРОКИ ИСПОЛНЕНИЯ:

3.1. {execution_schedule}

3.2. Платежи производятся по следующим реквизитам:
{payment_details}

4. СУДЕБНЫЕ РАСХОДЫ:

4.1. Судебные расходы, включая государственную пошлину и расходы
на представителей, распределяются следующим образом:
{costs_distribution}

5. ПОСЛЕДСТВИЯ УТВЕРЖДЕНИЯ:

5.1. Стороны понимают и соглашаются с тем, что:
- утверждение мирового соглашения судом влечёт прекращение производства по делу;
- повторное обращение в суд по спору между теми же лицами, о том же предмете
  и по тем же основаниям не допускается;
- мировое соглашение может быть принудительно исполнено на основании
  исполнительного листа.

6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ:

6.1. Мировое соглашение вступает в силу с момента его утверждения судом.

6.2. Мировое соглашение составлено в трёх экземплярах: по одному для каждой
из Сторон и один экземпляр для материалов дела.

6.3. Стороны просят суд утвердить настоящее Мировое соглашение и прекратить
производство по делу № {case_number}.

ПОДПИСИ СТОРОН:

СТОРОНА 1:                               СТОРОНА 2:
{party1_name}                             {party2_name}

_____________________ / {party1_signatory} /   _____________________ / {party2_signatory} /

М.П.                                      М.П.
"""


# =============================================================================
# Template 6: Legal Opinion
# =============================================================================

LEGAL_OPINION_TEMPLATE = """
                         ЮРИДИЧЕСКОЕ ЗАКЛЮЧЕНИЕ

{organization_name}
Юридический отдел / Внешний юрист

                              ЗАКЛЮЧЕНИЕ № {opinion_number}

«{day}» {month} {year} г.

По запросу: {requester_name}
От: {request_date}
Вх. № {incoming_number}

ПРЕДМЕТ ЗАКЛЮЧЕНИЯ:
{subject_matter}

I. ФАКТИЧЕСКИЕ ОБСТОЯТЕЛЬСТВА:

{factual_background}

II. ПОСТАВЛЕННЫЕ ВОПРОСЫ:

{questions_posed}

III. ПРИМЕНИМОЕ ЗАКОНОДАТЕЛЬСТВО:

{applicable_law}

IV. ПРАВОВОЙ АНАЛИЗ:

{legal_analysis}

V. ВЫВОДЫ:

{conclusions}

VI. РЕКОМЕНДАЦИИ:

{recommendations}

VII. ОГОВОРКИ:

Настоящее заключение подготовлено исключительно для внутреннего использования
{recipient_organization} и основывается на информации и документах,
предоставленных Заказчиком.

Заключение не может рассматриваться как гарантия определённого исхода дела
в суде или государственном органе.

Заключение актуально на дату его составления. Изменения законодательства
или судебной практики могут повлиять на выводы.

Юрист / Начальник юридического отдела:

_____________________ / {lawyer_name} /
{lawyer_position}
{lawyer_registration}

Дата: «{day}» {month} {year} г.
"""


# =============================================================================
# Template 7: Notarized Power of Attorney
# =============================================================================

NOTARIZED_POA_TEMPLATE = """
                         ДОВЕРЕННОСТЬ

{city}                                    «{day}» {month} {year} года

Настоящая доверенность удостоверена мной, {notary_name}, нотариусом
{notary_district}, {notary_address}.

{principal_name}, именуемое в дальнейшем «Доверитель»,
ИНН: {principal_inn}, ОГРН: {principal_ogrn},
адрес: {principal_address},
в лице {principal_representative_name}, действующего на основании {principal_basis},

настоящей доверенностью уполномочивает:

{attorney_name}
{attorney_position}
паспорт {attorney_passport_series} № {attorney_passport_number},
выдан {attorney_passport_issued_by}, {attorney_passport_date},
зарегистрирован по адресу: {attorney_address}

представлять интересы Доверителя:

{scope_of_authority}

Для выполнения указанных полномочий представителю предоставляется право:

{specific_powers}

Доверенность выдана {substitution_clause} права передоверия.

Срок действия доверенности: {validity_period} / до «{expiry_date}».

Подпись представителя {attorney_name}: _____________________ удостоверяю.

{principal_name}
в лице {principal_representative_name}

Подпись: _____________________

М.П.

                    УДОСТОВЕРИТЕЛЬНАЯ НАДПИСЬ НОТАРИУСА

{notary_certification}

Зарегистрировано в реестре за № {registry_number}

Взыскано государственной пошлины (нотариального тарифа): {notary_fee} рублей

Нотариус: _____________________ / {notary_name} /

М.П.
"""


# =============================================================================
# Template 8: Government Complaint (Жалоба в госорган)
# =============================================================================

GOVERNMENT_COMPLAINT_TEMPLATE = """
                                             В {government_body}
                                             Адрес: {government_address}

                                             Заявитель: {complainant_name}
                                             ИНН: {complainant_inn}
                                             Адрес: {complainant_address}
                                             Тел.: {complainant_phone}
                                             E-mail: {complainant_email}

                                             Лицо, действия которого
                                             обжалуются: {respondent_name}
                                             ИНН: {respondent_inn}
                                             Адрес: {respondent_address}

                              ЖАЛОБА

«{day}» {month} {year} г.

{complainant_name} (далее — «Заявитель») просит рассмотреть жалобу на действия
(бездействие) {respondent_name}.

I. ОБСТОЯТЕЛЬСТВА ДЕЛА:

{case_circumstances}

II. НАРУШЕННЫЕ НОРМЫ:

{violated_norms}

III. НАРУШЕННЫЕ ПРАВА ЗАЯВИТЕЛЯ:

{violated_rights}

IV. ДОКАЗАТЕЛЬСТВА:

{evidence_list}

V. ТРЕБОВАНИЯ:

На основании изложенного, в соответствии с {legal_basis}, прошу:

{demands}

VI. ПРИЛОЖЕНИЯ:

{attachments_list}

Ответ прошу направить по адресу: {response_address}
либо по электронной почте: {response_email}

С уважением,

{signatory_position}
_____________________ / {signatory_name} /

М.П.
"""


# =============================================================================
# Template 9: Appeal (Апелляционная жалоба)
# =============================================================================

APPEAL_TEMPLATE = """
                                             В {appellate_court}
                                             через {court_of_first_instance}
                                             Адрес: {court_address}

                                             Дело № {case_number}

                                             Апеллянт (Истец/Ответчик):
                                             {appellant_name}
                                             ИНН: {appellant_inn}
                                             Адрес: {appellant_address}
                                             Тел.: {appellant_phone}

                                             Другая сторона:
                                             {appellee_name}
                                             Адрес: {appellee_address}

                                             Госпошлина: {state_duty} рублей

                    АПЕЛЛЯЦИОННАЯ ЖАЛОБА
         на решение {court_of_first_instance} от {judgment_date}
                    по делу № {case_number}

Решением {court_of_first_instance} от {judgment_date} по делу № {case_number}
{judgment_summary}

С указанным решением Апеллянт не согласен по следующим основаниям:

I. СУЩЕСТВЕННЫЕ НАРУШЕНИЯ НОРМ МАТЕРИАЛЬНОГО ПРАВА:

{material_law_violations}

II. СУЩЕСТВЕННЫЕ НАРУШЕНИЯ НОРМ ПРОЦЕССУАЛЬНОГО ПРАВА:

{procedural_violations}

III. НЕСООТВЕТСТВИЕ ВЫВОДОВ СУДА ОБСТОЯТЕЛЬСТВАМ ДЕЛА:

{factual_errors}

IV. НЕПОЛНОЕ ВЫЯСНЕНИЕ ОБСТОЯТЕЛЬСТВ, ИМЕЮЩИХ ЗНАЧЕНИЕ ДЛЯ ДЕЛА:

{incomplete_investigation}

На основании изложенного, руководствуясь статьями {apc_articles}
Арбитражного процессуального кодекса РФ,

                              ПРОШУ:

{appeal_demands}

ПРИЛОЖЕНИЯ:

1. Копия обжалуемого решения.
2. Документ об уплате государственной пошлины.
3. Копия апелляционной жалобы для {copies_count} лиц.
4. Доверенность представителя (при необходимости).
{additional_attachments}

Апеллянт: {appellant_name}

{signatory_position}
_____________________ / {signatory_name} /

«{day}» {month} {year} г.

М.П.
"""


# =============================================================================
# Remaining Legal Templates (Shorter versions)
# =============================================================================

PATENT_APPLICATION_COVER_TEMPLATE = """
                                             В Федеральный институт
                                             промышленной собственности (ФИПС)

                    ЗАЯВКА НА ВЫДАЧУ ПАТЕНТА
                    на {patent_type}

┌───────────────────────────────────────────────────────────────────────────────┐
│ Заявитель: {applicant_name}                                                   │
│ ИНН: {inn}  ОГРН: {ogrn}                                                      │
│ Адрес: {address}                                                              │
├───────────────────────────────────────────────────────────────────────────────┤
│ Название: {invention_title}                                                   │
│ Индекс МПК: {ipc_index}                                                       │
├───────────────────────────────────────────────────────────────────────────────┤
│ Автор(ы): {inventors}                                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ Приоритет испрашивается: [ ] по дате подачи                                   │
│                          [ ] конвенционный (страна: _____ дата: _____)        │
└───────────────────────────────────────────────────────────────────────────────┘

Приложения: Описание, Формула, Реферат, Чертежи, Документ об уплате пошлины

_____________________ / {signatory_name} /
Дата: «{day}» {month} {year} г.    М.П.
"""


KNOWHOW_REGISTRATION_TEMPLATE = """
               АКТ О ВВЕДЕНИИ РЕЖИМА КОММЕРЧЕСКОЙ ТАЙНЫ (НОУ-ХАУ)

{organization_name}

                              АКТ № {act_number}
                    от «{day}» {month} {year} г.

1. Наименование секрета производства: {knowhow_name}

2. Описание: {knowhow_description}

3. Коммерческая ценность: {commercial_value}

4. Меры по охране:
{protection_measures}

5. Перечень лиц, имеющих доступ: {authorized_persons}

6. Место хранения материальных носителей: {storage_location}

7. Срок действия режима: {validity_period}

Утверждаю введение режима коммерческой тайны.

Руководитель: _____________________ / {director_name} /
М.П.
"""


CLAIM_RESPONSE_TEMPLATE = """
                                             В {court_name}
                                             Дело № {case_number}

                                             Ответчик: {defendant_name}
                                             Адрес: {defendant_address}

                                             Истец: {plaintiff_name}
                                             Адрес: {plaintiff_address}

                    ОТЗЫВ НА ИСКОВОЕ ЗАЯВЛЕНИЕ

{defendant_name} (далее — «Ответчик») представляет отзыв на исковое заявление
{plaintiff_name} от {claim_date}.

I. ПОЗИЦИЯ ПО СУЩЕСТВУ ИСКА:

{substantive_position}

II. ВОЗРАЖЕНИЯ:

{objections}

III. ПРАВОВОЕ ОБОСНОВАНИЕ:

{legal_grounds}

IV. ПРОСИТЕЛЬНАЯ ЧАСТЬ:

Прошу: {demands}

Приложения: {attachments_list}

Ответчик: {defendant_name}
_____________________ / {signatory_name} /
«{day}» {month} {year} г.    М.П.
"""


# =============================================================================
# Legal Template Service
# =============================================================================

class LegalTemplateService:
    """Service for generating legal and IP documents."""

    TEMPLATES = {
        LegalDocType.TRADEMARK_APPLICATION: TRADEMARK_APPLICATION_TEMPLATE,
        LegalDocType.COPYRIGHT_REGISTRATION: COPYRIGHT_REGISTRATION_TEMPLATE,
        LegalDocType.PATENT_APPLICATION: PATENT_APPLICATION_COVER_TEMPLATE,
        LegalDocType.KNOWHOW_REGISTRATION: KNOWHOW_REGISTRATION_TEMPLATE,
        LegalDocType.CEASE_DESIST: CEASE_DESIST_TEMPLATE,
        LegalDocType.LAWSUIT: LAWSUIT_TEMPLATE,
        LegalDocType.CLAIM_RESPONSE: CLAIM_RESPONSE_TEMPLATE,
        LegalDocType.SETTLEMENT: SETTLEMENT_AGREEMENT_TEMPLATE,
        LegalDocType.LEGAL_OPINION: LEGAL_OPINION_TEMPLATE,
        LegalDocType.NOTARIZED_POA: NOTARIZED_POA_TEMPLATE,
        LegalDocType.GOVERNMENT_COMPLAINT: GOVERNMENT_COMPLAINT_TEMPLATE,
        LegalDocType.APPEAL: APPEAL_TEMPLATE,
    }

    TEMPLATE_NAMES = {
        LegalDocType.TRADEMARK_APPLICATION: "Заявка на товарный знак",
        LegalDocType.COPYRIGHT_REGISTRATION: "Регистрация авторских прав",
        LegalDocType.PATENT_APPLICATION: "Заявка на патент",
        LegalDocType.KNOWHOW_REGISTRATION: "Регистрация ноу-хау",
        LegalDocType.CEASE_DESIST: "Претензия о нарушении прав",
        LegalDocType.LAWSUIT: "Исковое заявление",
        LegalDocType.CLAIM_RESPONSE: "Отзыв на иск",
        LegalDocType.SETTLEMENT: "Мировое соглашение",
        LegalDocType.LEGAL_OPINION: "Юридическое заключение",
        LegalDocType.NOTARIZED_POA: "Нотариальная доверенность",
        LegalDocType.GOVERNMENT_COMPLAINT: "Жалоба в госорган",
        LegalDocType.APPEAL: "Апелляционная жалоба",
    }

    @classmethod
    def get_template(cls, doc_type: LegalDocType) -> str:
        return cls.TEMPLATES.get(doc_type, "")

    @classmethod
    def get_template_name(cls, doc_type: LegalDocType) -> str:
        return cls.TEMPLATE_NAMES.get(doc_type, "")

    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        return [
            {"type": dt.value, "name": cls.TEMPLATE_NAMES[dt]}
            for dt in LegalDocType
        ]

    @classmethod
    def generate_document(cls, doc_type: LegalDocType, data: Dict[str, Any]) -> str:
        template = cls.get_template(doc_type)
        if not template:
            raise ValueError(f"Unknown document type: {doc_type}")

        if "day" not in data:
            today = date.today()
            data["day"] = str(today.day).zfill(2)
            data["month"] = cls._get_russian_month(today.month)
            data["year"] = str(today.year)

        try:
            return template.format(**data)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

    @staticmethod
    def _get_russian_month(month: int) -> str:
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        return months.get(month, "")
