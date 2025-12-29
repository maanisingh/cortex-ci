"""
SME Document Templates - Phases 14-21: Specialized Documents
Russian specialized business document templates

Categories:
- Phase 14: Real Estate (12 templates)
- Phase 15: Banking/Finance (15 templates)
- Phase 16: Government Tenders 44-ФЗ/223-ФЗ (15 templates)
- Phase 17: Licenses/Permits (10 templates)
- Phase 18: Environmental/Safety (12 templates)
- Phase 19: Vehicles/Equipment (8 templates)
- Phase 20: Quality/Certification (10 templates)
- Phase 21: Crisis/Restructuring (8 templates)

Total: 90 templates
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel


# =============================================================================
# ENUMS FOR ALL SPECIALIZED CATEGORIES
# =============================================================================

class RealEstateDocType(str, Enum):
    PURCHASE_SALE_REAL_ESTATE = "purchase_sale_real_estate"
    COMMERCIAL_LEASE = "commercial_lease"
    LAND_LEASE = "land_lease"
    MORTGAGE_AGREEMENT = "mortgage_agreement"
    PROPERTY_MANAGEMENT = "property_management"
    CONSTRUCTION_INVESTMENT = "construction_investment"
    PRELIMINARY_AGREEMENT = "preliminary_agreement"
    DEED_OF_GIFT = "deed_of_gift"
    PROPERTY_VALUATION = "property_valuation"
    EASEMENT_AGREEMENT = "easement_agreement"
    HANDOVER_ACT = "handover_act"
    CADASTRAL_APPLICATION = "cadastral_application"


class BankingDocType(str, Enum):
    CREDIT_APPLICATION = "credit_application"
    LOAN_AGREEMENT_BANK = "loan_agreement_bank"
    OVERDRAFT_AGREEMENT = "overdraft"
    BANK_GUARANTEE = "bank_guarantee"
    FACTORING_AGREEMENT = "factoring"
    LEASING_AGREEMENT = "leasing"
    ACCOUNT_OPENING = "account_opening"
    LETTER_OF_CREDIT = "letter_of_credit"
    BILL_OF_EXCHANGE = "bill_of_exchange"
    PLEDGE_AGREEMENT_BANK = "pledge_bank"
    SURETY_AGREEMENT_BANK = "surety_bank"
    COMFORT_LETTER = "comfort_letter"
    CREDIT_LINE = "credit_line"
    PROJECT_FINANCING = "project_financing"
    SYNDICATED_LOAN = "syndicated_loan"


class GovTenderDocType(str, Enum):
    TENDER_APPLICATION_44FZ = "tender_44fz"
    TENDER_APPLICATION_223FZ = "tender_223fz"
    BANK_GUARANTEE_TENDER = "bank_guarantee_tender"
    CONTRACT_44FZ = "contract_44fz"
    SUBCONTRACT_44FZ = "subcontract_44fz"
    ACCEPTANCE_ACT_44FZ = "acceptance_act_44fz"
    CLAIM_FAS = "claim_fas"
    PERFORMANCE_BOND = "performance_bond"
    WARRANTY_BOND = "warranty_bond"
    PRICE_JUSTIFICATION = "price_justification"
    TECHNICAL_PROPOSAL = "technical_proposal"
    QUALIFICATION_DOCS = "qualification_docs"
    JOINT_TENDER = "joint_tender"
    TENDER_DISPUTE = "tender_dispute"
    CONTRACT_MODIFICATION = "contract_modification"


class LicenseDocType(str, Enum):
    LICENSE_APPLICATION = "license_application"
    SRO_APPLICATION = "sro_application"
    DECLARATION_CONFORMITY = "declaration_conformity"
    CERTIFICATE_APPLICATION = "certificate_application"
    NOTIFICATION_ACTIVITY = "notification_activity"
    ACCREDITATION_APPLICATION = "accreditation"
    PERMIT_APPLICATION = "permit_application"
    RENEWAL_APPLICATION = "renewal"
    LICENSE_CHANGE = "license_change"
    LICENSE_TERMINATION = "license_termination"


class EnvironmentalDocType(str, Enum):
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    WASTE_MANAGEMENT = "waste_management"
    EMISSION_PERMIT = "emission_permit"
    WATER_USE_PERMIT = "water_use"
    HAZARDOUS_WASTE = "hazardous_waste"
    ENVIRONMENTAL_REPORT = "environmental_report"
    OCCUPATIONAL_SAFETY = "occupational_safety"
    FIRE_SAFETY = "fire_safety"
    INDUSTRIAL_SAFETY = "industrial_safety"
    SAFETY_AUDIT = "safety_audit"
    ACCIDENT_INVESTIGATION = "accident_investigation"
    EMERGENCY_PLAN = "emergency_plan"


class VehicleDocType(str, Enum):
    VEHICLE_PURCHASE = "vehicle_purchase"
    VEHICLE_LEASE = "vehicle_lease"
    FLEET_MANAGEMENT = "fleet_management"
    EQUIPMENT_PURCHASE = "equipment_purchase"
    EQUIPMENT_LEASE = "equipment_lease"
    MAINTENANCE_CONTRACT = "maintenance"
    INSURANCE_VEHICLE = "insurance_vehicle"
    WAYBILL = "waybill"


class QualityDocType(str, Enum):
    QUALITY_MANUAL = "quality_manual"
    QUALITY_POLICY = "quality_policy"
    PROCEDURE_DOCUMENT = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    AUDIT_CHECKLIST = "audit_checklist"
    CORRECTIVE_ACTION = "corrective_action"
    NONCONFORMITY_REPORT = "nonconformity"
    MANAGEMENT_REVIEW = "management_review"
    CALIBRATION_RECORD = "calibration"
    TRAINING_RECORD = "training_record"


class CrisisDocType(str, Enum):
    RESTRUCTURING_PLAN = "restructuring_plan"
    CREDITOR_AGREEMENT = "creditor_agreement"
    DEBT_RESTRUCTURING = "debt_restructuring"
    ASSET_SALE = "asset_sale"
    VOLUNTARY_LIQUIDATION = "voluntary_liquidation"
    BANKRUPTCY_APPLICATION = "bankruptcy"
    SETTLEMENT_AGREEMENT_CRISIS = "settlement_crisis"
    BUSINESS_CONTINUITY = "business_continuity"


# =============================================================================
# REAL ESTATE TEMPLATES
# =============================================================================

PURCHASE_SALE_REAL_ESTATE_TEMPLATE = """
               ДОГОВОР КУПЛИ-ПРОДАЖИ НЕДВИЖИМОГО ИМУЩЕСТВА № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

