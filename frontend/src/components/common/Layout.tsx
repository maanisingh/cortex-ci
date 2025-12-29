import { Fragment, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Dialog, Transition } from "@headlessui/react";
import {
  Bars3Icon,
  HomeIcon,
  BuildingOfficeIcon,
  ShieldExclamationIcon,
  LinkIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  UsersIcon,
  UserCircleIcon,
  // Phase 2 icons
  ArrowsRightLeftIcon,
  ScaleIcon,
  ClockIcon,
  SparklesIcon,
  ChartBarSquareIcon,
  // Phase 2.1 icons
  Square3Stack3DIcon,
  ViewColumnsIcon,
  // Phase 3 icons
  ShieldCheckIcon,
  // Phase 4 icons
  ArrowsUpDownIcon,
  ChartBarIcon,
  // Phase 5 icons
  CpuChipIcon,
  // Compliance icons
  DocumentCheckIcon,
  // GRC icons
  DocumentTextIcon,
  MagnifyingGlassCircleIcon,
  ExclamationCircleIcon,
  TruckIcon,
  FolderOpenIcon,
  ListBulletIcon,
  // Calendar icons
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  // Template icons
  RectangleStackIcon,
  // SME Business icons
  LightBulbIcon,
  BriefcaseIcon,
} from "@heroicons/react/24/outline";
import { useAuthStore } from "../../stores/authStore";
import RealTimeAlerts from "./RealTimeAlerts";
import ThemeToggle from "./ThemeToggle";
import UserGuide from "./UserGuide";
import LanguageSelector from "./LanguageSelector";
import NotificationCenter from "./NotificationCenter";
import OnboardingTour, { useOnboardingTour } from "./OnboardingTour";
import MobileBottomNav from "./MobileBottomNav";
import {
  useKeyboardShortcuts,
  KeyboardShortcutsHelp,
} from "../../hooks/useKeyboardShortcuts";
import { useLanguage } from "../../contexts/LanguageContext";

// Core Navigation - GRC Overview
const coreNavigation = [
  { name: "grcDashboard", href: "/dashboard", icon: HomeIcon },
];

// Governance Module - included in compliance section

// Risk Management Module
const riskNavigation = [
  { name: "riskRegister", href: "/risks", icon: ExclamationTriangleIcon },
  { name: "riskObjects", href: "/entities", icon: BuildingOfficeIcon },
  { name: "riskRelationships", href: "/dependencies", icon: LinkIcon },
  { name: "riskScenarios", href: "/scenarios", icon: BeakerIcon },
  { name: "riskLayers", href: "/dependency-layers", icon: Square3Stack3DIcon },
  {
    name: "crossLayerAnalysis",
    href: "/cross-layer-analysis",
    icon: ViewColumnsIcon,
  },
  {
    name: "scenarioChains",
    href: "/scenario-chains",
    icon: ArrowsRightLeftIcon,
  },
  { name: "riskJustification", href: "/risk-justification", icon: ScaleIcon },
  { name: "simulations", href: "/simulations", icon: CpuChipIcon },
];

// Compliance Module
const complianceNavigation = [
  {
    name: "complianceDashboard",
    href: "/compliance",
    icon: DocumentCheckIcon,
  },
  { name: "controlsNav", href: "/constraints", icon: ShieldExclamationIcon },
  { name: "policies", href: "/policies", icon: DocumentTextIcon },
  { name: "documentLibrary", href: "/documents", icon: FolderOpenIcon },
  { name: "templateCatalog", href: "/templates", icon: RectangleStackIcon },
  { name: "russianCompliance", href: "/russian-compliance", icon: ShieldCheckIcon },
  { name: "complianceTasks", href: "/compliance-tasks", icon: ClipboardDocumentCheckIcon },
  { name: "complianceCalendar", href: "/compliance-calendar", icon: CalendarDaysIcon },
];

// SME Business Templates
const smeNavigation = [
  { name: "companyLifecycle", href: "/company-lifecycle", icon: LightBulbIcon },
  { name: "smeTemplates", href: "/sme-templates", icon: BriefcaseIcon },
];

