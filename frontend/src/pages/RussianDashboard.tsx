import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
import {
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  UserGroupIcon,
  ServerStackIcon,
  ChevronRightIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  DocumentDuplicateIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolidIcon } from "@heroicons/react/24/solid";
import { exportToPDF } from "../utils/pdfExport";
import { russianComplianceApi } from "../services/api";

interface ComplianceScore {
  framework: string;
  frameworkName: string;
  score: number;
  total: number;
  completed: number;
  inProgress: number;
  pending: number;
  overdue: number;
}

interface RecentActivity {
  id: string;
  type: "document" | "task" | "ispdn" | "training";
  action: string;
  title: string;
  user: string;
  timestamp: string;
}

interface UpcomingDeadline {
  id: string;
  title: string;
  type: string;
  dueDate: string;
  priority: "low" | "medium" | "high" | "critical";
  assignee: string;
}

interface Company {
  id: string;
  name: string;
  inn: string;
  ispdnCount?: number;
  employeeCount?: number;
  documentsTotal?: number;
  documentsApproved?: number;
  tasksTotal?: number;
  tasksCompleted?: number;
  overallScore?: number;
}

interface DashboardData {
  companyData: {
    id: string;
    name: string;
    inn: string;
    ispdnCount: number;
    employeeCount: number;
    documentsTotal: number;
    documentsApproved: number;
    tasksTotal: number;
    tasksCompleted: number;
    overallScore: number;
  };
  complianceScores: ComplianceScore[];
  recentActivities: RecentActivity[];
  upcomingDeadlines: UpcomingDeadline[];
  checklist?: Array<{ title: string; completed: boolean }>;
}