{seller_name}, именуемое в дальнейшем «Продавец», в лице {seller_representative},
действующего на основании {seller_basis}, с одной стороны, и

{buyer_name}, именуемое в дальнейшем «Покупатель», в лице {buyer_representative},
действующего на основании {buyer_basis}, с другой стороны,

заключили настоящий Договор:

                    1. ПРЕДМЕТ ДОГОВОРА

1.1. Продавец продаёт, а Покупатель приобретает в собственность недвижимое
имущество:
{property_description}

1.2. Адрес: {property_address}
1.3. Кадастровый номер: {cadastral_number}
1.4. Площадь: {area} кв. м.
1.5. Назначение: {purpose}

1.6. Имущество принадлежит Продавцу на праве собственности на основании:
{ownership_basis}

1.7. Имущество не обременено правами третьих лиц, не находится в залоге,
под арестом, в споре.

                    2. ЦЕНА И ПОРЯДОК РАСЧЁТОВ

2.1. Цена имущества: {price} ({price_words}) рублей.

2.2. Порядок оплаты:
{payment_terms}

2.3. Расчёты производятся: {payment_method}

                    3. ПЕРЕДАЧА ИМУЩЕСТВА

3.1. Имущество передаётся по Акту приёма-передачи в течение {handover_period}
с момента {handover_trigger}.

3.2. Право собственности переходит к Покупателю с момента государственной
регистрации перехода права.

                    4. ГАРАНТИИ ПРОДАВЦА

4.1. Продавец гарантирует:
- имущество не является предметом притязаний третьих лиц;
- отсутствуют обременения и ограничения;
- имущество не находится под арестом;
- отсутствует задолженность по коммунальным платежам.

                    5. ГОСУДАРСТВЕННАЯ РЕГИСТРАЦИЯ

5.1. Стороны обязуются обратиться в Росреестр для регистрации перехода права.

5.2. Расходы по регистрации несёт: {registration_costs}

                    6. ОТВЕТСТВЕННОСТЬ

6.1. За уклонение от регистрации — штраф {evasion_penalty}%

6.2. За нарушение сроков оплаты — пеня {late_payment_penalty}% в день.

                    7. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

ПРОДАВЕЦ:                                ПОКУПАТЕЛЬ:
{seller_name}                             {buyer_name}
ИНН: {seller_inn}                         ИНН: {buyer_inn}
Адрес: {seller_address}                   Адрес: {buyer_address}
Р/с: {seller_account}                     Р/с: {buyer_account}

_____________________ / {seller_signatory} /   _____________________ / {buyer_signatory} /
М.П.                                      М.П.
"""


COMMERCIAL_LEASE_TEMPLATE = """
               ДОГОВОР АРЕНДЫ НЕЖИЛОГО ПОМЕЩЕНИЯ № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

{landlord_name} («Арендодатель») и {tenant_name} («Арендатор»)

заключили настоящий Договор:

                    1. ПРЕДМЕТ ДОГОВОРА

1.1. Помещение: {premises_description}
1.2. Адрес: {premises_address}
1.3. Площадь: {area} кв. м.
1.4. Кадастровый номер: {cadastral_number}
1.5. Целевое использование: {intended_use}

                    2. СРОК АРЕНДЫ

2.1. Срок: с {start_date} по {end_date}
2.2. Государственная регистрация: {registration_required}

                    3. АРЕНДНАЯ ПЛАТА

3.1. Базовая ставка: {base_rent} руб./кв.м. в месяц
3.2. Арендная плата: {monthly_rent} руб./месяц, {vat_clause}
3.3. Эксплуатационные расходы: {opex}
3.4. Коммунальные услуги: {utilities}
3.5. Индексация: {indexation}

                    4. ПОРЯДОК ОПЛАТЫ

4.1. Оплата до {payment_day} числа текущего месяца.
4.2. Обеспечительный платёж: {security_deposit}
4.3. Реквизиты: {payment_details}

                    5. ОБЯЗАННОСТИ СТОРОН

5.1. Арендодатель:
- передать помещение по акту;
- обеспечить доступ;
- производить капитальный ремонт.

5.2. Арендатор:
- использовать по назначению;
- своевременно оплачивать;
- производить текущий ремонт;
- соблюдать правила эксплуатации.

                    6. УЛУЧШЕНИЯ

6.1. Неотделимые улучшения: {improvements_policy}

                    7. РАСТОРЖЕНИЕ

7.1. По соглашению сторон.
7.2. В одностороннем порядке с уведомлением за {notice_period}.