// Audit & Issue Management
const auditNavigation = [
  { name: "auditPlanning", href: "/audits", icon: MagnifyingGlassCircleIcon },
  { name: "gapAnalysis", href: "/gap-analysis", icon: DocumentCheckIcon },
  { name: "findings", href: "/findings", icon: ListBulletIcon },
  { name: "incidents", href: "/incidents", icon: ExclamationCircleIcon },
  { name: "activityLog", href: "/audit", icon: ClipboardDocumentListIcon },
];

// Third Party Risk & Evidence
const vendorNavigation = [
  { name: "vendorRegister", href: "/vendors", icon: TruckIcon },
  { name: "evidenceLibrary", href: "/evidence", icon: FolderOpenIcon },
];

// Intelligence & Analytics
const intelligenceNavigation = [
  { name: "historicalAnalysis", href: "/history", icon: ClockIcon },
  { name: "aiInsights", href: "/ai-analysis", icon: SparklesIcon },
  { name: "monitoring", href: "/monitoring", icon: ChartBarSquareIcon },
];

// Admin
const adminNavigation = [
  { name: "userManagement", href: "/admin/users", icon: UsersIcon },
  { name: "analyticsReports", href: "/analytics", icon: ChartBarIcon },
  { name: "bulkOperations", href: "/bulk-operations", icon: ArrowsUpDownIcon },
  { name: "settings", href: "/settings", icon: Cog6ToothIcon },
];

