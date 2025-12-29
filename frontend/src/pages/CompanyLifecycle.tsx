import React, { useState } from 'react';
import {
  LightBulbIcon,
  BuildingOfficeIcon,
  RocketLaunchIcon,
  ArrowTrendingUpIcon,
  CheckBadgeIcon,
  GlobeAltIcon,
  ArrowPathIcon,
  ArrowRightOnRectangleIcon,
  DocumentTextIcon,
  ChevronRightIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

// Company lifecycle stages
type LifecycleStage =
  | 'idea'
  | 'registration'
  | 'launch'
  | 'growth'
  | 'maturity'
  | 'expansion'
  | 'restructuring'
  | 'exit';

interface StageInfo {
  id: LifecycleStage;
  name: string;
  nameEn: string;
  description: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  borderColor: string;
  templates: TemplateRecommendation[];
  keyActions: string[];
  typicalDuration: string;
}

interface TemplateRecommendation {
  id: string;
  name: string;
  category: string;
  priority: 'required' | 'recommended' | 'optional';
  description: string;
}

const LIFECYCLE_STAGES: StageInfo[] = [
  {
    id: 'idea',
    name: 'Идея',
    nameEn: 'Idea',
    description: 'Разработка бизнес-концепции и подготовка к регистрации',
    icon: LightBulbIcon,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    typicalDuration: '1-3 месяца',
    keyActions: [
      'Разработка бизнес-плана',
      'Поиск соучредителей',
      'Защита интеллектуальной собственности',
      'Предварительные договоренности',
    ],
    templates: [
      { id: 'founders_agreement', name: 'Соглашение учредителей', category: 'corporate', priority: 'required', description: 'Определение долей и обязанностей' },
      { id: 'nda', name: 'Соглашение о конфиденциальности (NDA)', category: 'contracts', priority: 'required', description: 'Защита бизнес-идеи' },
      { id: 'preliminary_agreement', name: 'Предварительный договор', category: 'contracts', priority: 'recommended', description: 'Фиксация договоренностей' },
      { id: 'ip_assignment', name: 'Договор об отчуждении ИС', category: 'legal', priority: 'optional', description: 'Передача прав на разработки' },
    ],
  },
  {
    id: 'registration',
    name: 'Регистрация',
    nameEn: 'Registration',
    description: 'Официальное создание юридического лица',
    icon: BuildingOfficeIcon,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    typicalDuration: '2-4 недели',
    keyActions: [
      'Выбор организационно-правовой формы',
      'Подготовка учредительных документов',
      'Регистрация в ФНС',
      'Открытие расчетного счета',
    ],
    templates: [
      { id: 'charter_ooo', name: 'Устав ООО', category: 'corporate', priority: 'required', description: 'Основной учредительный документ' },
      { id: 'formation_decision_sole', name: 'Решение о создании (единст. учредитель)', category: 'corporate', priority: 'required', description: 'Для ООО с одним учредителем' },
      { id: 'formation_decision_multiple', name: 'Протокол собрания учредителей', category: 'corporate', priority: 'required', description: 'Для ООО с несколькими учредителями' },
      { id: 'usn_application', name: 'Заявление о переходе на УСН', category: 'tax', priority: 'recommended', description: 'Упрощенная система налогообложения' },
      { id: 'account_opening', name: 'Заявление на открытие счета', category: 'banking', priority: 'required', description: 'Банковский счет для ООО' },
      { id: 'director_appointment', name: 'Приказ о вступлении в должность директора', category: 'hr', priority: 'required', description: 'Назначение руководителя' },
    ],
  },
  {
    id: 'launch',
    name: 'Запуск',
    nameEn: 'Launch',
    description: 'Начало операционной деятельности',
    icon: RocketLaunchIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    typicalDuration: '1-6 месяцев',
    keyActions: [
      'Найм первых сотрудников',
      'Настройка бухгалтерии',
      'Запуск продаж',
      'Внутренние регламенты',
    ],
    templates: [
      { id: 'employment_contract', name: 'Трудовой договор', category: 'hr', priority: 'required', description: 'Оформление сотрудников' },
      { id: 'internal_labor_rules', name: 'Правила внутреннего трудового распорядка', category: 'hr', priority: 'required', description: 'Обязательный ЛНА' },
      { id: 'accounting_policy', name: 'Учетная политика', category: 'financial', priority: 'required', description: 'Организация бухучета' },
      { id: 'privacy_policy', name: 'Политика конфиденциальности', category: 'legal', priority: 'required', description: 'Для сайта и ПДн' },
      { id: 'online_terms', name: 'Пользовательское соглашение', category: 'legal', priority: 'recommended', description: 'Для онлайн-сервисов' },
      { id: 'pdp_policy', name: 'Политика обработки ПДн (152-ФЗ)', category: 'grc', priority: 'required', description: 'Соответствие 152-ФЗ' },
    ],
  },
  {
    id: 'growth',
    name: 'Рост',
    nameEn: 'Growth',
    description: 'Масштабирование бизнеса',
    icon: ArrowTrendingUpIcon,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    typicalDuration: '1-3 года',
    keyActions: [
      'Расширение команды',
      'Увеличение клиентской базы',
      'Работа с поставщиками',
      'Привлечение финансирования',
    ],
    templates: [
      { id: 'supply', name: 'Договор поставки', category: 'contracts', priority: 'required', description: 'Работа с поставщиками' },
      { id: 'service', name: 'Договор оказания услуг', category: 'contracts', priority: 'required', description: 'Для клиентов-юрлиц' },
      { id: 'lease', name: 'Договор аренды', category: 'contracts', priority: 'recommended', description: 'Расширение площадей' },
      { id: 'loan', name: 'Договор займа', category: 'contracts', priority: 'optional', description: 'Привлечение средств' },
      { id: 'contractor_agreement', name: 'Договор ГПХ', category: 'hr', priority: 'recommended', description: 'Работа с подрядчиками' },
      { id: 'leasing', name: 'Договор лизинга', category: 'banking', priority: 'optional', description: 'Приобретение оборудования' },
    ],
  },
  {
    id: 'maturity',
    name: 'Зрелость',
    nameEn: 'Maturity',
    description: 'Стабильная операционная деятельность',
    icon: CheckBadgeIcon,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    typicalDuration: '3-10 лет',
    keyActions: [
      'Оптимизация процессов',
      'Распределение дивидендов',
      'Сертификация качества',
      'Развитие партнерств',
    ],
    templates: [
      { id: 'dividend_resolution', name: 'Решение о распределении прибыли', category: 'corporate', priority: 'required', description: 'Выплата дивидендов' },
      { id: 'shareholder_meeting', name: 'Протокол общего собрания', category: 'corporate', priority: 'required', description: 'Корпоративные решения' },
      { id: 'quality_manual', name: 'Руководство по качеству', category: 'quality', priority: 'recommended', description: 'Система менеджмента качества' },
      { id: 'sla_agreement', name: 'SLA (Соглашение об уровне сервиса)', category: 'industry', priority: 'recommended', description: 'Гарантии для клиентов' },
      { id: 'distribution', name: 'Дистрибьюторский договор', category: 'contracts', priority: 'optional', description: 'Расширение сбыта' },
    ],
  },
  {
    id: 'expansion',
    name: 'Экспансия',
    nameEn: 'Expansion',
    description: 'Выход на новые рынки и направления',
    icon: GlobeAltIcon,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    typicalDuration: '1-5 лет',
    keyActions: [
      'Создание филиалов',
      'Франчайзинг',
      'M&A активность',
      'Международная экспансия',
    ],
    templates: [
      { id: 'franchise', name: 'Договор франчайзинга', category: 'contracts', priority: 'recommended', description: 'Масштабирование бренда' },
      { id: 'joint_venture', name: 'Договор о совместной деятельности', category: 'contracts', priority: 'recommended', description: 'Партнерство с другими компаниями' },
      { id: 'licensing', name: 'Лицензионный договор', category: 'contracts', priority: 'recommended', description: 'Монетизация ИС' },
      { id: 'branch_regulation', name: 'Положение о филиале', category: 'corporate', priority: 'required', description: 'Создание филиала' },
      { id: 'bank_guarantee', name: 'Банковская гарантия', category: 'banking', priority: 'optional', description: 'Для крупных контрактов' },
    ],
  },
  {
    id: 'restructuring',
    name: 'Реструктуризация',
    nameEn: 'Restructuring',
    description: 'Оптимизация структуры и операций',
    icon: ArrowPathIcon,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    typicalDuration: '6-18 месяцев',
    keyActions: [
      'Реорганизация структуры',
      'Работа с кредиторами',
      'Оптимизация расходов',
      'Изменение бизнес-модели',
    ],
    templates: [
      { id: 'restructuring_plan', name: 'План реструктуризации', category: 'crisis', priority: 'required', description: 'Стратегия изменений' },
      { id: 'creditor_agreement', name: 'Соглашение с кредиторами', category: 'crisis', priority: 'required', description: 'Урегулирование долгов' },
      { id: 'debt_restructuring', name: 'Договор реструктуризации долга', category: 'crisis', priority: 'required', description: 'Изменение условий' },
      { id: 'capital_increase', name: 'Решение об увеличении уставного капитала', category: 'corporate', priority: 'recommended', description: 'Привлечение инвестиций' },
      { id: 'layoff_order', name: 'Приказ о сокращении', category: 'hr', priority: 'optional', description: 'Оптимизация персонала' },
    ],
  },
  {
    id: 'exit',
    name: 'Выход',
    nameEn: 'Exit',
    description: 'Продажа, слияние или ликвидация',
    icon: ArrowRightOnRectangleIcon,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    typicalDuration: '3-12 месяцев',
    keyActions: [
      'Оценка бизнеса',
      'Поиск покупателей',
      'Due diligence',
      'Оформление сделки',
    ],
    templates: [
      { id: 'share_sale', name: 'Договор купли-продажи доли', category: 'corporate', priority: 'required', description: 'Продажа бизнеса' },
      { id: 'voluntary_liquidation', name: 'Заявление о добровольной ликвидации', category: 'crisis', priority: 'required', description: 'Закрытие компании' },
      { id: 'liquidation_decision', name: 'Решение о ликвидации', category: 'corporate', priority: 'required', description: 'Корпоративное решение' },
      { id: 'asset_sale', name: 'Договор продажи активов', category: 'contracts', priority: 'recommended', description: 'Реализация имущества' },
      { id: 'settlement', name: 'Мировое соглашение', category: 'legal', priority: 'optional', description: 'Урегулирование споров' },
    ],
  },
];

const PRIORITY_COLORS = {
  required: { bg: 'bg-red-100', text: 'text-red-700', label: 'Обязательно' },
  recommended: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Рекомендуется' },
  optional: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Опционально' },
};

const CompanyLifecycle: React.FC = () => {
  const [selectedStage, setSelectedStage] = useState<LifecycleStage>('idea');
  const [showAllTemplates, setShowAllTemplates] = useState(false);

  const currentStage = LIFECYCLE_STAGES.find(s => s.id === selectedStage)!;

  const handleTemplateClick = (templateId: string) => {
    // Navigate to template detail or open modal
    console.log('Opening template:', templateId);
    // TODO: Integrate with template generation
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Навигатор жизненного цикла компании
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Выберите этап развития вашей компании для получения рекомендаций по документам
          </p>
        </div>
      </div>

      {/* Stage Timeline */}
      <div className="bg-white border-b border-gray-200 overflow-x-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex space-x-2 min-w-max">
            {LIFECYCLE_STAGES.map((stage, index) => {
              const Icon = stage.icon;
              const isSelected = selectedStage === stage.id;
              return (
                <React.Fragment key={stage.id}>
                  <button
                    onClick={() => setSelectedStage(stage.id)}
                    className={`flex flex-col items-center p-3 rounded-lg transition-all ${
                      isSelected
                        ? `${stage.bgColor} ${stage.borderColor} border-2`
                        : 'hover:bg-gray-100 border-2 border-transparent'
                    }`}
                  >
                    <div className={`p-2 rounded-full ${isSelected ? stage.bgColor : 'bg-gray-100'}`}>
                      <Icon className={`h-6 w-6 ${isSelected ? stage.color : 'text-gray-400'}`} />
                    </div>
                    <span className={`mt-1 text-xs font-medium ${isSelected ? stage.color : 'text-gray-500'}`}>
                      {stage.name}
                    </span>
                  </button>
                  {index < LIFECYCLE_STAGES.length - 1 && (
                    <div className="flex items-center">
                      <ChevronRightIcon className="h-4 w-4 text-gray-300" />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Stage Details */}
          <div className="lg:col-span-1">
            <div className={`rounded-lg ${currentStage.bgColor} ${currentStage.borderColor} border-2 p-6`}>
              <div className="flex items-center">
                <div className={`p-3 rounded-full bg-white`}>
                  <currentStage.icon className={`h-8 w-8 ${currentStage.color}`} />
                </div>
                <div className="ml-4">
                  <h2 className={`text-xl font-bold ${currentStage.color}`}>
                    {currentStage.name}
                  </h2>
                  <p className="text-sm text-gray-600">{currentStage.nameEn}</p>
                </div>
              </div>

              <p className="mt-4 text-gray-700">{currentStage.description}</p>

              <div className="mt-4 flex items-center text-sm text-gray-600">
                <ClockIcon className="h-4 w-4 mr-1" />
                <span>Типичная длительность: {currentStage.typicalDuration}</span>
              </div>

              <div className="mt-6">
                <h3 className="font-medium text-gray-900 mb-3">Ключевые действия:</h3>
                <ul className="space-y-2">
                  {currentStage.keyActions.map((action, index) => (
                    <li key={index} className="flex items-start">
                      <span className={`mt-1.5 h-1.5 w-1.5 rounded-full ${currentStage.color.replace('text-', 'bg-')} mr-2`} />
                      <span className="text-sm text-gray-700">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Statistics */}
            <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-medium text-gray-900 mb-4">Статистика этапа</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {currentStage.templates.length}
                  </div>
                  <div className="text-xs text-gray-500">Шаблонов</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {currentStage.templates.filter(t => t.priority === 'required').length}
                  </div>
                  <div className="text-xs text-gray-500">Обязательных</div>
                </div>
              </div>
            </div>
          </div>

          {/* Templates List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="font-medium text-gray-900">
                  Рекомендуемые документы
                </h3>
                <button
                  onClick={() => setShowAllTemplates(!showAllTemplates)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {showAllTemplates ? 'Показать основные' : 'Показать все'}
                </button>
              </div>

              <div className="divide-y divide-gray-200">
                {currentStage.templates
                  .filter(t => showAllTemplates || t.priority !== 'optional')
                  .map((template) => (
                    <div
                      key={template.id}
                      className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleTemplateClick(template.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start">
                          <DocumentTextIcon className="h-5 w-5 text-gray-400 mt-0.5 mr-3" />
                          <div>
                            <h4 className="font-medium text-gray-900">{template.name}</h4>
                            <p className="text-sm text-gray-500 mt-0.5">{template.description}</p>
                          </div>
                        </div>
                        <span
                          className={`ml-4 px-2 py-1 text-xs font-medium rounded-full ${
                            PRIORITY_COLORS[template.priority].bg
                          } ${PRIORITY_COLORS[template.priority].text}`}
                        >
                          {PRIORITY_COLORS[template.priority].label}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>

              {/* CTA */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <button
                  className={`w-full py-2 px-4 rounded-lg font-medium text-white ${
                    currentStage.color.replace('text-', 'bg-')
                  } hover:opacity-90 transition-opacity`}
                >
                  Создать все обязательные документы
                </button>
              </div>
            </div>

            {/* Next Stage Preview */}
            {selectedStage !== 'exit' && (
              <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="font-medium text-gray-900 mb-2">Следующий этап</h3>
                {(() => {
                  const currentIndex = LIFECYCLE_STAGES.findIndex(s => s.id === selectedStage);
                  const nextStage = LIFECYCLE_STAGES[currentIndex + 1];
                  if (!nextStage) return null;

                  return (
                    <button
                      onClick={() => setSelectedStage(nextStage.id)}
                      className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center">
                        <div className={`p-2 rounded-full ${nextStage.bgColor}`}>
                          <nextStage.icon className={`h-5 w-5 ${nextStage.color}`} />
                        </div>
                        <div className="ml-3 text-left">
                          <div className="font-medium text-gray-900">{nextStage.name}</div>
                          <div className="text-sm text-gray-500">{nextStage.description}</div>
                        </div>
                      </div>
                      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                    </button>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyLifecycle;