АРЕНДОДАТЕЛЬ:                            АРЕНДАТОР:
{landlord_name}                           {tenant_name}
_____________________ / {landlord_signatory} /   _____________________ / {tenant_signatory} /
"""


# =============================================================================
# BANKING/FINANCE TEMPLATES
# =============================================================================

BANK_GUARANTEE_TEMPLATE = """
                         БАНКОВСКАЯ ГАРАНТИЯ № {guarantee_number}

{bank_name}
Лицензия ЦБ РФ № {license_number}
Адрес: {bank_address}

(далее — «Гарант»)

Дата выдачи: «{day}» {month} {year} г.

                    1. СТОРОНЫ

Принципал: {principal_name}
ИНН: {principal_inn}
Адрес: {principal_address}

Бенефициар: {beneficiary_name}
ИНН: {beneficiary_inn}
Адрес: {beneficiary_address}

                    2. ОБЕСПЕЧИВАЕМОЕ ОБЯЗАТЕЛЬСТВО

Гарантия выдана в обеспечение исполнения обязательств Принципала по:
{underlying_obligation}

Договор/Контракт: № {contract_number} от {contract_date}

                    3. СУММА ГАРАНТИИ

Максимальная сумма гарантии: {guarantee_amount} ({guarantee_amount_words}) рублей.

                    4. СРОК ДЕЙСТВИЯ

Гарантия вступает в силу: {effective_date}
Гарантия действует до: {expiry_date}

                    5. УСЛОВИЯ ПЛАТЕЖА

5.1. Гарант обязуется выплатить Бенефициару денежную сумму по его
письменному требованию.

5.2. Требование должно содержать:
- указание на нарушение Принципалом обязательств;
- расчёт суммы требования;
- документы, подтверждающие нарушение.

5.3. Срок рассмотрения требования: {review_period} рабочих дней.

5.4. Срок выплаты: {payment_period} рабочих дней после принятия решения.

                    6. ОСНОВАНИЯ ДЛЯ ОТКАЗА

6.1. Требование предъявлено после истечения срока гарантии.
6.2. Сумма требования превышает сумму гарантии.
6.3. Требование не соответствует условиям гарантии.
6.4. Документы не подтверждают нарушение.

                    7. ОСОБЫЕ УСЛОВИЯ

{special_conditions}

                    8. ПРИМЕНИМОЕ ПРАВО

8.1. Гарантия регулируется законодательством Российской Федерации.

8.2. Споры разрешаются в {court_jurisdiction}.

Гарант: {bank_name}

Уполномоченное лицо: _____________________ / {authorized_signatory} /
                     {signatory_position}

М.П.

Регистрационный номер в реестре банковских гарантий: {registry_number}
"""


LEASING_AGREEMENT_TEMPLATE = """
               ДОГОВОР ФИНАНСОВОЙ АРЕНДЫ (ЛИЗИНГА) № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

{lessor_name} («Лизингодатель»), в лице {lessor_representative},
действующего на основании {lessor_basis}, с одной стороны, и

{lessee_name} («Лизингополучатель»), в лице {lessee_representative},
действующего на основании {lessee_basis}, с другой стороны,

заключили настоящий Договор:

                    1. ПРЕДМЕТ ДОГОВОРА

1.1. Лизингодатель приобретает в собственность и передаёт Лизингополучателю
во временное владение и пользование:
{equipment_description}

1.2. Продавец: {seller_name}

1.3. Лизингополучатель несёт риски, связанные с выбором Продавца и имущества.

                    2. СРОК ЛИЗИНГА

2.1. Срок лизинга: {lease_term} месяцев

2.2. Дата начала: {start_date}

2.3. Дата окончания: {end_date}

                    3. ЛИЗИНГОВЫЕ ПЛАТЕЖИ

3.1. Общая сумма лизинговых платежей: {total_payments} рублей, в том числе:
- возмещение стоимости имущества: {capital_cost}
- лизинговое вознаграждение: {lease_fee}
- НДС: {vat_amount}

3.2. График платежей: Приложение № 1.

3.3. Авансовый платёж: {advance_payment}

                    4. ПРАВО СОБСТВЕННОСТИ

4.1. Имущество является собственностью Лизингодателя.

4.2. По окончании договора: {end_of_term_option}
[ ] выкуп по остаточной стоимости {residual_value}
[ ] возврат имущества
[ ] продление договора

                    5. СТРАХОВАНИЕ

5.1. Имущество страхуется от: {insurance_coverage}

5.2. Страхователь: {insurer}

5.3. Выгодоприобретатель: {beneficiary}

                    6. ОБЯЗАННОСТИ ЛИЗИНГОПОЛУЧАТЕЛЯ

6.1. Использовать имущество по назначению.
6.2. Своевременно вносить лизинговые платежи.
6.3. Поддерживать имущество в исправном состоянии.
6.4. Производить техническое обслуживание.
6.5. Не передавать имущество третьим лицам.

                    7. ДОСРОЧНОЕ РАСТОРЖЕНИЕ

7.1. Лизингодатель вправе расторгнуть договор при:
- просрочке платежей более {payment_delay_limit};
- нецелевом использовании;
- ухудшении имущества.

7.2. При досрочном расторжении: {early_termination_consequences}

ЛИЗИНГОДАТЕЛЬ:                           ЛИЗИНГОПОЛУЧАТЕЛЬ:
{lessor_name}                             {lessee_name}
_____________________ / {lessor_signatory} /   _____________________ / {lessee_signatory} /
"""


# =============================================================================
# GOVERNMENT TENDERS (44-FZ/223-FZ) TEMPLATES
# =============================================================================

CONTRACT_44FZ_TEMPLATE = """
               ГОСУДАРСТВЕННЫЙ КОНТРАКТ № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

