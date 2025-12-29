import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
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
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import { russianComplianceApi } from '../services/api';

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
  keyActions: string[];
  typicalDuration: string;
}

interface ApiTemplate {
  id: string;
  name: string;
  category: string;
  priority: 'required' | 'recommended' | 'optional';
  description: string | null;
}

interface ApiLifecycleStage {
  stage: string;
  stage_name: string;
  templates: ApiTemplate[];
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
  },
];

const PRIORITY_COLORS = {
  required: { bg: 'bg-red-100', text: 'text-red-700', label: 'Обязательно' },
  recommended: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Рекомендуется' },
  optional: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Опционально' },
};

const CompanyLifecycle: React.FC = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const [selectedStage, setSelectedStage] = useState<LifecycleStage>('idea');
  const [showAllTemplates, setShowAllTemplates] = useState(false);

  // Bilingual translations
  const t = {
    title: language === 'ru' ? 'Навигатор жизненного цикла компании' : 'Company Lifecycle Navigator',
    subtitle: language === 'ru' ? 'Выберите этап развития вашей компании для получения рекомендаций по документам' : 'Select your company stage to get document recommendations',
    typicalDuration: language === 'ru' ? 'Типичная длительность' : 'Typical duration',
    keyActions: language === 'ru' ? 'Ключевые действия' : 'Key actions',
    stageStats: language === 'ru' ? 'Статистика этапа' : 'Stage statistics',
    templates: language === 'ru' ? 'Шаблонов' : 'Templates',
    required: language === 'ru' ? 'Обязательных' : 'Required',
    recommendedDocs: language === 'ru' ? 'Рекомендуемые документы' : 'Recommended documents',
    showMain: language === 'ru' ? 'Показать основные' : 'Show main',
    showAll: language === 'ru' ? 'Показать все' : 'Show all',
    loading: language === 'ru' ? 'Загрузка шаблонов...' : 'Loading templates...',
    noTemplates: language === 'ru' ? 'Нет шаблонов для этого этапа' : 'No templates for this stage',
    category: language === 'ru' ? 'Категория' : 'Category',
    createAllDocs: language === 'ru' ? 'Создать все обязательные документы' : 'Create all required documents',
    nextStage: language === 'ru' ? 'Следующий этап' : 'Next stage',
    docs: language === 'ru' ? 'док.' : 'docs',
  };

  const currentStage = LIFECYCLE_STAGES.find(s => s.id === selectedStage)!;

  // Fetch lifecycle templates from API
  const { data: lifecycleData, isLoading } = useQuery({
    queryKey: ['lifecycle-templates'],
    queryFn: async () => {
      const response = await russianComplianceApi.lifecycleTemplates.listAll();
      return response.data as ApiLifecycleStage[];
    },
  });

  // Get templates for current stage from API data
  const apiTemplates = lifecycleData?.find(s => s.stage === selectedStage)?.templates || [];

  const handleTemplateClick = (templateId: string) => {
    // Navigate to SME templates page with template pre-selected
    navigate(`/sme-templates?template=${templateId}`);
  };

  const handleCreateAllDocuments = () => {
    // Navigate to SME templates with stage filter
    navigate(`/sme-templates?stage=${selectedStage}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            {t.title}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {t.subtitle}
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
              const stageTemplates = lifecycleData?.find(s => s.stage === stage.id)?.templates || [];
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
                    {stageTemplates.length > 0 && (
                      <span className="mt-0.5 text-[10px] text-gray-400">
                        {stageTemplates.length} {t.docs}
                      </span>
                    )}
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
                <span>{t.typicalDuration}: {currentStage.typicalDuration}</span>
              </div>

              <div className="mt-6">
                <h3 className="font-medium text-gray-900 mb-3">{t.keyActions}:</h3>
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
              <h3 className="font-medium text-gray-900 mb-4">{t.stageStats}</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {isLoading ? '...' : apiTemplates.length}
                  </div>
                  <div className="text-xs text-gray-500">{t.templates}</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {isLoading ? '...' : apiTemplates.filter(tmpl => tmpl.priority === 'required').length}
                  </div>
                  <div className="text-xs text-gray-500">{t.required}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Templates List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="font-medium text-gray-900">
                  {t.recommendedDocs}
                </h3>
                <button
                  onClick={() => setShowAllTemplates(!showAllTemplates)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {showAllTemplates ? t.showMain : t.showAll}
                </button>
              </div>

              {isLoading ? (
                <div className="p-8 text-center text-gray-500">
                  {t.loading}
                </div>
              ) : apiTemplates.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  {t.noTemplates}
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {apiTemplates
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
                              <p className="text-sm text-gray-500 mt-0.5">
                                {template.description || `${t.category}: ${template.category}`}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span
                              className={`px-2 py-1 text-xs font-medium rounded-full ${
                                PRIORITY_COLORS[template.priority]?.bg || 'bg-gray-100'
                              } ${PRIORITY_COLORS[template.priority]?.text || 'text-gray-700'}`}
                            >
                              {PRIORITY_COLORS[template.priority]?.label || template.priority}
                            </span>
                            <ArrowDownTrayIcon className="h-4 w-4 text-gray-400" />
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              )}

              {/* CTA */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <button
                  onClick={handleCreateAllDocuments}
                  className={`w-full py-2 px-4 rounded-lg font-medium text-white ${
                    currentStage.color.replace('text-', 'bg-')
                  } hover:opacity-90 transition-opacity`}
                >
                  {t.createAllDocs}
                </button>
              </div>
            </div>

            {/* Next Stage Preview */}
            {selectedStage !== 'exit' && (
              <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="font-medium text-gray-900 mb-2">{t.nextStage}</h3>
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
