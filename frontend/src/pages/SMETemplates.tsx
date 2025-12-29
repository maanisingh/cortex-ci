import React, { useState, useMemo } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  DocumentDuplicateIcon,
  BanknotesIcon,
  CalculatorIcon,
  ScaleIcon,
  BuildingStorefrontIcon,
  HomeModernIcon,
  BuildingLibraryIcon,
  ClipboardDocumentListIcon,
  IdentificationIcon,
  ShieldExclamationIcon,
  TruckIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  ArchiveBoxIcon,
} from '@heroicons/react/24/outline';

// Template categories
type TemplateCategory =
  | 'corporate'
  | 'hr'
  | 'contracts'
  | 'financial'
  | 'tax'
  | 'legal'
  | 'industry'
  | 'real_estate'
  | 'banking'
  | 'gov_tenders'
  | 'licenses'
  | 'environmental'
  | 'vehicles'
  | 'quality'
  | 'crisis'
  | 'grc_compliance';

interface CategoryInfo {
  id: TemplateCategory;
  name: string;
  nameEn: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  templateCount: number;
}

interface Template {
  id: string;
  name: string;
  nameEn?: string;
  category: TemplateCategory;
  description: string;
  tags: string[];
  regulatoryRefs?: string[];
}

const CATEGORIES: CategoryInfo[] = [
  { id: 'corporate', name: 'Корпоративные', nameEn: 'Corporate', icon: BuildingOfficeIcon, color: 'text-blue-600', bgColor: 'bg-blue-50', templateCount: 15 },
  { id: 'hr', name: 'Кадровые', nameEn: 'HR', icon: UserGroupIcon, color: 'text-green-600', bgColor: 'bg-green-50', templateCount: 20 },
  { id: 'contracts', name: 'Договоры', nameEn: 'Contracts', icon: DocumentDuplicateIcon, color: 'text-purple-600', bgColor: 'bg-purple-50', templateCount: 25 },
  { id: 'financial', name: 'Финансовые', nameEn: 'Financial', icon: BanknotesIcon, color: 'text-emerald-600', bgColor: 'bg-emerald-50', templateCount: 18 },
  { id: 'tax', name: 'Налоговые', nameEn: 'Tax', icon: CalculatorIcon, color: 'text-orange-600', bgColor: 'bg-orange-50', templateCount: 15 },
  { id: 'legal', name: 'Юридические', nameEn: 'Legal', icon: ScaleIcon, color: 'text-red-600', bgColor: 'bg-red-50', templateCount: 12 },
  { id: 'industry', name: 'Отраслевые', nameEn: 'Industry', icon: BuildingStorefrontIcon, color: 'text-cyan-600', bgColor: 'bg-cyan-50', templateCount: 40 },
  { id: 'real_estate', name: 'Недвижимость', nameEn: 'Real Estate', icon: HomeModernIcon, color: 'text-amber-600', bgColor: 'bg-amber-50', templateCount: 12 },
  { id: 'banking', name: 'Банковские', nameEn: 'Banking', icon: BuildingLibraryIcon, color: 'text-indigo-600', bgColor: 'bg-indigo-50', templateCount: 15 },
  { id: 'gov_tenders', name: 'Госзакупки', nameEn: 'Gov Tenders', icon: ClipboardDocumentListIcon, color: 'text-teal-600', bgColor: 'bg-teal-50', templateCount: 15 },
  { id: 'licenses', name: 'Лицензии', nameEn: 'Licenses', icon: IdentificationIcon, color: 'text-pink-600', bgColor: 'bg-pink-50', templateCount: 10 },
  { id: 'environmental', name: 'Экология и ОТ', nameEn: 'Environmental', icon: ShieldExclamationIcon, color: 'text-lime-600', bgColor: 'bg-lime-50', templateCount: 12 },
  { id: 'vehicles', name: 'Транспорт', nameEn: 'Vehicles', icon: TruckIcon, color: 'text-slate-600', bgColor: 'bg-slate-50', templateCount: 8 },
  { id: 'quality', name: 'Качество', nameEn: 'Quality', icon: CheckBadgeIcon, color: 'text-violet-600', bgColor: 'bg-violet-50', templateCount: 10 },
  { id: 'crisis', name: 'Антикризисные', nameEn: 'Crisis', icon: ExclamationTriangleIcon, color: 'text-rose-600', bgColor: 'bg-rose-50', templateCount: 8 },
  { id: 'grc_compliance', name: 'GRC Комплаенс', nameEn: 'GRC Compliance', icon: DocumentTextIcon, color: 'text-gray-600', bgColor: 'bg-gray-50', templateCount: 30 },
];