Идентификационный код закупки (ИКЗ): {ikz}

{customer_name} («Заказчик»), в лице {customer_representative},
действующего на основании {customer_basis}, с одной стороны, и

{supplier_name} («Поставщик/Подрядчик/Исполнитель»), в лице
{supplier_representative}, действующего на основании {supplier_basis},
с другой стороны,

по результатам закупки: {procurement_method}
(реестровый номер извещения: {notice_number})

заключили настоящий Контракт:

                    1. ПРЕДМЕТ КОНТРАКТА

1.1. Поставщик обязуется:
{contract_subject}

1.2. Код ОКПД2: {okpd_code}

1.3. Место поставки/выполнения/оказания: {delivery_location}

                    2. ЦЕНА КОНТРАКТА

2.1. Цена контракта: {contract_price} ({contract_price_words}) рублей,
{vat_clause}.

2.2. Цена является твёрдой и не подлежит изменению, за исключением случаев,
предусмотренных законодательством.

2.3. Источник финансирования: {funding_source}

2.4. Код бюджетной классификации (КБК): {kbk}

                    3. СРОКИ ИСПОЛНЕНИЯ

3.1. Срок поставки/выполнения/оказания: {delivery_term}

3.2. Этапы исполнения: {stages}

3.3. Контракт вступает в силу с момента подписания и действует
до полного исполнения обязательств.

                    4. ПОРЯДОК ОПЛАТЫ

4.1. Оплата производится за фактически поставленные товары/выполненные
работы/оказанные услуги.

4.2. Авансирование: {advance_terms}

4.3. Срок оплаты: {payment_term} рабочих дней с даты подписания
документов о приёмке.

4.4. Оплата производится путём перечисления на счёт Поставщика.

                    5. ОБЕСПЕЧЕНИЕ ИСПОЛНЕНИЯ

5.1. Размер обеспечения: {security_amount} рублей ({security_percent}%).

5.2. Форма обеспечения: {security_form}

5.3. Срок действия обеспечения: {security_term}

5.4. Обеспечение гарантийных обязательств: {warranty_security}

                    6. ПРИЁМКА

6.1. Приёмка осуществляется в порядке, установленном Приложением № {acceptance_appendix}.

6.2. Документы о приёмке формируются в ЕИС.

6.3. Срок приёмки: {acceptance_term} рабочих дней.

6.4. Экспертиза: {expertise_terms}

                    7. ОТВЕТСТВЕННОСТЬ

7.1. За просрочку исполнения обязательств — пеня за каждый день просрочки:
{penalty_formula}

7.2. За неисполнение/ненадлежащее исполнение — штраф:
{fine_rates}

7.3. Общая сумма неустойки не может превышать цену контракта.

                    8. ГАРАНТИЙНЫЕ ОБЯЗАТЕЛЬСТВА

8.1. Гарантийный срок: {warranty_period}

8.2. Гарантийное обслуживание: {warranty_service}

                    9. ИЗМЕНЕНИЕ И РАСТОРЖЕНИЕ

9.1. Изменение существенных условий контракта допускается в случаях,
предусмотренных ст. 95 Федерального закона № 44-ФЗ.

9.2. Расторжение контракта: {termination_conditions}

                    10. АНТИКОРРУПЦИОННАЯ ОГОВОРКА

10.1. Стороны обязуются не допускать коррупционных действий.

10.2. При выявлении нарушений — контракт может быть расторгнут.

                    11. ПРИЛОЖЕНИЯ

{appendices_list}

                    12. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

ЗАКАЗЧИК:                                ПОСТАВЩИК:
{customer_name}                           {supplier_name}
ИНН: {customer_inn}                       ИНН: {supplier_inn}
КПП: {customer_kpp}                       КПП: {supplier_kpp}
Адрес: {customer_address}                 Адрес: {supplier_address}
Л/с: {customer_account}                   Р/с: {supplier_account}
Банк: {customer_bank}                     Банк: {supplier_bank}

_____________________ / {customer_signatory} /   _____________________ / {supplier_signatory} /
М.П.                                      М.П.
"""


BANK_GUARANTEE_TENDER_TEMPLATE = """
                    БАНКОВСКАЯ ГАРАНТИЯ № {guarantee_number}
              (для обеспечения заявки/исполнения контракта по 44-ФЗ)

{bank_name}
Лицензия ЦБ РФ № {license_number}

Гарант: {bank_name}
Принципал: {principal_name}, ИНН {principal_inn}
Бенефициар: {beneficiary_name}, ИНН {beneficiary_inn}

Настоящая гарантия выдана в обеспечение:
{guarantee_purpose}

ИКЗ: {ikz}
Реестровый номер извещения: {notice_number}

Сумма гарантии: {guarantee_amount} рублей
Срок действия: до {expiry_date}

Требование о платеже должно содержать указание на нарушение Принципалом
обязательств, в обеспечение которых выдана гарантия.

Гарантия внесена в реестр банковских гарантий ЕИС.
Регистрационный номер: {eis_registry_number}

Гарантия соответствует требованиям статей 45, 96 Федерального закона № 44-ФЗ.

{bank_name}
_____________________ / {authorized_signatory} /
М.П.
"""


# =============================================================================
# LICENSE/PERMIT TEMPLATES
# =============================================================================

LICENSE_APPLICATION_TEMPLATE = """
                                             В {licensing_authority}
                                             Адрес: {authority_address}

                              ЗАЯВЛЕНИЕ
                    о предоставлении лицензии

Заявитель: {applicant_name}
Организационно-правовая форма: {legal_form}
ОГРН: {ogrn}
ИНН: {inn}
Адрес места нахождения: {legal_address}
Адреса мест осуществления деятельности: {activity_addresses}
Номер телефона: {phone}
E-mail: {email}