const userNavigation = [
  { name: "profile", href: "/profile", icon: UserCircleIcon },
  { name: "security", href: "/security", icon: ShieldCheckIcon },
];

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(" ");
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { t } = useLanguage();

  // Onboarding tour
  const { showTour, endTour } = useOnboardingTour();

  // Enable keyboard shortcuts
  useKeyboardShortcuts(() => setShowShortcuts(true));

  return (
    <div>
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-50 lg:hidden"
          onClose={setSidebarOpen}
        >
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-900/80" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-primary-900 px-6 pb-4">
                  <div className="flex h-16 shrink-0 items-center">
                    <span className="text-2xl font-bold text-white">
                      CORTEX <span className="text-primary-300">GRC</span>
                    </span>
                  </div>
                  <nav className="flex flex-1 flex-col">
                    <ul role="list" className="flex flex-1 flex-col gap-y-7">
                      {/* Core Navigation */}
                      <li>
                        <ul role="list" className="-mx-2 space-y-1">
                          {coreNavigation.map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href
                                    ? "bg-primary-800 text-white"
                                    : "text-primary-200 hover:text-white hover:bg-primary-800",
                                  "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                                )}
                                onClick={() => setSidebarOpen(false)}
                              >
                                <item.icon
                                  className="h-6 w-6 shrink-0"
                                  aria-hidden="true"
                                />
                                {t(item.name as any)}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                      {/* Risk Management */}
                      <li>
                        <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                          {t("riskManagement")}
                        </div>
                        <ul role="list" className="-mx-2 mt-2 space-y-1">
                          {riskNavigation.slice(0, 4).map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href ||
                                    location.pathname.startsWith(
                                      item.href + "/",
                                    )
                                    ? "bg-primary-800 text-white"
                                    : "text-primary-200 hover:text-white hover:bg-primary-800",
                                  "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                                )}
                                onClick={() => setSidebarOpen(false)}
                              >
                                <item.icon
                                  className="h-6 w-6 shrink-0"
                                  aria-hidden="true"
                                />
                                {t(item.name as any)}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                      {/* Compliance */}
                      <li>
                        <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                          {t("complianceSection")}
                        </div>
                        <ul role="list" className="-mx-2 mt-2 space-y-1">
                          {complianceNavigation.map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href ||
                                    location.pathname.startsWith(
                                      item.href + "/",
                                    )
                                    ? "bg-primary-800 text-white"
                                    : "text-primary-200 hover:text-white hover:bg-primary-800",
                                  "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                                )}
                                onClick={() => setSidebarOpen(false)}
                              >
                                <item.icon
                                  className="h-6 w-6 shrink-0"
                                  aria-hidden="true"
                                />
                                {t(item.name as any)}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                      {/* Mobile User Section */}
                      <li className="mt-auto">
                        <ul role="list" className="-mx-2 space-y-1 mb-4">
                          {userNavigation.map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href
                                    ? "bg-primary-800 text-white"
                                    : "text-primary-200 hover:text-white hover:bg-primary-800",
                                  "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                                )}
                                onClick={() => setSidebarOpen(false)}
                              >
                                <item.icon
                                  className="h-6 w-6 shrink-0"
                                  aria-hidden="true"
                                />
                                {t(item.name as any)}
                              </Link>
                            </li>
                          ))}
                        </ul>
                        <div className="text-primary-200 text-sm mb-2 border-t border-primary-700 pt-4">
                          {user?.full_name}
                          <span className="text-primary-400 block text-xs">
                            {user?.email}
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            logout();
                            setSidebarOpen(false);
                          }}
                          className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-primary-200 hover:bg-primary-800 hover:text-white w-full"
                        >
                          {t("signOut")}
                        </button>
                      </li>
                    </ul>
                  </nav>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-primary-900 px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
            <span className="text-2xl font-bold text-white">
              CORTEX <span className="text-primary-300">GRC</span>
            </span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-5">
              {/* Core Navigation */}
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {coreNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname === "/"
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Risk Management */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("riskManagement")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {riskNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Compliance */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("complianceSection")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {complianceNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* SME Business */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("smeBusiness")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {smeNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Audit */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("audit")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {auditNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Third Party & Evidence */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("thirdParty")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {vendorNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Intelligence */}
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                  {t("intelligence")}
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {intelligenceNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href ||
                            location.pathname.startsWith(item.href + "/")
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* Admin */}
              {user?.role?.toUpperCase() === "ADMIN" && (
                <li>
                  <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">
                    {t("administration")}
                  </div>
                  <ul role="list" className="-mx-2 mt-2 space-y-1">
                    {adminNavigation.map((item) => (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={classNames(
                            location.pathname === item.href ||
                              location.pathname.startsWith(item.href + "/")
                              ? "bg-primary-800 text-white"
                              : "text-primary-200 hover:text-white hover:bg-primary-800",
                            "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                          )}
                        >
                          <item.icon
                            className="h-6 w-6 shrink-0"
                            aria-hidden="true"
                          />
                          {t(item.name as any)}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              )}
              <li className="mt-auto">
                <ul role="list" className="-mx-2 space-y-1 mb-4">
                  {userNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? "bg-primary-800 text-white"
                            : "text-primary-200 hover:text-white hover:bg-primary-800",
                          "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold",
                        )}
                      >
                        <item.icon
                          className="h-6 w-6 shrink-0"
                          aria-hidden="true"
                        />
                        {t(item.name as any)}
                      </Link>
                    </li>
                  ))}
                </ul>
                <div className="text-primary-200 text-sm mb-2 border-t border-primary-700 pt-4">
                  {user?.full_name}
                  <span className="text-primary-400 block text-xs">
                    {user?.email}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-primary-200 hover:bg-primary-800 hover:text-white w-full"
                >
                  {t("signOut")}
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      <div className="lg:pl-72">
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white dark:bg-dark-800 dark:border-dark-700 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8 transition-colors">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 dark:text-gray-300 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex items-center gap-x-4 lg:gap-x-6 ml-auto">
              {/* Language Selector */}
              <LanguageSelector variant="light" />
              {/* Theme Toggle */}
              <ThemeToggle />
              {/* Real-time Alerts */}
              <RealTimeAlerts />
              {/* Notification Center - Due Date Reminders */}
              <NotificationCenter />
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Role:{" "}
                <span className="font-medium text-gray-900 dark:text-gray-200 capitalize">
                  {user?.role}
                </span>
              </span>
            </div>
          </div>
        </div>

        <main className="py-10 pb-24 lg:pb-10 bg-gray-50 dark:bg-dark-900 min-h-screen transition-colors">
          <div className="px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav onMenuClick={() => setSidebarOpen(true)} />

      {/* User Guide / Help System */}
      <UserGuide />

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />

      {/* Onboarding Tour */}
      <OnboardingTour isOpen={showTour} onClose={endTour} />
    </div>
  );
}