export default function RussianDashboard() {
  const { language } = useLanguage();
  const [selectedCompany, setSelectedCompany] = useState<string>("");

  // Bilingual text
  const t = {
    title: language === "ru" ? "Панель соответствия — Российское законодательство" : "Compliance Dashboard — Russian Regulations",
    subtitle: language === "ru" ? "Мониторинг соответствия 152-ФЗ, 187-ФЗ, ГОСТ Р 57580, ФСТЭК" : "Compliance monitoring: 152-FZ, 187-FZ, GOST R 57580, FSTEC",
    exportPdf: language === "ru" ? "Экспорт PDF" : "Export PDF",
    addCompany: language === "ru" ? "Добавить организацию" : "Add Company",
    documents: language === "ru" ? "Документы" : "Documents",
    inn: language === "ru" ? "ИНН" : "INN",
    overallCompliance: language === "ru" ? "Общий уровень соответствия" : "Overall Compliance",
    ispdn: language === "ru" ? "ИСПДн" : "ISPDn",
    employees: language === "ru" ? "Сотрудников" : "Employees",
    tasks: language === "ru" ? "Задач" : "Tasks",
    completed: language === "ru" ? "Выполнено" : "Completed",
    inProgress: language === "ru" ? "В работе" : "In Progress",
    pending: language === "ru" ? "Ожидает" : "Pending",
    overdue: language === "ru" ? "Просрочено" : "Overdue",
    moreDetails: language === "ru" ? "Подробнее о требованиях" : "View Requirements",
    recentActivity: language === "ru" ? "Последние действия" : "Recent Activity",
    showAll: language === "ru" ? "Показать все" : "Show All",
    upcomingDeadlines: language === "ru" ? "Ближайшие сроки" : "Upcoming Deadlines",
    allTasks: language === "ru" ? "Все задачи" : "All Tasks",
    assignee: language === "ru" ? "Исполнитель" : "Assignee",
    daysAgo: language === "ru" ? "дн. назад" : "days ago",
    quickActions: language === "ru" ? "Быстрые действия" : "Quick Actions",
    newCompany: language === "ru" ? "Новая организация" : "New Company",
    fullCycle: language === "ru" ? "Полный цикл регистрации" : "Full registration cycle",
    generateDocs: language === "ru" ? "Генерация документов" : "Generate Documents",
    docPackage: language === "ru" ? "Пакет 152-ФЗ" : "152-FZ Package",
    taskManagement: language === "ru" ? "Управление задачами" : "Task Management",
    kanban: language === "ru" ? "Kanban-доска" : "Kanban Board",
    runAudit: language === "ru" ? "Провести аудит" : "Run Audit",
    selfCheck: language === "ru" ? "Самопроверка" : "Self-Check",
    checklist: language === "ru" ? "Чек-лист соответствия 152-ФЗ" : "152-FZ Compliance Checklist",
    outOf: language === "ru" ? "из" : "of",
    done: language === "ru" ? "выполнено" : "completed",
    critical: language === "ru" ? "Критично" : "Critical",
    high: language === "ru" ? "Высокий" : "High",
    medium: language === "ru" ? "Средний" : "Medium",
    low: language === "ru" ? "Низкий" : "Low",
    loading: language === "ru" ? "Загрузка..." : "Loading...",
    error: language === "ru" ? "Ошибка загрузки данных" : "Error loading data",
    retry: language === "ru" ? "Повторить" : "Retry",
    noCompanies: language === "ru" ? "Нет зарегистрированных организаций" : "No registered companies",
    selectCompany: language === "ru" ? "Выберите организацию" : "Select a company",
  };

  // Fetch companies list
  const {
    data: companiesData,
    isLoading: isLoadingCompanies,
    error: companiesError,
    refetch: refetchCompanies,
  } = useQuery({
    queryKey: ["russian-companies"],
    queryFn: async () => {
      const response = await russianComplianceApi.companies.list();
      return response.data as Company[];
    },
  });

  // Set first company as selected when companies load
  useEffect(() => {
    if (companiesData && companiesData.length > 0 && !selectedCompany) {
      setSelectedCompany(companiesData[0].id);
    }
  }, [companiesData, selectedCompany]);

  // Fetch dashboard data for selected company
  const {
    data: dashboardData,
    isLoading: isLoadingDashboard,
    error: dashboardError,
    refetch: refetchDashboard,
  } = useQuery({
    queryKey: ["russian-dashboard", selectedCompany],
    queryFn: async () => {
      const response = await russianComplianceApi.dashboard(selectedCompany);
      return response.data as DashboardData;
    },
    enabled: !!selectedCompany,
  });

  // Extract data from dashboard response
  const companyData = dashboardData?.companyData || {
    id: "",
    name: "",
    inn: "",
    ispdnCount: 0,
    employeeCount: 0,
    documentsTotal: 0,
    documentsApproved: 0,
    tasksTotal: 0,
    tasksCompleted: 0,
    overallScore: 0,
  };

  const complianceScores: ComplianceScore[] = dashboardData?.complianceScores || [];
  const recentActivities: RecentActivity[] = dashboardData?.recentActivities || [];
  const upcomingDeadlines: UpcomingDeadline[] = dashboardData?.upcomingDeadlines || [];
  const checklist = dashboardData?.checklist || [];

  const priorityColors = {
    low: "text-gray-500",
    medium: "text-yellow-600",
    high: "text-orange-600",
    critical: "text-red-600",
  };

  const getDaysUntil = (date: string) => {
    const due = new Date(date);
    const now = new Date();
    return Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    if (score >= 40) return "text-orange-600";
    return "text-red-600";
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  // Handle PDF export
  const handleExportPDF = () => {
    exportToPDF({
      companyName: companyData.name,
      companyInn: companyData.inn,
      generatedAt: new Date(),
      overallScore: companyData.overallScore,
      frameworks: complianceScores.map((fw) => ({
        name: fw.frameworkName,
        score: fw.score,
        completed: fw.completed,
        total: fw.total,
      })),
      documentStats: {
        total: companyData.documentsTotal,
        approved: companyData.documentsApproved,
        draft: companyData.documentsTotal - companyData.documentsApproved,
        expired: 0,
      },
      taskStats: {
        total: companyData.tasksTotal,
        completed: companyData.tasksCompleted,
        inProgress: companyData.tasksTotal - companyData.tasksCompleted - 1,
        overdue: 1,
      },
      auditReadiness: {
        score: 78,
        categories: [
          { name: language === "ru" ? "Документация" : "Documentation", score: 85 },
          { name: language === "ru" ? "Технические меры" : "Technical Controls", score: 72 },
          { name: language === "ru" ? "Организационные меры" : "Organizational Controls", score: 90 },
          { name: language === "ru" ? "Обучение персонала" : "Staff Training", score: 65 },
        ],
      },
      risks: [],
    });
  };

  // Loading state
  if (isLoadingCompanies) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">{t.loading}</p>
        </div>
      </div>
    );
  }

  // Error state for companies
  if (companiesError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-4 text-gray-900 font-medium">{t.error}</p>
          <p className="mt-2 text-sm text-gray-500">
            {companiesError instanceof Error ? companiesError.message : String(companiesError)}
          </p>
          <button
            onClick={() => refetchCompanies()}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            {t.retry}
          </button>
        </div>
      </div>
    );
  }

  // No companies state
  if (!companiesData || companiesData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <BuildingOfficeIcon className="h-12 w-12 text-gray-400 mx-auto" />
          <p className="mt-4 text-gray-900 font-medium">{t.noCompanies}</p>
          <Link
            to="/russian-onboarding"
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <BuildingOfficeIcon className="h-4 w-4 mr-2" />
            {t.addCompany}
          </Link>
        </div>
      </div>
    );
  }

  // Dashboard loading state
  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
            <p className="mt-1 text-sm text-gray-500">{t.subtitle}</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <ArrowPathIcon className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
            <p className="mt-4 text-gray-600">{t.loading}</p>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard error state
  if (dashboardError) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
            <p className="mt-1 text-sm text-gray-500">{t.subtitle}</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
            <p className="mt-4 text-gray-900 font-medium">{t.error}</p>
            <p className="mt-2 text-sm text-gray-500">
              {dashboardError instanceof Error ? dashboardError.message : String(dashboardError)}
            </p>
            <button
              onClick={() => refetchDashboard()}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              {t.retry}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t.title}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {t.subtitle}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {/* Company selector */}
          {companiesData && companiesData.length > 1 && (
            <select
              value={selectedCompany}
              onChange={(e) => setSelectedCompany(e.target.value)}
              className="block w-48 px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
            >
              {companiesData.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          )}
          <button
            onClick={handleExportPDF}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            {t.exportPdf}
          </button>
          <Link
            to="/russian-onboarding"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <BuildingOfficeIcon className="h-5 w-5 mr-2" />
            {t.addCompany}
          </Link>
          <Link
            to="/russian-compliance"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <DocumentDuplicateIcon className="h-5 w-5 mr-2" />
            {t.documents}
          </Link>
        </div>
      </div>

      {/* Company overview card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold">{companyData.name}</h2>
            <p className="text-blue-100">{t.inn}: {companyData.inn}</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{companyData.overallScore}%</div>
            <div className="text-blue-100">{t.overallCompliance}</div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <ServerStackIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{companyData.ispdnCount}</div>
                <div className="text-sm text-blue-200">{t.ispdn}</div>
              </div>
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <UserGroupIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{companyData.employeeCount}</div>
                <div className="text-sm text-blue-200">{t.employees}</div>
              </div>
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <DocumentTextIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">
                  {companyData.documentsApproved}/{companyData.documentsTotal}
                </div>
                <div className="text-sm text-blue-200">{t.documents}</div>
              </div>
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">
                  {companyData.tasksCompleted}/{companyData.tasksTotal}
                </div>
                <div className="text-sm text-blue-200">{t.tasks}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance scores by framework */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {complianceScores.map((framework) => (
          <div key={framework.framework} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">{framework.frameworkName}</h3>
                <div className="mt-2 flex items-center">
                  <div className={`text-3xl font-bold ${getScoreColor(framework.score)}`}>
                    {framework.score}%
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getProgressColor(framework.score)} transition-all duration-500`}
                        style={{ width: `${framework.score}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <ShieldCheckIcon
                className={`h-12 w-12 ${getScoreColor(framework.score)} opacity-50`}
              />
            </div>

            <div className="mt-4 grid grid-cols-4 gap-2 text-center">
              <div className="bg-green-50 rounded-lg p-2">
                <div className="text-lg font-bold text-green-700">{framework.completed}</div>
                <div className="text-xs text-green-600">{t.completed}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-lg font-bold text-blue-700">{framework.inProgress}</div>
                <div className="text-xs text-blue-600">{t.inProgress}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-2">
                <div className="text-lg font-bold text-gray-700">{framework.pending}</div>
                <div className="text-xs text-gray-600">{t.pending}</div>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <div className="text-lg font-bold text-red-700">{framework.overdue}</div>
                <div className="text-xs text-red-600">{t.overdue}</div>
              </div>
            </div>

            <div className="mt-4">
              <Link
                to={`/russian-compliance?framework=${framework.framework}`}
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
              >
                {t.moreDetails}
                <ChevronRightIcon className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        ))}
      </div>

      {/* Two columns: Recent activity and Upcoming deadlines */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent activity */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">{t.recentActivity}</h3>
            <button className="text-sm text-blue-600 hover:text-blue-700">{t.showAll}</button>
          </div>
          <div className="divide-y">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start">
                  <div
                    className={`p-2 rounded-full ${
                      activity.type === "document"
                        ? "bg-blue-100 text-blue-600"
                        : activity.type === "task"
                        ? "bg-green-100 text-green-600"
                        : activity.type === "ispdn"
                        ? "bg-purple-100 text-purple-600"
                        : "bg-yellow-100 text-yellow-600"
                    }`}
                  >
                    {activity.type === "document" && <DocumentTextIcon className="h-5 w-5" />}
                    {activity.type === "task" && <CheckCircleSolidIcon className="h-5 w-5" />}
                    {activity.type === "ispdn" && <ServerStackIcon className="h-5 w-5" />}
                    {activity.type === "training" && <UserGroupIcon className="h-5 w-5" />}
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="text-sm text-gray-500">{activity.action}</p>
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {activity.user} •{" "}
                      {new Date(activity.timestamp).toLocaleString("ru-RU", {
                        day: "numeric",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming deadlines */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">{t.upcomingDeadlines}</h3>
            <Link to="/compliance-tasks" className="text-sm text-blue-600 hover:text-blue-700">
              {t.allTasks}
            </Link>
          </div>
          <div className="divide-y">
            {upcomingDeadlines.map((deadline) => {
              const daysUntil = getDaysUntil(deadline.dueDate);
              return (
                <div key={deadline.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            deadline.priority === "critical"
                              ? "bg-red-100 text-red-800"
                              : deadline.priority === "high"
                              ? "bg-orange-100 text-orange-800"
                              : deadline.priority === "medium"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {deadline.type}
                        </span>
                        <span className={`ml-2 text-xs ${priorityColors[deadline.priority]}`}>
                          {deadline.priority === "critical" && t.critical}
                          {deadline.priority === "high" && t.high}
                          {deadline.priority === "medium" && t.medium}
                          {deadline.priority === "low" && t.low}
                        </span>
                      </div>
                      <p className="mt-1 text-sm font-medium text-gray-900">{deadline.title}</p>
                      <p className="text-xs text-gray-500">{t.assignee}: {deadline.assignee}</p>
                    </div>
                    <div className="text-right">
                      <div
                        className={`text-sm font-medium ${
                          daysUntil <= 3
                            ? "text-red-600"
                            : daysUntil <= 7
                            ? "text-orange-600"
                            : "text-gray-600"
                        }`}
                      >
                        {daysUntil === 0
                          ? (language === "ru" ? "Сегодня" : "Today")
                          : daysUntil === 1
                          ? (language === "ru" ? "Завтра" : "Tomorrow")
                          : daysUntil < 0
                          ? `${Math.abs(daysUntil)} ${t.daysAgo}`
                          : `${daysUntil} ${language === "ru" ? "дн." : "days"}`}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(deadline.dueDate).toLocaleDateString("ru-RU")}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">{t.quickActions}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/russian-onboarding"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <BuildingOfficeIcon className="h-8 w-8 text-blue-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">{t.newCompany}</span>
            <span className="text-xs text-gray-500">{t.fullCycle}</span>
          </Link>
          <Link
            to="/russian-compliance"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <DocumentDuplicateIcon className="h-8 w-8 text-green-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">{t.generateDocs}</span>
            <span className="text-xs text-gray-500">{t.docPackage}</span>
          </Link>
          <Link
            to="/compliance-tasks"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <ClockIcon className="h-8 w-8 text-orange-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">{t.taskManagement}</span>
            <span className="text-xs text-gray-500">{t.kanban}</span>
          </Link>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <ArrowPathIcon className="h-8 w-8 text-purple-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">{t.runAudit}</span>
            <span className="text-xs text-gray-500">{t.selfCheck}</span>
          </button>
        </div>
      </div>

      {/* Compliance checklist summary */}
      {checklist.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">{t.checklist}</h3>
            <span className="text-sm text-gray-500">
              {checklist.filter((item) => item.completed).length} {t.outOf} {checklist.length} {t.done}
            </span>
          </div>
          <div className="space-y-3">
            {checklist.map((item, index) => (
              <div key={index} className="flex items-center">
                {item.completed ? (
                  <CheckCircleSolidIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                ) : (
                  <div className="h-5 w-5 rounded-full border-2 border-gray-300 flex-shrink-0" />
                )}
                <span
                  className={`ml-3 text-sm ${
                    item.completed ? "text-gray-500 line-through" : "text-gray-900"
                  }`}
                >
                  {item.title}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
