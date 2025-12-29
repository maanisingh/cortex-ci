import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import {
  ShieldCheckIcon,
  ChartBarIcon,
  DocumentCheckIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  ExclamationTriangleIcon,
  CpuChipIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  LockClosedIcon,
  BoltIcon,
  DocumentTextIcon,
  MagnifyingGlassCircleIcon,
  ClipboardDocumentCheckIcon,
  UserGroupIcon,
  ScaleIcon,
  PresentationChartLineIcon,
  SparklesIcon,
  CloudArrowUpIcon,
  ServerIcon,
  CommandLineIcon,
} from "@heroicons/react/24/outline";
import { useLanguage, LANGUAGES, LanguageCode } from "../contexts/LanguageContext";

const internationalFrameworks = [
  { name: "NIST SP 800-53", controls: 1196, category: "Security" },
  { name: "ISO 27001:2022", controls: 93, category: "ISMS" },
  { name: "SOC 2 Type II", controls: 64, category: "Trust Services" },
  { name: "PCI-DSS v4.0", controls: 251, category: "Payment Security" },
  { name: "GDPR", controls: 99, category: "Privacy" },
  { name: "HIPAA", controls: 75, category: "Healthcare" },
  { name: "MITRE ATT&CK", controls: 703, category: "Threat Intel" },
  { name: "CIS Controls v8", controls: 153, category: "Security" },
];

const russianFrameworks = [
  { name: "152-ФЗ", controls: 48, category: "Персональные данные", description: "Защита персональных данных" },
  { name: "187-ФЗ", controls: 85, category: "КИИ", description: "Критическая инфраструктура" },
  { name: "ГОСТ Р 57580", controls: 150, category: "Финансы", description: "Безопасность банковских операций" },
  { name: "ФСТЭК №21", controls: 72, category: "ИСПДн", description: "Защита информационных систем" },
  { name: "683-П ЦБ", controls: 95, category: "Банки", description: "Требования ЦБ РФ" },
  { name: "ФСБ №378", controls: 60, category: "Крипто", description: "Криптографическая защита" },
];

const documentCategories = [
  { name: "Contracts & Agreements", nameRu: "Договоры", icon: "📝", count: "45+", description: "Service, sales, NDA, partnership" },
  { name: "Corporate Documents", nameRu: "Корпоративные", icon: "🏢", count: "35+", description: "Charters, protocols, resolutions" },
  { name: "HR & Employment", nameRu: "Кадры", icon: "👥", count: "50+", description: "Contracts, orders, policies" },
  { name: "Financial & Tax", nameRu: "Финансы", icon: "💰", count: "40+", description: "Invoices, acts, reports" },
  { name: "Legal & Compliance", nameRu: "Право", icon: "⚖️", count: "60+", description: "Policies, consents, GDPR" },
  { name: "Operations", nameRu: "Операционные", icon: "⚙️", count: "55+", description: "SOPs, instructions, memos" },
];