Прошу предоставить лицензию на осуществление деятельности:
{licensed_activity}

Срок действия лицензии: {license_term}

Сведения о соблюдении лицензионных требований:
{compliance_info}

Приложения:
{attachments_list}

Руководитель: _____________________ / {director_name} /
Дата: «{day}» {month} {year} г.
М.П.
"""


SRO_APPLICATION_TEMPLATE = """
                                             В {sro_name}
                                             Адрес: {sro_address}

                              ЗАЯВЛЕНИЕ
                о приёме в члены саморегулируемой организации

Заявитель: {applicant_name}
ОГРН: {ogrn}
ИНН: {inn}
Адрес: {address}

Прошу принять в члены СРО для осуществления деятельности:
{activity_type}

Уровень ответственности: {responsibility_level}

Сведения о квалификации специалистов: {specialists_info}

Сведения о материально-технической базе: {material_base}

Размер взноса в компенсационный фонд: {compensation_fund_contribution}

Обязуюсь:
- соблюдать требования стандартов СРО;
- уплачивать членские взносы;
- предоставлять отчётность.

Приложения: {attachments_list}

Руководитель: _____________________ / {director_name} /
Дата: «{day}» {month} {year} г.
М.П.
"""


# =============================================================================
# ENVIRONMENTAL/SAFETY TEMPLATES
# =============================================================================

WASTE_MANAGEMENT_TEMPLATE = """
                    ДОГОВОР НА ОБРАЩЕНИЕ С ОТХОДАМИ № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

{operator_name} («Региональный оператор/Специализированная организация»),
Лицензия № {operator_license}, в лице {operator_representative}, и

{producer_name} («Образователь отходов»), в лице {producer_representative},

заключили настоящий Договор:

                    1. ПРЕДМЕТ ДОГОВОРА

1.1. Оператор оказывает услуги по обращению с отходами:
{services_scope}

1.2. Виды отходов: {waste_types}

1.3. Классы опасности: {hazard_classes}

1.4. Объём: {waste_volume}

                    2. ПОРЯДОК ОКАЗАНИЯ УСЛУГ

2.1. Сбор/вывоз отходов: {collection_schedule}

2.2. Место накопления: {accumulation_site}

2.3. Обработка/утилизация/размещение: {processing_method}

                    3. СТОИМОСТЬ И ОПЛАТА

3.1. Тариф: {tariff}

3.2. Общая стоимость: {total_cost}

3.3. Оплата: {payment_terms}

                    4. ОБЯЗАННОСТИ СТОРОН

4.1. Образователь отходов:
- раздельно накапливать отходы;
- предоставлять паспорта отходов;
- обеспечивать доступ для вывоза.

4.2. Оператор:
- соблюдать требования законодательства;
- предоставлять акты выполненных работ.

                    5. ЭКОЛОГИЧЕСКАЯ ОТВЕТСТВЕННОСТЬ

5.1. За ненадлежащее обращение с отходами стороны несут ответственность
в соответствии с законодательством РФ.

РЕГИОНАЛЬНЫЙ ОПЕРАТОР:                   ОБРАЗОВАТЕЛЬ ОТХОДОВ:
{operator_name}                           {producer_name}
_____________________ / {operator_signatory} /   _____________________ / {producer_signatory} /
"""


OCCUPATIONAL_SAFETY_TEMPLATE = """
                    ПОЛОЖЕНИЕ О СИСТЕМЕ УПРАВЛЕНИЯ
                    ОХРАНОЙ ТРУДА (СУОТ)

{organization_name}

                              УТВЕРЖДАЮ
                    Руководитель {organization_name}
                    _____________________ / {director_name} /
                    «{day}» {month} {year} г.

                    1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Настоящее Положение разработано в соответствии с:
- Трудовым кодексом РФ;
- Приказом Минтруда России № 776н;
- Типовым положением о СУОТ.

1.2. СУОТ является частью общей системы управления организацией.

                    2. ПОЛИТИКА В ОБЛАСТИ ОХРАНЫ ТРУДА

{safety_policy}

                    3. ЦЕЛИ В ОБЛАСТИ ОХРАНЫ ТРУДА

{safety_goals}

                    4. РАСПРЕДЕЛЕНИЕ ОБЯЗАННОСТЕЙ

4.1. Руководитель организации: {director_responsibilities}

4.2. Служба охраны труда: {safety_service_responsibilities}

4.3. Руководители подразделений: {managers_responsibilities}

4.4. Работники: {employees_responsibilities}

                    5. ПРОЦЕДУРЫ СУОТ

5.1. Оценка профессиональных рисков: {risk_assessment}

5.2. Обучение по охране труда: {training_procedure}

5.3. Обеспечение СИЗ: {ppe_provision}

5.4. Медицинские осмотры: {medical_examinations}

5.5. Расследование несчастных случаев: {accident_investigation}

                    6. ПЛАНИРОВАНИЕ И КОНТРОЛЬ

6.1. Планирование мероприятий: {planning_procedure}

6.2. Внутренний аудит: {internal_audit}

6.3. Анализ со стороны руководства: {management_review}

                    7. ДОКУМЕНТАЦИЯ

7.1. Перечень документов СУОТ: {documentation_list}

7.2. Хранение документов: {document_storage}

Специалист по охране труда: _____________________ / {safety_specialist} /
"""


# =============================================================================
# VEHICLE/EQUIPMENT TEMPLATES
# =============================================================================

FLEET_MANAGEMENT_TEMPLATE = """
               ДОГОВОР НА УПРАВЛЕНИЕ АВТОПАРКОМ № {contract_number}

