import { Link } from "react-router-dom";
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

export default function LandingPage() {
  const { t, language, setLanguage } = useLanguage();

  const grcModules = [
    {
      name: t("governance"),
      description: t("governanceDesc"),
      icon: DocumentTextIcon,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      name: t("riskManagementModule"),
      description: t("riskManagementDesc"),
      icon: ExclamationTriangleIcon,
      color: "text-red-600",
      bgColor: "bg-red-50",
    },
    {
      name: t("complianceModule"),
      description: t("complianceModuleDesc"),
      icon: DocumentCheckIcon,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      name: t("auditManagement"),
      description: t("auditManagementDesc"),
      icon: MagnifyingGlassCircleIcon,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      name: t("incidentResponse"),
      description: t("incidentResponseDesc"),
      icon: ShieldCheckIcon,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      name: t("thirdPartyRisk"),
      description: t("thirdPartyRiskDesc"),
      icon: UserGroupIcon,
      color: "text-amber-600",
      bgColor: "bg-amber-50",
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

  const stats = [
    { id: 1, name: t("complianceFrameworks"), value: "13+" },
    { id: 2, name: t("securityControls"), value: "2,390+" },
    { id: 3, name: t("riskFactorsAnalyzed"), value: "50+" },
    { id: 4, name: t("enterprisesTrustUs"), value: "100+" },
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
    <div className="bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100">
        <nav className="flex items-center justify-between p-6 lg:px-8 max-w-7xl mx-auto">
          <div className="flex lg:flex-1">
            <span className="text-2xl font-bold">
              <span className="text-primary-900">CORTEX</span>
              <span className="text-primary-600 ml-1">GRC</span>
            </span>
          </div>
          <div className="flex items-center gap-x-6">
            {/* Language Selector */}
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as LanguageCode)}
              className="text-sm border border-gray-200 rounded-md px-2 py-1 bg-white hover:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {Object.entries(LANGUAGES).map(([code, { nativeName, flag }]) => (
                <option key={code} value={code}>
                  {flag} {nativeName}
                </option>
              ))}
            </select>
            <Link
              to="/login"
              className="text-sm font-semibold leading-6 text-gray-900 hover:text-primary-600"
            >
              {t("signIn")}
            </Link>
            <Link
              to="/login"
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
            >
              {t("getStarted")}
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <div className="relative isolate pt-14">
        <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
          <div
            className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-primary-600 to-cyan-400 opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                "polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)",
            }}
          />
        </div>

        <div className="py-24 sm:py-32 lg:pb-40">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <div className="mb-8 flex justify-center">
                <div className="rounded-full px-4 py-1.5 text-sm font-medium text-primary-700 ring-1 ring-primary-600/20 bg-primary-50">
                  {t("integratedGrcPlatform")}
                </div>
              </div>
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                {t("unifiedGrc")}{" "}
                <span className="text-primary-600">
                  {t("governanceRiskCompliance")}
                </span>{" "}
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-600">
                {t("heroDescription")}
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link
                  to="/login"
                  className="rounded-md bg-primary-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                >
                  {t("startTrial")}
                </Link>
                <a
                  href="#modules"
                  className="text-base font-semibold leading-6 text-gray-900"
                >
                  {t("exploreModules")} <span aria-hidden="true">→</span>
                </a>
              </div>
            </div>

            {/* Stats */}
            <div className="mx-auto mt-16 max-w-7xl px-6 lg:px-8">
              <dl className="grid grid-cols-2 gap-x-8 gap-y-16 text-center lg:grid-cols-4">
                {stats.map((stat) => (
                  <div
                    key={stat.id}
                    className="mx-auto flex max-w-xs flex-col gap-y-4"
                  >
                    <dt className="text-base leading-7 text-gray-600">
                      {stat.name}
                    </dt>
                    <dd className="order-first text-3xl font-semibold tracking-tight text-primary-600 sm:text-5xl">
                      {stat.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* GRC Modules Section */}
      <div id="modules" className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              {t("completeGrcSuite")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              {t("sixIntegratedModules")}
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              {t("modulesDescription")}
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-6 lg:max-w-none lg:grid-cols-3">
              {grcModules.map((module) => (
                <div
                  key={module.name}
                  className="relative rounded-2xl bg-white p-8 shadow-sm ring-1 ring-gray-200 hover:shadow-md transition-shadow"
                >
                  <div
                    className={`inline-flex items-center justify-center rounded-lg ${module.bgColor} p-3`}
                  >
                    <module.icon
                      className={`h-6 w-6 ${module.color}`}
                      aria-hidden="true"
                    />
                  </div>
                  <dt className="mt-4 text-lg font-semibold leading-7 text-gray-900">
                    {module.name}
                  </dt>
                  <dd className="mt-2 text-base leading-7 text-gray-600">
                    {module.description}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Capabilities Section */}
      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              {t("advancedCapabilities")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              {t("powerfulFeatures")}
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3">
              {capabilities.map((capability) => (
                <div key={capability.name} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                    <capability.icon
                      className="h-5 w-5 flex-none text-primary-600"
                      aria-hidden="true"
                    />
                    {capability.name}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                    <p className="flex-auto">{capability.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Russian SME Section */}
      <div className="bg-gradient-to-b from-red-50 to-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <div className="flex justify-center items-center gap-2 mb-4">
              <span className="text-4xl">🇷🇺</span>
              <h2 className="text-base font-semibold leading-7 text-red-600">
                {language === "ru" ? "Специально для российского бизнеса" : "Built for Russian Business"}
              </h2>
            </div>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              {language === "ru" ? "Полное соответствие российскому законодательству" : "Complete Russian Regulatory Compliance"}
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              {language === "ru"
                ? "285+ готовых шаблонов документов для всех этапов жизненного цикла компании. Введите ИНН — получите все документы."
                : "285+ ready-to-use document templates for every stage of your company lifecycle. Enter your INN — get all documents."}
            </p>
          </div>

          {/* Russian Frameworks */}
          <div className="mx-auto mt-12 max-w-4xl">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              {russianFrameworks.map((framework) => (
                <div
                  key={framework.name}
                  className="relative rounded-xl border-2 border-red-200 bg-white p-5 hover:border-red-500 hover:shadow-md transition-all"
                >
                  <h3 className="text-lg font-bold text-red-700">
                    {framework.name}
                  </h3>
                  <p className="mt-1 text-xs text-gray-600">
                    {framework.category}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    {framework.description}
                  </p>
                  <p className="mt-2 text-xl font-bold text-red-600">
                    {framework.controls}
                    <span className="text-xs font-normal text-gray-500 ml-1">
                      {language === "ru" ? "требований" : "requirements"}
                    </span>
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* SME Value Props */}
          <div className="mx-auto mt-16 max-w-5xl">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div className="text-center p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-all">
                <div className="text-4xl font-bold text-red-600">285+</div>
                <div className="mt-2 text-sm text-gray-600">
                  {language === "ru" ? "Шаблонов документов" : "Document Templates"}
                </div>
              </div>
              <div className="text-center p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-all">
                <div className="text-4xl font-bold text-red-600">8</div>
                <div className="mt-2 text-sm text-gray-600">
                  {language === "ru" ? "Этапов жизненного цикла" : "Lifecycle Stages"}
                </div>
              </div>
              <div className="text-center p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-all">
                <div className="text-4xl font-bold text-red-600">30</div>
                <div className="mt-2 text-sm text-gray-600">
                  {language === "ru" ? "Дней до полного соответствия" : "Days to Full Compliance"}
                </div>
              </div>
              <div className="text-center p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-all">
                <div className="text-4xl font-bold text-red-600">6</div>
                <div className="mt-2 text-sm text-gray-600">
                  {language === "ru" ? "Российских стандартов" : "Russian Standards"}
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <Link
              to="/login"
              className="rounded-md bg-red-600 px-8 py-4 text-lg font-semibold text-white shadow-lg hover:bg-red-500 transition-all"
            >
              {language === "ru" ? "Начать бесплатно →" : "Start Free →"}
            </Link>
            <p className="mt-4 text-sm text-gray-500">
              {language === "ru"
                ? "Бесплатный тариф для МСП. Без банковской карты."
                : "Free tier for SMEs. No credit card required."}
            </p>
          </div>
        </div>
      </div>

      {/* International Frameworks Section */}
      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              {t("frameworkCoverage")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              {t("preBuiltContent")}
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              {t("frameworksDescription")}
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl lg:max-w-none">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {internationalFrameworks.map((framework) => (
                <div
                  key={framework.name}
                  className="relative rounded-xl border border-gray-200 bg-white p-5 hover:border-primary-500 hover:shadow-sm transition-all"
                >
                  <h3 className="text-sm font-semibold text-gray-900">
                    {framework.name}
                  </h3>
                  <p className="mt-1 text-xs text-gray-500">
                    {framework.category}
                  </p>
                  <p className="mt-2 text-xl font-bold text-primary-600">
                    {framework.controls}
                    <span className="text-xs font-normal text-gray-500 ml-1">
                      {t("controlsLabel")}
                    </span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Personas Section */}
      <div className="bg-primary-900 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-300">
              {t("builtForYourRole")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("tailoredExperiences")}
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl lg:max-w-none">
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
              {personas.map((persona) => (
                <div
                  key={persona.title}
                  className="rounded-2xl bg-white/5 p-8 ring-1 ring-white/10 hover:bg-white/10 transition-colors"
                >
                  <h3 className="text-xl font-semibold text-white">
                    {persona.title}
                  </h3>
                  <p className="mt-4 text-sm text-gray-300">
                    {persona.description}
                  </p>
                  <ul className="mt-6 space-y-3">
                    {persona.benefits.map((benefit) => (
                      <li key={benefit} className="flex gap-x-3">
                        <CheckCircleIcon className="h-5 w-5 flex-none text-primary-400" />
                        <span className="text-sm text-gray-300">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Trust Section */}
      <div className="bg-white py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              {t("enterpriseReady")}
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              {t("securityComplianceBuiltIn")}
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl lg:max-w-none">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gray-50">
                <LockClosedIcon className="h-12 w-12 text-primary-600" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {t("enterpriseSecurity")}
                </h3>
                <p className="mt-2 text-gray-600">
                  {t("enterpriseSecurityDesc")}
                </p>
              </div>
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gray-50">
                <BuildingOfficeIcon className="h-12 w-12 text-primary-600" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {t("flexibleDeployment")}
                </h3>
                <p className="mt-2 text-gray-600">
                  {t("flexibleDeploymentDesc")}
                </p>
              </div>
              <div className="flex flex-col items-center text-center p-6 rounded-xl bg-gray-50">
                <ScaleIcon className="h-12 w-12 text-primary-600" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {t("multiTenantArchitecture")}
                </h3>
                <p className="mt-2 text-gray-600">
                  {t("multiTenantDesc")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600">
        <div className="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {t("readyToTransform")}
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-primary-100">
              {t("ctaDescription")}
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/login"
                className="rounded-md bg-white px-6 py-3 text-base font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                {t("startTrial")}
              </Link>
              <a
                href="mailto:sales@cortex-grc.com"
                className="text-base font-semibold leading-6 text-white"
              >
                {t("contactSales")} <ArrowRightIcon className="inline h-4 w-4 ml-1" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <span className="text-xl font-bold">
                <span className="text-white">CORTEX</span>
                <span className="text-primary-400 ml-1">GRC</span>
              </span>
            </div>
            <div className="flex gap-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white">
                {t("privacyPolicy")}
              </a>
              <a href="#" className="hover:text-white">
                {t("termsOfService")}
              </a>
              <a href="#" className="hover:text-white">
                {t("securityPage")}
              </a>
              <a
                href="mailto:support@cortex-grc.com"
                className="hover:text-white"
              >
                {t("support")}
              </a>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8">
            <p className="text-sm text-gray-400 text-center">
              &copy; 2025 CORTEX GRC. {t("footerCopyright")}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