// Sample templates data (in production, this would come from the API)
const ALL_TEMPLATES: Template[] = [
  // Corporate
  { id: 'charter_ooo', name: 'Устав ООО', category: 'corporate', description: 'Учредительный документ общества с ограниченной ответственностью', tags: ['регистрация', 'ФНС'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'charter_ao', name: 'Устав АО', category: 'corporate', description: 'Учредительный документ акционерного общества', tags: ['регистрация', 'ФНС'], regulatoryRefs: ['208-ФЗ'] },
  { id: 'founders_agreement', name: 'Договор об учреждении', category: 'corporate', description: 'Соглашение между учредителями при создании ООО', tags: ['учреждение'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'formation_decision_sole', name: 'Решение единственного учредителя', category: 'corporate', description: 'Решение о создании ООО одним учредителем', tags: ['регистрация'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'formation_decision_multiple', name: 'Протокол собрания учредителей', category: 'corporate', description: 'Протокол о создании ООО несколькими учредителями', tags: ['регистрация'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'dividend_resolution', name: 'Решение о распределении прибыли', category: 'corporate', description: 'Решение о выплате дивидендов участникам', tags: ['дивиденды', 'прибыль'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'capital_increase', name: 'Решение об увеличении УК', category: 'corporate', description: 'Увеличение уставного капитала общества', tags: ['уставный капитал'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'share_sale', name: 'Договор купли-продажи доли', category: 'corporate', description: 'Отчуждение доли в уставном капитале', tags: ['доля', 'продажа'], regulatoryRefs: ['14-ФЗ'] },
  { id: 'shareholder_meeting', name: 'Протокол общего собрания', category: 'corporate', description: 'Протокол ОСУ/ОСА', tags: ['собрание', 'решения'], regulatoryRefs: ['14-ФЗ', '208-ФЗ'] },
  { id: 'branch_regulation', name: 'Положение о филиале', category: 'corporate', description: 'Регламент деятельности филиала', tags: ['филиал', 'структура'] },

  // HR
  { id: 'employment_contract', name: 'Трудовой договор', category: 'hr', description: 'Договор между работником и работодателем', tags: ['трудовой', 'найм'], regulatoryRefs: ['ТК РФ'] },
  { id: 'employment_contract_remote', name: 'Трудовой договор (дистанционная работа)', category: 'hr', description: 'Договор для удаленных сотрудников', tags: ['трудовой', 'дистанционный'], regulatoryRefs: ['ТК РФ'] },
  { id: 'contractor_agreement', name: 'Договор ГПХ', category: 'hr', description: 'Гражданско-правовой договор на оказание услуг', tags: ['подряд', 'услуги'], regulatoryRefs: ['ГК РФ'] },
  { id: 'director_appointment', name: 'Приказ о назначении директора', category: 'hr', description: 'Вступление в должность руководителя', tags: ['директор', 'назначение'], regulatoryRefs: ['ТК РФ'] },
  { id: 'internal_labor_rules', name: 'ПВТР', category: 'hr', description: 'Правила внутреннего трудового распорядка', tags: ['ЛНА', 'обязательный'], regulatoryRefs: ['ТК РФ'] },
  { id: 'vacation_schedule', name: 'График отпусков', category: 'hr', description: 'Ежегодный план отпусков сотрудников', tags: ['отпуск', 'график'], regulatoryRefs: ['ТК РФ'] },
  { id: 'dismissal_order', name: 'Приказ об увольнении', category: 'hr', description: 'Прекращение трудового договора', tags: ['увольнение'], regulatoryRefs: ['ТК РФ'] },
  { id: 'job_description', name: 'Должностная инструкция', category: 'hr', description: 'Описание обязанностей должности', tags: ['ЛНА', 'функции'] },
  { id: 'nda_employee', name: 'Соглашение о неразглашении (сотрудник)', category: 'hr', description: 'Обязательство о конфиденциальности', tags: ['NDA', 'конфиденциальность'] },
  { id: 'layoff_order', name: 'Приказ о сокращении', category: 'hr', description: 'Сокращение численности/штата', tags: ['сокращение'], regulatoryRefs: ['ТК РФ'] },

  // Contracts
  { id: 'supply', name: 'Договор поставки', category: 'contracts', description: 'Поставка товаров для предпринимательских целей', tags: ['поставка', 'товары'], regulatoryRefs: ['ГК РФ'] },
  { id: 'service', name: 'Договор оказания услуг', category: 'contracts', description: 'Возмездное оказание услуг', tags: ['услуги'], regulatoryRefs: ['ГК РФ'] },
  { id: 'agency', name: 'Агентский договор', category: 'contracts', description: 'Совершение действий от имени принципала', tags: ['агент', 'посредничество'], regulatoryRefs: ['ГК РФ'] },
  { id: 'commission', name: 'Договор комиссии', category: 'contracts', description: 'Совершение сделок от своего имени за счет комитента', tags: ['комиссия', 'посредничество'], regulatoryRefs: ['ГК РФ'] },
  { id: 'lease', name: 'Договор аренды', category: 'contracts', description: 'Аренда имущества', tags: ['аренда'], regulatoryRefs: ['ГК РФ'] },
  { id: 'sublease', name: 'Договор субаренды', category: 'contracts', description: 'Субаренда арендованного имущества', tags: ['субаренда'], regulatoryRefs: ['ГК РФ'] },
  { id: 'loan', name: 'Договор займа', category: 'contracts', description: 'Передача денег в долг', tags: ['заем', 'деньги'], regulatoryRefs: ['ГК РФ'] },
  { id: 'franchise', name: 'Договор франчайзинга', category: 'contracts', description: 'Коммерческая концессия', tags: ['франшиза', 'бренд'], regulatoryRefs: ['ГК РФ'] },
  { id: 'distribution', name: 'Дистрибьюторский договор', category: 'contracts', description: 'Распространение товаров', tags: ['дистрибуция', 'сбыт'] },
  { id: 'nda', name: 'NDA', category: 'contracts', description: 'Соглашение о конфиденциальности', tags: ['NDA', 'секретность'] },
  { id: 'joint_venture', name: 'Договор о совместной деятельности', category: 'contracts', description: 'Простое товарищество', tags: ['партнерство'], regulatoryRefs: ['ГК РФ'] },
  { id: 'licensing', name: 'Лицензионный договор', category: 'contracts', description: 'Использование интеллектуальной собственности', tags: ['лицензия', 'ИС'], regulatoryRefs: ['ГК РФ'] },

  // Financial
  { id: 'invoice', name: 'Счет на оплату', category: 'financial', description: 'Документ для оплаты товаров/услуг', tags: ['счет', 'оплата'] },
  { id: 'torg_12', name: 'ТОРГ-12', category: 'financial', description: 'Товарная накладная', tags: ['накладная', 'товар'] },
  { id: 'upd', name: 'УПД', category: 'financial', description: 'Универсальный передаточный документ', tags: ['первичка', 'НДС'] },
  { id: 'act_services', name: 'Акт выполненных работ', category: 'financial', description: 'Подтверждение оказания услуг', tags: ['акт', 'услуги'] },
  { id: 'cash_receipt_ko1', name: 'Приходный кассовый ордер (КО-1)', category: 'financial', description: 'Прием наличных в кассу', tags: ['касса', 'приход'] },
  { id: 'cash_expense_ko2', name: 'Расходный кассовый ордер (КО-2)', category: 'financial', description: 'Выдача наличных из кассы', tags: ['касса', 'расход'] },
  { id: 'advance_report', name: 'Авансовый отчет', category: 'financial', description: 'Отчет об использовании подотчетных средств', tags: ['авансовый', 'подотчет'] },
  { id: 'accounting_policy', name: 'Учетная политика', category: 'financial', description: 'Организация бухгалтерского учета', tags: ['учет', 'политика'] },
  { id: 'reconciliation_act', name: 'Акт сверки взаиморасчетов', category: 'financial', description: 'Сверка задолженности с контрагентом', tags: ['сверка', 'задолженность'] },

  // Tax
  { id: 'usn_application', name: 'Заявление на УСН', category: 'tax', description: 'Переход на упрощенную систему', tags: ['УСН', 'режим'], regulatoryRefs: ['НК РФ'] },
  { id: 'vat_declaration', name: 'Декларация по НДС', category: 'tax', description: 'Квартальная отчетность по НДС', tags: ['НДС', 'декларация'], regulatoryRefs: ['НК РФ'] },
  { id: 'profit_tax_declaration', name: 'Декларация по налогу на прибыль', category: 'tax', description: 'Отчетность по налогу на прибыль', tags: ['прибыль', 'декларация'], regulatoryRefs: ['НК РФ'] },
  { id: '6_ndfl', name: '6-НДФЛ', category: 'tax', description: 'Расчет по НДФЛ', tags: ['НДФЛ', 'расчет'], regulatoryRefs: ['НК РФ'] },
  { id: 'rsv_report', name: 'РСВ', category: 'tax', description: 'Расчет страховых взносов', tags: ['взносы', 'расчет'], regulatoryRefs: ['НК РФ'] },
  { id: 'tax_reconciliation', name: 'Запрос на сверку с ФНС', category: 'tax', description: 'Сверка расчетов с бюджетом', tags: ['сверка', 'ФНС'] },

  // Legal
  { id: 'trademark_application', name: 'Заявка на товарный знак', category: 'legal', description: 'Регистрация товарного знака в Роспатент', tags: ['ТЗ', 'Роспатент'] },
  { id: 'copyright_registration', name: 'Депонирование авторских прав', category: 'legal', description: 'Защита авторских прав', tags: ['авторское право'] },
  { id: 'cease_desist', name: 'Претензия о нарушении прав', category: 'legal', description: 'Требование прекратить нарушение', tags: ['претензия', 'нарушение'] },
  { id: 'lawsuit', name: 'Исковое заявление', category: 'legal', description: 'Обращение в арбитражный суд', tags: ['иск', 'суд'] },
  { id: 'settlement', name: 'Мировое соглашение', category: 'legal', description: 'Урегулирование спора', tags: ['мировая', 'спор'] },
  { id: 'legal_opinion', name: 'Юридическое заключение', category: 'legal', description: 'Правовая экспертиза', tags: ['экспертиза', 'заключение'] },

  // Industry (sample)
  { id: 'ks_2', name: 'КС-2', category: 'industry', description: 'Акт о приемке выполненных работ (строительство)', tags: ['строительство', 'акт'] },
  { id: 'ks_3', name: 'КС-3', category: 'industry', description: 'Справка о стоимости работ', tags: ['строительство', 'справка'] },
  { id: 'sla_agreement', name: 'SLA', category: 'industry', description: 'Соглашение об уровне обслуживания', tags: ['IT', 'сервис'] },
  { id: 'dpa', name: 'DPA', category: 'industry', description: 'Соглашение об обработке данных', tags: ['IT', 'данные'] },
  { id: 'haccp_plan', name: 'План ХАССП', category: 'industry', description: 'Система безопасности пищевой продукции', tags: ['пищевая', 'безопасность'] },
  { id: 'clinical_trial', name: 'Договор клинических исследований', category: 'industry', description: 'Проведение клинических испытаний', tags: ['медицина', 'исследования'] },

  // Real Estate
  { id: 'property_sale', name: 'Договор купли-продажи недвижимости', category: 'real_estate', description: 'Отчуждение объекта недвижимости', tags: ['продажа', 'Росреестр'] },
  { id: 'commercial_lease', name: 'Договор аренды коммерческой недвижимости', category: 'real_estate', description: 'Аренда офиса/склада/магазина', tags: ['аренда', 'коммерческая'] },
  { id: 'property_management', name: 'Договор управления недвижимостью', category: 'real_estate', description: 'Доверительное управление', tags: ['управление'] },

  // Banking
  { id: 'account_opening', name: 'Заявление на открытие счета', category: 'banking', description: 'Открытие расчетного счета', tags: ['счет', 'банк'] },
  { id: 'credit_agreement', name: 'Кредитный договор', category: 'banking', description: 'Получение банковского кредита', tags: ['кредит', 'банк'] },
  { id: 'bank_guarantee', name: 'Банковская гарантия', category: 'banking', description: 'Обеспечение обязательств', tags: ['гарантия', 'обеспечение'] },
  { id: 'leasing_contract', name: 'Договор лизинга', category: 'banking', description: 'Финансовая аренда оборудования', tags: ['лизинг', 'оборудование'] },
  { id: 'factoring', name: 'Договор факторинга', category: 'banking', description: 'Финансирование под уступку требований', tags: ['факторинг', 'дебиторка'] },

  // Gov Tenders
  { id: 'tender_application_44fz', name: 'Заявка на участие в тендере (44-ФЗ)', category: 'gov_tenders', description: 'Государственные закупки', tags: ['44-ФЗ', 'тендер'], regulatoryRefs: ['44-ФЗ'] },
  { id: 'tender_application_223fz', name: 'Заявка на участие в тендере (223-ФЗ)', category: 'gov_tenders', description: 'Закупки госкомпаний', tags: ['223-ФЗ', 'тендер'], regulatoryRefs: ['223-ФЗ'] },
  { id: 'state_contract', name: 'Государственный контракт', category: 'gov_tenders', description: 'Контракт по 44-ФЗ', tags: ['контракт', '44-ФЗ'], regulatoryRefs: ['44-ФЗ'] },
  { id: 'anti_dumping_explanation', name: 'Обоснование цены (антидемпинговые меры)', category: 'gov_tenders', description: 'Объяснение сниженной цены', tags: ['цена', 'демпинг'], regulatoryRefs: ['44-ФЗ'] },

  // Licenses
  { id: 'license_application', name: 'Заявление на получение лицензии', category: 'licenses', description: 'Заявка в лицензирующий орган', tags: ['лицензия', 'заявка'] },
  { id: 'alcohol_license', name: 'Заявление на лицензию (алкоголь)', category: 'licenses', description: 'Лицензия на розничную продажу алкоголя', tags: ['алкоголь', 'лицензия'] },
  { id: 'medical_license', name: 'Заявление на медицинскую лицензию', category: 'licenses', description: 'Лицензия на медицинскую деятельность', tags: ['медицина', 'лицензия'] },

  // Environmental
  { id: 'environmental_report', name: 'Экологический отчет', category: 'environmental', description: 'Отчетность по экологическим платежам', tags: ['экология', 'отчет'] },
  { id: 'waste_passport', name: 'Паспорт отходов', category: 'environmental', description: 'Документация на отходы 1-4 класса', tags: ['отходы', 'паспорт'] },
  { id: 'ot_instruction', name: 'Инструкция по охране труда', category: 'environmental', description: 'ИОТ по профессии/виду работ', tags: ['ОТ', 'инструкция'] },
  { id: 'sout_card', name: 'Карта СОУТ', category: 'environmental', description: 'Специальная оценка условий труда', tags: ['СОУТ', 'условия'] },

  // Vehicles
  { id: 'vehicle_sale', name: 'Договор купли-продажи ТС', category: 'vehicles', description: 'Продажа транспортного средства', tags: ['авто', 'продажа'] },
  { id: 'vehicle_lease', name: 'Договор аренды ТС', category: 'vehicles', description: 'Аренда автомобиля', tags: ['авто', 'аренда'] },
  { id: 'waybill', name: 'Путевой лист', category: 'vehicles', description: 'Учет работы транспорта', tags: ['путевой', 'учет'] },

  // Quality
  { id: 'quality_manual', name: 'Руководство по качеству', category: 'quality', description: 'СМК по ISO 9001', tags: ['ISO', 'СМК'] },
  { id: 'quality_policy', name: 'Политика в области качества', category: 'quality', description: 'Декларация о качестве', tags: ['политика', 'СМК'] },
  { id: 'calibration_schedule', name: 'График поверки СИ', category: 'quality', description: 'План метрологического обеспечения', tags: ['метрология', 'поверка'] },

  // Crisis
  { id: 'restructuring_plan', name: 'План реструктуризации', category: 'crisis', description: 'Стратегия финансового оздоровления', tags: ['реструктуризация', 'план'] },
  { id: 'creditor_agreement', name: 'Соглашение с кредиторами', category: 'crisis', description: 'Урегулирование задолженности', tags: ['кредиторы', 'долг'] },
  { id: 'voluntary_liquidation', name: 'Заявление о ликвидации', category: 'crisis', description: 'Добровольная ликвидация ООО', tags: ['ликвидация', 'закрытие'] },
  { id: 'bankruptcy_application', name: 'Заявление о банкротстве', category: 'crisis', description: 'Инициирование процедуры банкротства', tags: ['банкротство'], regulatoryRefs: ['127-ФЗ'] },

  // GRC Compliance
  { id: 'pdp_policy', name: 'Политика обработки ПДн', category: 'grc_compliance', description: 'Документ по 152-ФЗ', tags: ['152-ФЗ', 'ПДн'], regulatoryRefs: ['152-ФЗ'] },
  { id: 'pdp_consent', name: 'Согласие на обработку ПДн', category: 'grc_compliance', description: 'Форма согласия субъекта ПДн', tags: ['152-ФЗ', 'согласие'], regulatoryRefs: ['152-ФЗ'] },
  { id: 'kii_categorization', name: 'Акт категорирования КИИ', category: 'grc_compliance', description: 'Категорирование объектов КИИ', tags: ['187-ФЗ', 'КИИ'], regulatoryRefs: ['187-ФЗ'] },
  { id: 'security_policy', name: 'Политика информационной безопасности', category: 'grc_compliance', description: 'Базовый документ ИБ', tags: ['ИБ', 'политика'] },
  { id: 'gost_57580_report', name: 'Отчет по ГОСТ Р 57580', category: 'grc_compliance', description: 'Оценка соответствия для финорганизаций', tags: ['ГОСТ', 'финансы'], regulatoryRefs: ['ГОСТ Р 57580'] },
];

const SMETemplates: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Filter templates
  const filteredTemplates = useMemo(() => {
    let result = ALL_TEMPLATES;

    if (selectedCategory) {
      result = result.filter(t => t.category === selectedCategory);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    return result;
  }, [selectedCategory, searchQuery]);

  // Get category info
  const getCategoryInfo = (categoryId: TemplateCategory) =>
    CATEGORIES.find(c => c.id === categoryId)!;

  // Total template count
  const totalTemplates = CATEGORIES.reduce((sum, c) => sum + c.templateCount, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Шаблоны документов для бизнеса
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                {totalTemplates}+ шаблонов для всех этапов развития компании
              </p>
            </div>
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <span className="text-sm text-gray-500">
                Найдено: {filteredTemplates.length}
              </span>
            </div>
          </div>

          {/* Search */}
          <div className="mt-4 flex gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск шаблонов..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 border rounded-lg flex items-center ${
                showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Категории
            </button>
          </div>
        </div>
      </div>

      {/* Category Filters */}
      {showFilters && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === null
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Все ({totalTemplates})
              </button>
              {CATEGORIES.map((category) => {
                const Icon = category.icon;
                const isSelected = selectedCategory === category.id;
                return (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                      isSelected
                        ? `${category.bgColor} ${category.color}`
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-1" />
                    <span className="truncate">{category.name}</span>
                    <span className="ml-1 text-xs opacity-70">({category.templateCount})</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Categories */}
          <div className="lg:col-span-1 hidden lg:block">
            <div className="bg-white rounded-lg border border-gray-200 sticky top-8">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">Категории</h3>
              </div>
              <div className="p-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                    selectedCategory === null
                      ? 'bg-gray-100 font-medium'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  Все шаблоны
                  <span className="float-right text-gray-500">{totalTemplates}</span>
                </button>
                {CATEGORIES.map((category) => {
                  const Icon = category.icon;
                  const isSelected = selectedCategory === category.id;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                      className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors flex items-center ${
                        isSelected ? `${category.bgColor} ${category.color}` : 'hover:bg-gray-50'
                      }`}
                    >
                      <Icon className={`h-4 w-4 mr-2 ${isSelected ? category.color : 'text-gray-400'}`} />
                      <span className="truncate flex-1">{category.name}</span>
                      <span className={`text-xs ${isSelected ? category.color : 'text-gray-500'}`}>
                        {category.templateCount}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Template Grid */}
          <div className="lg:col-span-3">
            {filteredTemplates.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  Шаблоны не найдены
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Попробуйте изменить критерии поиска
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredTemplates.map((template) => {
                  const categoryInfo = getCategoryInfo(template.category);
                  return (
                    <div
                      key={template.id}
                      onClick={() => setSelectedTemplate(template)}
                      className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 hover:shadow-sm cursor-pointer transition-all"
                    >
                      <div className="flex items-start">
                        <div className={`p-2 rounded-lg ${categoryInfo.bgColor}`}>
                          <DocumentTextIcon className={`h-5 w-5 ${categoryInfo.color}`} />
                        </div>
                        <div className="ml-3 flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">
                            {template.name}
                          </h4>
                          <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                            {template.description}
                          </p>
                          <div className="mt-2 flex flex-wrap gap-1">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${categoryInfo.bgColor} ${categoryInfo.color}`}>
                              {categoryInfo.name}
                            </span>
                            {template.regulatoryRefs?.slice(0, 2).map((ref) => (
                              <span key={ref} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                {ref}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Template Detail Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${getCategoryInfo(selectedTemplate.category).bgColor}`}>
                  <DocumentTextIcon className={`h-6 w-6 ${getCategoryInfo(selectedTemplate.category).color}`} />
                </div>
                <div className="ml-3">
                  <h2 className="text-xl font-bold text-gray-900">{selectedTemplate.name}</h2>
                  <p className="text-sm text-gray-500">{getCategoryInfo(selectedTemplate.category).name}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedTemplate(null)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <XMarkIcon className="h-5 w-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-1">Описание</h3>
                <p className="text-gray-900">{selectedTemplate.description}</p>
              </div>

              {selectedTemplate.regulatoryRefs && selectedTemplate.regulatoryRefs.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Нормативные ссылки</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedTemplate.regulatoryRefs.map((ref) => (
                      <span key={ref} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-50 text-blue-700">
                        {ref}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Теги</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.tags.map((tag) => (
                    <span key={tag} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
                <button className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <DocumentTextIcon className="h-5 w-5 mr-2" />
                  Создать документ
                </button>
                <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  <ArrowDownTrayIcon className="h-5 w-5 mr-2 text-gray-500" />
                  Скачать шаблон
                </button>
                <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  <ShareIcon className="h-5 w-5 mr-2 text-gray-500" />
                  Поделиться
                </button>
                <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  <ArchiveBoxIcon className="h-5 w-5 mr-2 text-gray-500" />
                  В архив
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SMETemplates;