г. {city}                                           «{day}» {month} {year} г.

{management_company} («Управляющая компания») и
{client_name} («Клиент»)

заключили настоящий Договор:

                    1. ПРЕДМЕТ ДОГОВОРА

1.1. Управляющая компания оказывает комплексные услуги по управлению
автопарком Клиента:
{fleet_description}

1.2. Услуги включают:
{services_list}

                    2. ТРАНСПОРТНЫЕ СРЕДСТВА

2.1. Перечень ТС: Приложение № 1

2.2. Количество единиц: {vehicle_count}

2.3. Общая балансовая стоимость: {total_value}

                    3. СТОИМОСТЬ УСЛУГ

3.1. Фиксированная плата: {fixed_fee} руб./месяц

3.2. Переменная плата: {variable_fee}

3.3. Порядок оплаты: {payment_terms}

                    4. ОБЯЗАННОСТИ УПРАВЛЯЮЩЕЙ КОМПАНИИ

4.1. Организация технического обслуживания и ремонта.
4.2. Страхование ТС.
4.3. Оформление документов (ОСАГО, техосмотр).
4.4. Контроль расхода ГСМ.
4.5. Мониторинг и отчётность.

                    5. KPI И ОТЧЁТНОСТЬ

5.1. Показатели эффективности: {kpi_metrics}

5.2. Периодичность отчётов: {reporting_frequency}

УПРАВЛЯЮЩАЯ КОМПАНИЯ:                    КЛИЕНТ:
{management_company}                      {client_name}
_____________________ / {mc_signatory} /   _____________________ / {client_signatory} /
"""


WAYBILL_TEMPLATE = """
                                                    Типовая межотраслевая форма
                                                    № 4-П (4-С)

                              ПУТЕВОЙ ЛИСТ
                    {vehicle_type} № {waybill_number}

«{day}» {month} {year} г.

Организация: {organization_name}
Адрес: {organization_address}
Телефон: {organization_phone}

                    ТРАНСПОРТНОЕ СРЕДСТВО

Марка: {vehicle_make}
Государственный номер: {license_plate}
Тип: {vehicle_type}
Гаражный номер: {garage_number}

                    ВОДИТЕЛЬ

ФИО: {driver_name}
Табельный номер: {driver_id}
Удостоверение: {license_number}, категория {license_category}

                    ЗАДАНИЕ

Маршрут: {route}
Цель поездки: {trip_purpose}
Заказчик: {customer}

                    ПОКАЗАНИЯ ПРИБОРОВ

Одометр при выезде: {odometer_start} км
Одометр при возвращении: {odometer_end} км
Пробег: {mileage} км

Остаток топлива при выезде: {fuel_start} л
Выдано топлива: {fuel_issued} л
Остаток топлива при возвращении: {fuel_end} л
Расход: {fuel_consumption} л

                    ВРЕМЯ

Выезд из гаража: {departure_time}
Возвращение в гараж: {return_time}

                    ОТМЕТКИ

Медицинский осмотр пройден: _____________________
Техническое состояние проверено: _____________________

Диспетчер: _____________________ / {dispatcher_name} /
Механик: _____________________ / {mechanic_name} /
Водитель: _____________________ / {driver_signature} /
"""


# =============================================================================
# QUALITY/CERTIFICATION TEMPLATES
# =============================================================================

QUALITY_MANUAL_TEMPLATE = """
                              РУКОВОДСТВО ПО КАЧЕСТВУ

{organization_name}

Версия: {version}
Дата введения: «{day}» {month} {year} г.

                              УТВЕРЖДАЮ
                    Генеральный директор
                    _____________________ / {director_name} /

                    1. ОБЛАСТЬ ПРИМЕНЕНИЯ

1.1. Настоящее Руководство описывает систему менеджмента качества (СМК)
{organization_name}.

1.2. Область применения СМК: {scope}

1.3. Исключения: {exclusions}

                    2. НОРМАТИВНЫЕ ССЫЛКИ

- ГОСТ Р ИСО 9001-2015
{additional_standards}

                    3. КОНТЕКСТ ОРГАНИЗАЦИИ

3.1. Понимание организации: {organization_context}

3.2. Заинтересованные стороны: {interested_parties}

3.3. Область применения СМК: {qms_scope}

                    4. ЛИДЕРСТВО

4.1. Политика в области качества: {quality_policy}

4.2. Цели в области качества: {quality_objectives}

4.3. Ответственность и полномочия: {responsibilities}

                    5. ПЛАНИРОВАНИЕ

5.1. Действия в отношении рисков: {risk_actions}

5.2. Цели и планирование: {planning}

                    6. ОБЕСПЕЧЕНИЕ

6.1. Ресурсы: {resources}

6.2. Компетентность: {competence}

6.3. Документированная информация: {documentation}

                    7. ДЕЯТЕЛЬНОСТЬ

7.1. Планирование и управление: {operations_planning}

7.2. Проектирование и разработка: {design_development}

7.3. Управление поставщиками: {supplier_management}

7.4. Производство: {production}

                    8. ОЦЕНКА РЕЗУЛЬТАТОВ

8.1. Мониторинг и измерение: {monitoring}

8.2. Внутренний аудит: {internal_audit}

8.3. Анализ со стороны руководства: {management_review}

                    9. УЛУЧШЕНИЕ

9.1. Несоответствия и корректирующие действия: {corrective_actions}

9.2. Постоянное улучшение: {continuous_improvement}

