import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  SparklesIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  CalendarIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';
import { useLanguage } from '../../contexts/LanguageContext';

interface TourStep {
  id: string;
  title: string;
  titleRu: string;
  description: string;
  descriptionRu: string;
  targetSelector?: string;
  route?: string;
  icon: React.ElementType;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
}

const TOUR_STEPS: TourStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to CORTEX AI',
    titleRu: 'Добро пожаловать в CORTEX AI',
    description: 'Your comprehensive platform for Russian regulatory compliance. This tour will guide you through the key features.',
    descriptionRu: 'Ваша комплексная платформа для соответствия российским нормативным требованиям. Этот тур познакомит вас с ключевыми функциями.',
    icon: SparklesIcon,
    position: 'center',
  },
  {
    id: 'dashboard',
    title: 'GRC Dashboard',
    titleRu: 'Панель управления GRC',
    description: 'Your central hub for compliance monitoring. View overall compliance scores, risk heat maps, and upcoming tasks at a glance.',
    descriptionRu: 'Ваш центр мониторинга соответствия. Просматривайте общие оценки соответствия, карты рисков и предстоящие задачи.',
    route: '/dashboard',
    icon: ChartBarIcon,
    position: 'center',
  },
  {
    id: 'russian-compliance',
    title: 'Russian Compliance (152-ФЗ)',
    titleRu: 'Российское соответствие (152-ФЗ)',
    description: 'Manage your company profile, ISPDN systems, and generate required documents for 152-ФЗ compliance.',
    descriptionRu: 'Управляйте профилем компании, системами ИСПДн и генерируйте необходимые документы для соответствия 152-ФЗ.',
    route: '/russian-compliance',
    icon: ShieldCheckIcon,
    position: 'center',
  },
  {
    id: 'templates',
    title: 'Template Catalog',
    titleRu: 'Каталог шаблонов',
    description: 'Browse 90+ document templates for 152-ФЗ, 187-ФЗ (КИИ), and ГОСТ Р 57580. Generate documents with automatic company data fill.',
    descriptionRu: 'Просмотрите 90+ шаблонов документов для 152-ФЗ, 187-ФЗ (КИИ) и ГОСТ Р 57580. Генерируйте документы с автоматическим заполнением данных компании.',
    route: '/templates',
    icon: DocumentTextIcon,
    position: 'center',
  },
  {
    id: 'documents',
    title: 'Document Library',
    titleRu: 'Библиотека документов',
    description: 'Store and manage all your compliance documents. Track versions, manage approvals, and link documents to controls.',
    descriptionRu: 'Храните и управляйте всеми документами соответствия. Отслеживайте версии, управляйте утверждениями и связывайте документы с контролями.',
    route: '/documents',
    icon: FolderIcon,
    position: 'center',
  },
  {
    id: 'tasks',
    title: 'Compliance Tasks',
    titleRu: 'Задачи соответствия',
    description: 'Manage compliance tasks with a Kanban board. Set due dates, assign owners, and track progress with automatic reminders.',
    descriptionRu: 'Управляйте задачами соответствия с помощью Kanban-доски. Устанавливайте сроки, назначайте ответственных и отслеживайте прогресс с автоматическими напоминаниями.',
    route: '/compliance-tasks',
    icon: CheckCircleIcon,
    position: 'center',
  },
  {
    id: 'calendar',
    title: 'Compliance Calendar',
    titleRu: 'Календарь соответствия',
    description: 'View all compliance deadlines in a calendar format. Never miss a regulatory deadline with visual timeline tracking.',
    descriptionRu: 'Просматривайте все сроки соответствия в формате календаря. Никогда не пропускайте сроки с визуальным отслеживанием.',
    route: '/compliance-calendar',
    icon: CalendarIcon,
    position: 'center',
  },
  {
    id: 'complete',
    title: 'You\'re Ready!',
    titleRu: 'Вы готовы!',
    description: 'You\'ve completed the tour. Start by adding your company using INN in the Russian Compliance section. Need help? Use Shift+? for keyboard shortcuts.',
    descriptionRu: 'Вы завершили тур. Начните с добавления вашей компании по ИНН в разделе Российское соответствие. Нужна помощь? Нажмите Shift+? для клавиатурных сокращений.',
    icon: SparklesIcon,
    position: 'center',
  },
];

const TOUR_STORAGE_KEY = 'cortex_tour_completed';
const TOUR_SHOWN_KEY = 'cortex_tour_shown';