export default function LandingPage() {
  const { t, language, setLanguage } = useLanguage();
  const [scrollY, setScrollY] = useState(0);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Auto-rotate dashboard tabs
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTab((prev) => (prev + 1) % 4);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const grcModules = [
    {
      name: t("governance"),
      description: t("governanceDesc"),
      icon: DocumentTextIcon,
      color: "from-purple-500 to-indigo-600",
    },
    {
      name: t("riskManagementModule"),
      description: t("riskManagementDesc"),
      icon: ExclamationTriangleIcon,
      color: "from-red-500 to-orange-600",
    },
    {
      name: t("complianceModule"),
      description: t("complianceModuleDesc"),
      icon: DocumentCheckIcon,
      color: "from-blue-500 to-cyan-600",
    },
    {
      name: t("auditManagement"),
      description: t("auditManagementDesc"),
      icon: MagnifyingGlassCircleIcon,
      color: "from-green-500 to-emerald-600",
    },
    {
      name: t("incidentResponse"),
      description: t("incidentResponseDesc"),
      icon: ShieldCheckIcon,
      color: "from-orange-500 to-amber-600",
    },
    {
      name: t("thirdPartyRisk"),
      description: t("thirdPartyRiskDesc"),
      icon: UserGroupIcon,
      color: "from-amber-500 to-yellow-600",
    },
  ];

  const capabilities = [
    {
      name: t("realTimeRiskScoring"),
      description: t("realTimeRiskScoringDesc"),
      icon: ChartBarIcon,
    },
    {
      name: t("crossLayerAnalysisFeature"),
      description: t("crossLayerAnalysisDesc"),
      icon: GlobeAltIcon,
    },
    {
      name: t("monteCarloSimulations"),
      description: t("monteCarloDesc"),
      icon: CpuChipIcon,
    },
    {
      name: t("evidenceLibraryFeature"),
      description: t("evidenceLibraryDesc"),
      icon: ClipboardDocumentCheckIcon,
    },
    {
      name: t("aiPoweredInsights"),
      description: t("aiPoweredInsightsDesc"),
      icon: BoltIcon,
    },
    {
      name: t("executiveDashboards"),
      description: t("executiveDashboardsDesc"),
      icon: PresentationChartLineIcon,
    },
  ];

  const dashboardTabs = [
    {
      title: language === "ru" ? "Главная панель" : "Main Dashboard",
      subtitle: language === "ru" ? "Полный обзор соответствия" : "Complete compliance overview",
      metrics: [
        { label: language === "ru" ? "Оценка риска" : "Risk Score", value: "87%", change: "+5%", color: "text-green-400" },
        { label: language === "ru" ? "Соответствие" : "Compliance", value: "94%", change: "+3%", color: "text-green-400" },
        { label: language === "ru" ? "Открытых задач" : "Open Tasks", value: "23", change: "-8", color: "text-yellow-400" },
        { label: language === "ru" ? "Аудитов" : "Audits", value: "12", change: "+2", color: "text-blue-400" },
      ],
    },
    {
      title: language === "ru" ? "Управление рисками" : "Risk Management",
      subtitle: language === "ru" ? "Анализ и митигация" : "Analysis & mitigation",
      metrics: [
        { label: language === "ru" ? "Критических" : "Critical", value: "3", change: "-2", color: "text-red-400" },
        { label: language === "ru" ? "Высоких" : "High", value: "12", change: "-5", color: "text-orange-400" },
        { label: language === "ru" ? "Средних" : "Medium", value: "34", change: "-12", color: "text-yellow-400" },
        { label: language === "ru" ? "Низких" : "Low", value: "89", change: "+8", color: "text-green-400" },
      ],
    },
    {
      title: language === "ru" ? "Документация" : "Documentation",
      subtitle: language === "ru" ? "AI-генерация документов" : "AI-powered document generation",
      metrics: [
        { label: language === "ru" ? "Шаблонов" : "Templates", value: "285", change: "+15", color: "text-purple-400" },
        { label: language === "ru" ? "Созданных" : "Generated", value: "1.2K", change: "+234", color: "text-blue-400" },
        { label: language === "ru" ? "Ожидающих" : "Pending", value: "8", change: "-3", color: "text-yellow-400" },
        { label: language === "ru" ? "Одобренных" : "Approved", value: "156", change: "+28", color: "text-green-400" },
      ],
    },
    {
      title: language === "ru" ? "Аналитика" : "Analytics",
      subtitle: language === "ru" ? "Бизнес-интеллект" : "Business intelligence",
      metrics: [
        { label: language === "ru" ? "Отчётов" : "Reports", value: "48", change: "+12", color: "text-indigo-400" },
        { label: language === "ru" ? "Инсайтов" : "Insights", value: "127", change: "+45", color: "text-cyan-400" },
        { label: language === "ru" ? "Трендов" : "Trends", value: "23", change: "+8", color: "text-emerald-400" },
        { label: language === "ru" ? "Прогнозов" : "Forecasts", value: "15", change: "+5", color: "text-violet-400" },
      ],
    },
  ];

  const personas = [
    {
      title: t("chiefRiskOfficer"),
      description: t("croDescription"),
      benefits: [
        t("croBenefit1"),
        t("croBenefit2"),
        t("croBenefit3"),
        t("croBenefit4"),
      ],
    },
    {
      title: t("complianceManager"),
      description: t("cmDescription"),
      benefits: [
        t("cmBenefit1"),
        t("cmBenefit2"),
        t("cmBenefit3"),
        t("cmBenefit4"),
      ],
    },
    {
      title: t("internalAuditor"),
      description: t("iaDescription"),
      benefits: [
        t("iaBenefit1"),
        t("iaBenefit2"),
        t("iaBenefit3"),
        t("iaBenefit4"),
      ],
    },
  ];

  return (
    <div className="bg-slate-950 text-white overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                             radial-gradient(circle at 75% 75%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
                             radial-gradient(circle at 50% 50%, rgba(34, 211, 238, 0.1) 0%, transparent 50%)`,
            transform: `translateY(${scrollY * 0.1}px)`,
          }}
        />
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/5">
        <nav className="flex items-center justify-between p-6 lg:px-8 max-w-7xl mx-auto">
          <div className="flex lg:flex-1">
            <span className="text-2xl font-bold flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <DocumentTextIcon className="w-6 h-6 text-white" />
              </div>
              <span className="text-white">CORTEX</span>
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-x-6">
            {/* Language Selector */}
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as LanguageCode)}
              className="text-sm bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all cursor-pointer"
            >
              {Object.entries(LANGUAGES).map(([code, { nativeName, flag }]) => (
                <option key={code} value={code} className="bg-slate-900 text-white">
                  {flag} {nativeName}
                </option>
              ))}
            </select>
            <Link
              to="/login"
              className="text-sm font-medium text-gray-300 hover:text-white transition-colors"
            >
              {t("signIn")}
            </Link>
            <Link
              to="/login"
              className="rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-105 transition-all"
            >
              {t("getStarted")}
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <div className="relative z-10 pt-16 pb-24 sm:pt-24 sm:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-4xl text-center">
            {/* Badges */}
            <div className="mb-8 flex justify-center gap-3 flex-wrap">
              <div className="rounded-full px-4 py-2 text-sm font-medium bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-purple-300 ring-1 ring-purple-500/30 flex items-center gap-2">
                <SparklesIcon className="w-4 h-4" />
                {language === "ru" ? "AI-генерация" : "AI-Powered"}
              </div>
              <div className="rounded-full px-4 py-2 text-sm font-medium bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20">
                📄 {language === "ru" ? "285+ шаблонов" : "285+ Templates"}
              </div>
              <div className="rounded-full px-4 py-2 text-sm font-medium bg-green-500/10 text-green-400 ring-1 ring-green-500/20">
                {language === "ru" ? "Все документы бизнеса" : "All Business Documents"}
              </div>
              <div className="rounded-full px-4 py-2 text-sm font-medium bg-cyan-500/10 text-cyan-400 ring-1 ring-cyan-500/20">
                🇷🇺 {language === "ru" ? "RU/EN" : "RU/EN Support"}
              </div>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl font-bold tracking-tight sm:text-7xl">
              <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
                {language === "ru" ? "AI Делопроизводство" : "AI Paperwork"}
              </span>
              <span className="text-white">
                {language === "ru" ? " для бизнеса" : " for Business"}
              </span>
            </h1>

            <p className="mt-6 text-xl leading-8 text-gray-400 max-w-2xl mx-auto">
              {language === "ru"
                ? "Создавайте любые бизнес-документы за секунды. Договоры, кадровые приказы, финансовые отчёты, корпоративные документы — всё с помощью AI."
                : "Generate any business document in seconds. Contracts, HR orders, financial reports, corporate documents — all powered by AI."}
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/login"
                className="w-full sm:w-auto rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-4 text-lg font-semibold text-white shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-105 transition-all flex items-center justify-center gap-2"
              >
                {language === "ru" ? "Начать бесплатно" : "Start Free Trial"}
                <ArrowRightIcon className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto rounded-2xl bg-white/5 px-8 py-4 text-lg font-semibold text-white ring-1 ring-white/10 hover:bg-white/10 transition-all flex items-center justify-center gap-2"
              >
                <CommandLineIcon className="w-5 h-5" />
                {language === "ru" ? "Посмотреть демо" : "Watch Demo"}
              </Link>
            </div>

            <p className="mt-4 text-sm text-gray-500">
              {language === "ru"
                ? "Бесплатно для МСП • Не требуется карта • Настройка за 5 минут"
                : "Free for SMEs • No credit card • 5-minute setup"}
            </p>
          </div>

          {/* Stats Row */}
          <div className="mx-auto mt-16 max-w-5xl">
            <dl className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {[
                { value: "285+", label: language === "ru" ? "Шаблонов" : "Templates" },
                { value: "6", label: language === "ru" ? "Категорий" : "Categories" },
                { value: "< 30с", label: language === "ru" ? "Генерация" : "Generation" },
                { value: "99.9%", label: language === "ru" ? "Uptime" : "Uptime" },
              ].map((stat) => (
                <div key={stat.label} className="group relative rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 hover:bg-white/10 hover:ring-blue-500/50 transition-all">
                  <dt className="text-sm text-gray-400">{stat.label}</dt>
                  <dd className="text-3xl font-bold text-white mt-1 group-hover:text-blue-400 transition-colors">{stat.value}</dd>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Document Categories Section */}
      <div className="relative z-10 py-24 sm:py-32 bg-gradient-to-b from-transparent via-blue-950/20 to-transparent">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-blue-400">
              {language === "ru" ? "Полный охват документооборота" : "Complete Document Coverage"}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {language === "ru" ? "Все документы вашего бизнеса" : "All Your Business Documents"}
            </p>
            <p className="mt-4 text-lg text-gray-400">
              {language === "ru"
                ? "От договоров до кадровых приказов — генерируйте любой документ за секунды"
                : "From contracts to HR orders — generate any document in seconds"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documentCategories.map((category) => (
              <div
                key={category.name}
                className="group relative rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 hover:ring-blue-500/50 transition-all"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-3xl">{category.icon}</span>
                  <span className="rounded-full bg-blue-500/10 px-3 py-1 text-sm font-medium text-blue-400">
                    {category.count}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-white">
                  {language === "ru" ? category.nameRu : category.name}
                </h3>
                <p className="mt-2 text-sm text-gray-400">{category.description}</p>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dashboard Preview Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-blue-400">
              {language === "ru" ? "Интерактивные дашборды" : "Interactive Dashboards"}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {language === "ru" ? "Все метрики в одном месте" : "All Metrics in One Place"}
            </p>
          </div>

          {/* Dashboard Mockup */}
          <div className="relative mx-auto max-w-5xl">
            {/* Glow effect */}
            <div className="absolute -inset-4 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-cyan-500/20 rounded-3xl blur-2xl" />

            {/* Dashboard Container */}
            <div className="relative rounded-2xl bg-slate-900/80 ring-1 ring-white/10 overflow-hidden backdrop-blur-xl shadow-2xl">
              {/* Top Bar */}
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-800/50 border-b border-white/5">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="flex-1 text-center text-sm text-gray-400">
                  cortex.alexandratechlab.com
                </div>
              </div>

              {/* Dashboard Tabs */}
              <div className="flex border-b border-white/5">
                {dashboardTabs.map((tab, index) => (
                  <button
                    key={tab.title}
                    onClick={() => setActiveTab(index)}
                    className={`flex-1 px-4 py-3 text-sm font-medium transition-all ${
                      activeTab === index
                        ? "text-blue-400 bg-blue-500/10 border-b-2 border-blue-400"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {tab.title}
                  </button>
                ))}
              </div>

              {/* Dashboard Content */}
              <div className="p-6">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-white">{dashboardTabs[activeTab].title}</h3>
                  <p className="text-sm text-gray-400">{dashboardTabs[activeTab].subtitle}</p>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  {dashboardTabs[activeTab].metrics.map((metric) => (
                    <div key={metric.label} className="rounded-xl bg-slate-800/50 p-4 ring-1 ring-white/5">
                      <p className="text-sm text-gray-400">{metric.label}</p>
                      <p className="text-2xl font-bold text-white mt-1">{metric.value}</p>
                      <p className={`text-sm ${metric.color}`}>{metric.change}</p>
                    </div>
                  ))}
                </div>

                {/* Chart Mockup */}
                <div className="rounded-xl bg-slate-800/30 p-4 ring-1 ring-white/5">
                  <div className="flex items-end justify-between h-32 gap-2">
                    {[65, 80, 45, 90, 75, 85, 70, 95, 60, 88, 72, 92].map((height, i) => (
                      <div
                        key={i}
                        className="flex-1 rounded-t-sm bg-gradient-to-t from-blue-500 to-purple-500 transition-all hover:from-blue-400 hover:to-purple-400"
                        style={{ height: `${height}%`, opacity: 0.3 + (i / 15) }}
                      />
                    ))}
                  </div>
                  <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>Jan</span>
                    <span>Feb</span>
                    <span>Mar</span>
                    <span>Apr</span>
                    <span>May</span>
                    <span>Jun</span>
                    <span>Jul</span>
                    <span>Aug</span>
                    <span>Sep</span>
                    <span>Oct</span>
                    <span>Nov</span>
                    <span>Dec</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Features Section */}
      <div className="relative z-10 py-24 sm:py-32 bg-gradient-to-b from-transparent via-purple-950/20 to-transparent">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <div className="inline-flex items-center gap-2 rounded-full bg-purple-500/10 px-4 py-2 text-sm text-purple-400 ring-1 ring-purple-500/20 mb-4">
              <SparklesIcon className="w-4 h-4" />
              {language === "ru" ? "Наш AI" : "Our AI"}
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {language === "ru" ? "Как это работает" : "How It Works"}
            </h2>
            <p className="mt-4 text-lg text-gray-400">
              {language === "ru"
                ? "Введите данные компании — получите готовые документы за секунды"
                : "Enter company data — get ready documents in seconds"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: DocumentTextIcon,
                title: language === "ru" ? "1. Выберите шаблон" : "1. Choose Template",
                description: language === "ru"
                  ? "285+ готовых шаблонов: договоры, приказы, политики, акты, протоколы"
                  : "285+ ready templates: contracts, orders, policies, acts, protocols",
                gradient: "from-purple-500 to-pink-500",
              },
              {
                icon: SparklesIcon,
                title: language === "ru" ? "2. AI заполняет" : "2. AI Fills In",
                description: language === "ru"
                  ? "Введите ИНН и название — AI заполнит все реквизиты и данные"
                  : "Enter INN and name — AI fills in all details and data",
                gradient: "from-blue-500 to-cyan-500",
              },
              {
                icon: CheckCircleIcon,
                title: language === "ru" ? "3. Готово!" : "3. Done!",
                description: language === "ru"
                  ? "Скачайте в PDF, DOCX или отправьте на подпись через DocuSeal"
                  : "Download as PDF, DOCX or send for signature via DocuSeal",
                gradient: "from-green-500 to-emerald-500",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="group relative rounded-2xl bg-white/5 p-8 ring-1 ring-white/10 hover:ring-white/20 transition-all"
              >
                <div className={`inline-flex items-center justify-center rounded-xl bg-gradient-to-r ${feature.gradient} p-3 shadow-lg`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">{feature.title}</h3>
                <p className="mt-2 text-gray-400">{feature.description}</p>
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity`} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-green-400">
              {language === "ru" ? "Кому подходит" : "Who It's For"}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {language === "ru" ? "Решения для любого бизнеса" : "Solutions for Any Business"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: "🏢",
                title: language === "ru" ? "Стартапы и МСП" : "Startups & SMEs",
                description: language === "ru"
                  ? "Быстрый старт без юриста. Все документы для регистрации и первых сделок"
                  : "Quick start without a lawyer. All documents for registration and first deals",
              },
              {
                icon: "🏦",
                title: language === "ru" ? "Финансы и банки" : "Finance & Banking",
                description: language === "ru"
                  ? "Документы по 152-ФЗ, ГОСТ 57580, требования ЦБ РФ"
                  : "Documents for 152-FZ, GOST 57580, Central Bank requirements",
              },
              {
                icon: "🏥",
                title: language === "ru" ? "Здравоохранение" : "Healthcare",
                description: language === "ru"
                  ? "Согласия на обработку ПДн, медицинская документация"
                  : "Personal data consents, medical documentation",
              },
              {
                icon: "🏭",
                title: language === "ru" ? "Производство" : "Manufacturing",
                description: language === "ru"
                  ? "Договоры поставки, акты, накладные, техническая документация"
                  : "Supply contracts, acts, invoices, technical documentation",
              },
              {
                icon: "💼",
                title: language === "ru" ? "Консалтинг" : "Consulting",
                description: language === "ru"
                  ? "Договоры оказания услуг, NDA, SLA, отчётность"
                  : "Service agreements, NDAs, SLAs, reporting",
              },
              {
                icon: "🛒",
                title: language === "ru" ? "Ритейл и e-commerce" : "Retail & E-commerce",
                description: language === "ru"
                  ? "Оферты, политики возврата, пользовательские соглашения"
                  : "Offers, return policies, user agreements",
              },
            ].map((useCase) => (
              <div
                key={useCase.title}
                className="group relative rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 hover:ring-green-500/50 transition-all"
              >
                <span className="text-4xl mb-4 block">{useCase.icon}</span>
                <h3 className="text-lg font-semibold text-white">{useCase.title}</h3>
                <p className="mt-2 text-sm text-gray-400">{useCase.description}</p>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-green-500/5 to-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Platform Features Section */}
      <div className="relative z-10 py-24 sm:py-32 bg-gradient-to-b from-transparent via-purple-950/20 to-transparent">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-purple-400">
              {language === "ru" ? "Дополнительные возможности" : "Additional Features"}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {language === "ru" ? "Больше чем документы" : "More Than Documents"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {grcModules.map((module) => (
              <div
                key={module.name}
                className="group relative rounded-2xl bg-white/5 p-8 ring-1 ring-white/10 hover:ring-white/20 transition-all"
              >
                <div className={`inline-flex items-center justify-center rounded-xl bg-gradient-to-r ${module.color} p-3 shadow-lg`}>
                  <module.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">{module.name}</h3>
                <p className="mt-2 text-gray-400">{module.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Capabilities Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-cyan-400">
              {t("advancedCapabilities")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("powerfulFeatures")}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {capabilities.map((capability) => (
              <div key={capability.name} className="flex flex-col">
                <div className="flex items-center gap-3 mb-4">
                  <div className="rounded-xl bg-cyan-500/10 p-2 ring-1 ring-cyan-500/20">
                    <capability.icon className="h-5 w-5 text-cyan-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">{capability.name}</h3>
                </div>
                <p className="text-gray-400">{capability.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* International Frameworks */}
      <div className="relative z-10 py-24 sm:py-32 bg-gradient-to-b from-transparent via-slate-900/50 to-transparent">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-blue-400">
              {t("frameworkCoverage")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("preBuiltContent")}
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {internationalFrameworks.map((framework) => (
              <div
                key={framework.name}
                className="group relative rounded-xl bg-white/5 p-5 ring-1 ring-white/10 hover:ring-blue-500/50 transition-all"
              >
                <h3 className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">
                  {framework.name}
                </h3>
                <p className="mt-1 text-xs text-gray-500">{framework.category}</p>
                <p className="mt-2 text-xl font-bold text-blue-400">
                  {framework.controls}
                  <span className="text-xs font-normal text-gray-500 ml-1">{t("controlsLabel")}</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Personas Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-purple-400">
              {t("builtForYourRole")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("tailoredExperiences")}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {personas.map((persona) => (
              <div
                key={persona.title}
                className="rounded-2xl bg-gradient-to-br from-purple-950/50 to-slate-900/50 p-8 ring-1 ring-purple-500/20 hover:ring-purple-500/40 transition-all"
              >
                <h3 className="text-xl font-semibold text-white">{persona.title}</h3>
                <p className="mt-4 text-sm text-gray-400">{persona.description}</p>
                <ul className="mt-6 space-y-3">
                  {persona.benefits.map((benefit) => (
                    <li key={benefit} className="flex gap-3">
                      <CheckCircleIcon className="h-5 w-5 flex-none text-purple-400" />
                      <span className="text-sm text-gray-300">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Enterprise Features */}
      <div className="relative z-10 py-24 sm:py-32 bg-gradient-to-b from-transparent via-slate-900/50 to-transparent">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold text-green-400">
              {t("enterpriseReady")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("securityComplianceBuiltIn")}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: LockClosedIcon,
                title: t("enterpriseSecurity"),
                description: t("enterpriseSecurityDesc"),
                gradient: "from-green-500 to-emerald-500",
              },
              {
                icon: CloudArrowUpIcon,
                title: t("flexibleDeployment"),
                description: t("flexibleDeploymentDesc"),
                gradient: "from-blue-500 to-cyan-500",
              },
              {
                icon: ServerIcon,
                title: t("multiTenantArchitecture"),
                description: t("multiTenantDesc"),
                gradient: "from-purple-500 to-pink-500",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="flex flex-col items-center text-center p-8 rounded-2xl bg-white/5 ring-1 ring-white/10 hover:ring-white/20 transition-all"
              >
                <div className={`rounded-xl bg-gradient-to-r ${feature.gradient} p-4 shadow-lg`}>
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="mt-6 text-lg font-semibold text-white">{feature.title}</h3>
                <p className="mt-2 text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative rounded-3xl overflow-hidden">
            {/* Gradient background */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.2)_0%,transparent_50%)]" />

            <div className="relative px-6 py-24 sm:px-12 sm:py-32 text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                {t("readyToTransform")}
              </h2>
              <p className="mx-auto mt-6 max-w-xl text-lg text-white/80">
                {t("ctaDescription")}
              </p>
              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  to="/login"
                  className="rounded-2xl bg-white px-8 py-4 text-lg font-semibold text-gray-900 shadow-xl hover:bg-gray-100 hover:scale-105 transition-all"
                >
                  {t("startTrial")}
                </Link>
                <a
                  href="mailto:sales@cortex-grc.com"
                  className="rounded-2xl bg-white/10 px-8 py-4 text-lg font-semibold text-white ring-1 ring-white/20 hover:bg-white/20 transition-all flex items-center gap-2"
                >
                  {t("contactSales")}
                  <ArrowRightIcon className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0 flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <DocumentTextIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">
                <span className="text-white">CORTEX</span>
                <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent ml-1">AI</span>
              </span>
            </div>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">{t("privacyPolicy")}</a>
              <a href="#" className="hover:text-white transition-colors">{t("termsOfService")}</a>
              <a href="#" className="hover:text-white transition-colors">{t("securityPage")}</a>
              <a href="mailto:support@cortex-grc.com" className="hover:text-white transition-colors">{t("support")}</a>
            </div>
          </div>
          <div className="border-t border-white/5 mt-8 pt-8">
            <p className="text-sm text-gray-500 text-center">
              &copy; 2025 CORTEX AI. {t("footerCopyright")}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