Представитель руководства по качеству: _____________________ / {qmr_name} /
"""


NONCONFORMITY_REPORT_TEMPLATE = """
                    ОТЧЁТ О НЕСООТВЕТСТВИИ № {report_number}

{organization_name}
Дата обнаружения: «{day}» {month} {year} г.

                    1. ИДЕНТИФИКАЦИЯ НЕСООТВЕТСТВИЯ

Источник обнаружения: {detection_source}
[ ] Внутренний аудит  [ ] Входной контроль  [ ] Производственный контроль
[ ] Рекламация  [ ] Внешний аудит  [ ] Прочее

Процесс/Продукция: {process_product}
Требование: {requirement}
Описание несоответствия: {nonconformity_description}

                    2. НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ (КОРРЕКЦИЯ)

Принятые действия: {immediate_actions}
Ответственный: {immediate_responsible}
Дата выполнения: {immediate_date}

                    3. АНАЛИЗ ПРИЧИН

Метод анализа: [ ] 5 Почему  [ ] Диаграмма Исикавы  [ ] Прочее

Коренная причина: {root_cause}

                    4. КОРРЕКТИРУЮЩИЕ ДЕЙСТВИЯ

| № | Действие | Ответственный | Срок | Статус |
|---|----------|---------------|------|--------|
{corrective_actions_table}

                    5. ОЦЕНКА РЕЗУЛЬТАТИВНОСТИ

Критерии оценки: {effectiveness_criteria}
Дата оценки: {evaluation_date}
Результат: [ ] Результативно  [ ] Нерезультативно

Комментарии: {evaluation_comments}

                    6. ПОДПИСИ

Составил: _____________________ / {author_name} /
Утвердил: _____________________ / {approver_name} /
"""


# =============================================================================
# CRISIS/RESTRUCTURING TEMPLATES
# =============================================================================

RESTRUCTURING_PLAN_TEMPLATE = """
                    ПЛАН ФИНАНСОВОГО ОЗДОРОВЛЕНИЯ
                         {organization_name}

Дата разработки: «{day}» {month} {year} г.
Период реализации: {plan_period}

                    1. РЕЗЮМЕ

1.1. Текущее финансовое состояние: {current_state}

1.2. Причины кризиса: {crisis_causes}

1.3. Цели реструктуризации: {restructuring_goals}

                    2. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

2.1. Финансовые показатели:
{financial_indicators}

2.2. Структура задолженности:
| Кредитор | Сумма | Срок | Обеспечение |
|----------|-------|------|-------------|
{debt_structure}

2.3. Активы и обязательства: {assets_liabilities}

                    3. ПЛАН МЕРОПРИЯТИЙ

3.1. Операционные мероприятия:
{operational_measures}

3.2. Финансовые мероприятия:
{financial_measures}

3.3. Реструктуризация долга:
{debt_restructuring_measures}

3.4. Продажа активов:
{asset_sale_measures}

                    4. ФИНАНСОВЫЙ ПРОГНОЗ

4.1. Прогноз денежных потоков: {cash_flow_forecast}

4.2. Прогноз прибыли: {profit_forecast}

4.3. Источники финансирования: {funding_sources}

                    5. ГРАФИК РЕАЛИЗАЦИИ

{implementation_schedule}

                    6. КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ ЭФФЕКТИВНОСТИ

{kpi_targets}

                    7. РИСКИ И МЕРЫ ПО ИХ МИНИМИЗАЦИИ

{risks_mitigation}

Руководитель проекта: _____________________ / {project_manager} /
Финансовый директор: _____________________ / {cfo_name} /
Генеральный директор: _____________________ / {ceo_name} /
"""


CREDITOR_AGREEMENT_TEMPLATE = """
               СОГЛАШЕНИЕ О РЕСТРУКТУРИЗАЦИИ ЗАДОЛЖЕННОСТИ № {agreement_number}

г. {city}                                           «{day}» {month} {year} г.

{debtor_name} («Должник»), в лице {debtor_representative}, с одной стороны, и

Кредиторы:
{creditors_list}

совместно заключили настоящее Соглашение:

                    1. ПРЕДМЕТ СОГЛАШЕНИЯ

1.1. Общая сумма задолженности Должника перед Кредиторами составляет:
{total_debt} рублей.

1.2. Стороны договорились о реструктуризации задолженности на следующих условиях:
{restructuring_terms}

                    2. УСЛОВИЯ РЕСТРУКТУРИЗАЦИИ

2.1. Отсрочка/рассрочка: {deferral_terms}

2.2. Снижение процентной ставки: {interest_reduction}

2.3. Списание части долга: {debt_write_off}

2.4. Конвертация в капитал: {debt_to_equity}

                    3. ГРАФИК ПОГАШЕНИЯ

{repayment_schedule}

                    4. ОБЕСПЕЧЕНИЕ

4.1. В качестве обеспечения Должник предоставляет:
{security_provided}

                    5. ОБЯЗАТЕЛЬСТВА ДОЛЖНИКА

5.1. Соблюдать финансовые ковенанты: {financial_covenants}

5.2. Предоставлять отчётность: {reporting_requirements}

5.3. Не допускать: {negative_covenants}

                    6. МОРАТОРИЙ

6.1. Кредиторы обязуются не предъявлять требования о досрочном погашении
в период: {moratorium_period}

                    7. СОБЫТИЯ ДЕФОЛТА

7.1. При наступлении события дефолта: {default_consequences}

Подписи сторон:

ДОЛЖНИК: {debtor_name}
_____________________ / {debtor_signatory} /