export function useOnboardingTour() {
  const [showTour, setShowTour] = useState(false);
  const [hasSeenTour, setHasSeenTour] = useState(true);

  useEffect(() => {
    const tourCompleted = localStorage.getItem(TOUR_STORAGE_KEY);
    const tourShown = sessionStorage.getItem(TOUR_SHOWN_KEY);

    // Show tour on first visit if not completed
    if (!tourCompleted && !tourShown) {
      setHasSeenTour(false);
      // Show tour after a short delay
      const timer = setTimeout(() => {
        setShowTour(true);
        sessionStorage.setItem(TOUR_SHOWN_KEY, 'true');
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const startTour = useCallback(() => {
    setShowTour(true);
  }, []);

  const endTour = useCallback(() => {
    setShowTour(false);
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setHasSeenTour(true);
  }, []);

  const resetTour = useCallback(() => {
    localStorage.removeItem(TOUR_STORAGE_KEY);
    setHasSeenTour(false);
  }, []);

  return { showTour, hasSeenTour, startTour, endTour, resetTour };
}

interface OnboardingTourProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function OnboardingTour({ isOpen, onClose }: OnboardingTourProps) {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const [currentStep, setCurrentStep] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const step = TOUR_STEPS[currentStep];
  const isRussian = language === 'ru';
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === TOUR_STEPS.length - 1;

  useEffect(() => {
    if (isOpen && step.route && location.pathname !== step.route) {
      setIsTransitioning(true);
      navigate(step.route);
      const timer = setTimeout(() => setIsTransitioning(false), 500);
      return () => clearTimeout(timer);
    }
  }, [isOpen, step.route, location.pathname, navigate]);

  const handleNext = () => {
    if (isLastStep) {
      onClose();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  if (!isOpen) return null;

  const Icon = step.icon;

  const content = (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={handleSkip}
      />

      {/* Tour Card */}
      <div
        className={`relative bg-white dark:bg-dark-800 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden transition-all transform ${
          isTransitioning ? 'opacity-50 scale-95' : 'opacity-100 scale-100'
        }`}
      >
        {/* Header with gradient */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-xl">
                <Icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-primary-200 text-sm">
                  {isRussian ? 'Шаг' : 'Step'} {currentStep + 1} / {TOUR_STEPS.length}
                </p>
                <h2 className="text-xl font-bold">
                  {isRussian ? step.titleRu : step.title}
                </h2>
              </div>
            </div>
            <button
              onClick={handleSkip}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-1 bg-gray-200 dark:bg-dark-600">
          <div
            className="h-full bg-primary-500 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / TOUR_STEPS.length) * 100}%` }}
          />
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
            {isRussian ? step.descriptionRu : step.description}
          </p>
        </div>

        {/* Step indicators */}
        <div className="flex justify-center gap-2 pb-4">
          {TOUR_STEPS.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentStep(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentStep
                  ? 'w-6 bg-primary-500'
                  : index < currentStep
                    ? 'bg-primary-300 dark:bg-primary-700'
                    : 'bg-gray-300 dark:bg-dark-500'
              }`}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 pb-6 flex items-center justify-between">
          <button
            onClick={handleSkip}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-sm"
          >
            {isRussian ? 'Пропустить тур' : 'Skip tour'}
          </button>

          <div className="flex items-center gap-3">
            {!isFirstStep && (
              <button
                onClick={handlePrev}
                className="flex items-center gap-1 px-4 py-2 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-dark-500 rounded-lg hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
              >
                <ChevronLeftIcon className="h-4 w-4" />
                {isRussian ? 'Назад' : 'Back'}
              </button>
            )}
            <button
              onClick={handleNext}
              className="flex items-center gap-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              {isLastStep
                ? (isRussian ? 'Начать работу' : 'Get Started')
                : (isRussian ? 'Далее' : 'Next')
              }
              {!isLastStep && <ChevronRightIcon className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}

// Start Tour Button component for use in Settings or Help sections
export function StartTourButton() {
  const { language } = useLanguage();
  const { startTour } = useOnboardingTour();

  return (
    <button
      onClick={startTour}
      className="flex items-center gap-2 px-4 py-2 text-primary-600 dark:text-primary-400 border border-primary-300 dark:border-primary-700 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
    >
      <SparklesIcon className="h-5 w-5" />
      {language === 'ru' ? 'Начать тур' : 'Start Tour'}
    </button>
  );
}