КРЕДИТОРЫ:
{creditors_signatures}
"""


# =============================================================================
# Specialized Template Service
# =============================================================================

class SpecializedTemplateService:
    """Service for generating specialized documents across multiple categories."""

    # Template mapping for each category
    REAL_ESTATE_TEMPLATES = {
        RealEstateDocType.PURCHASE_SALE_REAL_ESTATE: PURCHASE_SALE_REAL_ESTATE_TEMPLATE,
        RealEstateDocType.COMMERCIAL_LEASE: COMMERCIAL_LEASE_TEMPLATE,
    }

    BANKING_TEMPLATES = {
        BankingDocType.BANK_GUARANTEE: BANK_GUARANTEE_TEMPLATE,
        BankingDocType.LEASING_AGREEMENT: LEASING_AGREEMENT_TEMPLATE,
    }

    GOV_TENDER_TEMPLATES = {
        GovTenderDocType.CONTRACT_44FZ: CONTRACT_44FZ_TEMPLATE,
        GovTenderDocType.BANK_GUARANTEE_TENDER: BANK_GUARANTEE_TENDER_TEMPLATE,
    }

    LICENSE_TEMPLATES = {
        LicenseDocType.LICENSE_APPLICATION: LICENSE_APPLICATION_TEMPLATE,
        LicenseDocType.SRO_APPLICATION: SRO_APPLICATION_TEMPLATE,
    }

    ENVIRONMENTAL_TEMPLATES = {
        EnvironmentalDocType.WASTE_MANAGEMENT: WASTE_MANAGEMENT_TEMPLATE,
        EnvironmentalDocType.OCCUPATIONAL_SAFETY: OCCUPATIONAL_SAFETY_TEMPLATE,
    }

    VEHICLE_TEMPLATES = {
        VehicleDocType.FLEET_MANAGEMENT: FLEET_MANAGEMENT_TEMPLATE,
        VehicleDocType.WAYBILL: WAYBILL_TEMPLATE,
    }

    QUALITY_TEMPLATES = {
        QualityDocType.QUALITY_MANUAL: QUALITY_MANUAL_TEMPLATE,
        QualityDocType.NONCONFORMITY_REPORT: NONCONFORMITY_REPORT_TEMPLATE,
    }

    CRISIS_TEMPLATES = {
        CrisisDocType.RESTRUCTURING_PLAN: RESTRUCTURING_PLAN_TEMPLATE,
        CrisisDocType.CREDITOR_AGREEMENT: CREDITOR_AGREEMENT_TEMPLATE,
    }

    TEMPLATE_NAMES = {
        # Real Estate
        RealEstateDocType.PURCHASE_SALE_REAL_ESTATE: "Договор купли-продажи недвижимости",
        RealEstateDocType.COMMERCIAL_LEASE: "Договор аренды нежилого помещения",
        # Banking
        BankingDocType.BANK_GUARANTEE: "Банковская гарантия",
        BankingDocType.LEASING_AGREEMENT: "Договор лизинга",
        # Government Tenders
        GovTenderDocType.CONTRACT_44FZ: "Государственный контракт (44-ФЗ)",
        GovTenderDocType.BANK_GUARANTEE_TENDER: "Банковская гарантия для тендера",
        # Licenses
        LicenseDocType.LICENSE_APPLICATION: "Заявление на лицензию",
        LicenseDocType.SRO_APPLICATION: "Заявление в СРО",
        # Environmental
        EnvironmentalDocType.WASTE_MANAGEMENT: "Договор на обращение с отходами",
        EnvironmentalDocType.OCCUPATIONAL_SAFETY: "Положение о СУОТ",
        # Vehicles
        VehicleDocType.FLEET_MANAGEMENT: "Договор управления автопарком",
        VehicleDocType.WAYBILL: "Путевой лист",
        # Quality
        QualityDocType.QUALITY_MANUAL: "Руководство по качеству",
        QualityDocType.NONCONFORMITY_REPORT: "Отчёт о несоответствии",
        # Crisis
        CrisisDocType.RESTRUCTURING_PLAN: "План финансового оздоровления",
        CrisisDocType.CREDITOR_AGREEMENT: "Соглашение с кредиторами",
    }

    @classmethod
    def get_all_templates(cls) -> Dict[str, Dict]:
        """Get all templates organized by category."""
        return {
            "real_estate": cls.REAL_ESTATE_TEMPLATES,
            "banking": cls.BANKING_TEMPLATES,
            "gov_tenders": cls.GOV_TENDER_TEMPLATES,
            "licenses": cls.LICENSE_TEMPLATES,
            "environmental": cls.ENVIRONMENTAL_TEMPLATES,
            "vehicles": cls.VEHICLE_TEMPLATES,
            "quality": cls.QUALITY_TEMPLATES,
            "crisis": cls.CRISIS_TEMPLATES,
        }

    @classmethod
    def list_all_templates(cls) -> List[Dict[str, str]]:
        """List all available templates."""
        return [
            {"type": str(dt.value), "name": name}
            for dt, name in cls.TEMPLATE_NAMES.items()
        ]

    @classmethod
    def generate_document(cls, doc_type: str, data: Dict[str, Any]) -> str:
        """Generate document from any category."""
        all_templates = {
            **cls.REAL_ESTATE_TEMPLATES,
            **cls.BANKING_TEMPLATES,
            **cls.GOV_TENDER_TEMPLATES,
            **cls.LICENSE_TEMPLATES,
            **cls.ENVIRONMENTAL_TEMPLATES,
            **cls.VEHICLE_TEMPLATES,
            **cls.QUALITY_TEMPLATES,
            **cls.CRISIS_TEMPLATES,
        }

        # Find template by enum value
        template = None
        for enum_type, tpl in all_templates.items():
            if enum_type.value == doc_type:
                template = tpl
                break

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
