import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  UserGroupIcon,
  ServerStackIcon,
  ArrowTrendingUpIcon,
  ChevronRightIcon,
  CalendarIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  DocumentDuplicateIcon,
  FlagIcon,
  ArrowPathIcon,
  BellAlertIcon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolidIcon } from "@heroicons/react/24/solid";

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

export default function RussianDashboard() {
  const [selectedCompany, setSelectedCompany] = useState<string>("1");

  // Mock data
  const companyData = {
    id: "1",
    name: "ООО «Демо Компания»",
    inn: "7707083893",
    ispdnCount: 3,
    employeeCount: 150,
    documentsTotal: 24,
    documentsApproved: 18,
    tasksTotal: 12,
    tasksCompleted: 8,
    overallScore: 75,
  };

  const complianceScores: ComplianceScore[] = [
    {
      framework: "fz152",
      frameworkName: "152-ФЗ «О персональных данных»",
      score: 78,
      total: 24,
      completed: 18,
      inProgress: 3,
      pending: 2,
      overdue: 1,
    },
    {
      framework: "fz187",
      frameworkName: "187-ФЗ «О безопасности КИИ»",
      score: 45,
      total: 16,
      completed: 7,
      inProgress: 4,
      pending: 5,
      overdue: 0,
    },
    {
      framework: "gost57580",
      frameworkName: "ГОСТ Р 57580 (Банковская безопасность)",
      score: 62,
      total: 32,
      completed: 20,
      inProgress: 6,
      pending: 4,
      overdue: 2,
    },
    {
      framework: "fstec",
      frameworkName: "Приказы ФСТЭК (№ 17, 21, 31, 239)",
      score: 55,
      total: 48,
      completed: 26,
      inProgress: 10,
      pending: 10,
      overdue: 2,
    },
  ];

  const recentActivities: RecentActivity[] = [
    {
      id: "1",
      type: "document",
      action: "Создан документ",
      title: "Политика обработки персональных данных",
      user: "Иванов И.И.",
      timestamp: "2024-01-15T14:30:00Z",
    },
    {
      id: "2",
      type: "task",
      action: "Задача выполнена",
      title: "Провести обучение сотрудников",
      user: "Петров П.П.",
      timestamp: "2024-01-15T12:00:00Z",
    },
    {
      id: "3",
      type: "ispdn",
      action: "Классификация ИСПДн",
      title: "CRM-система — УЗ-3",
      user: "Сидоров С.С.",
      timestamp: "2024-01-15T10:15:00Z",
    },
    {
      id: "4",
      type: "document",
      action: "Документ утверждён",
      title: "Инструкция пользователя ИСПДн",
      user: "Директор",
      timestamp: "2024-01-14T16:45:00Z",
    },
    {
      id: "5",
      type: "training",
      action: "Обучение пройдено",
      title: "Основы защиты ПДн",
      user: "12 сотрудников",
      timestamp: "2024-01-14T14:00:00Z",
    },
  ];

  const upcomingDeadlines: UpcomingDeadline[] = [
    {
      id: "1",
      title: "Подать уведомление в Роскомнадзор",
      type: "Задача",
      dueDate: "2024-01-20T00:00:00Z",
      priority: "critical",
      assignee: "Иванов И.И.",
    },
    {
      id: "2",
      title: "Утвердить Политику обработки ПДн",
      type: "Документ",
      dueDate: "2024-01-25T00:00:00Z",
      priority: "high",
      assignee: "Директор",
    },
    {
      id: "3",
      title: "Разработать модель угроз",
      type: "Документ",
      dueDate: "2024-02-01T00:00:00Z",
      priority: "high",
      assignee: "Сидоров С.С.",
    },
    {
      id: "4",
      title: "Провести аудит ИСПДн",
      type: "Задача",
      dueDate: "2024-02-10T00:00:00Z",
      priority: "medium",
      assignee: "Петров П.П.",
    },
  ];

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Панель соответствия — Российское законодательство
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Комплексный мониторинг соответствия требованиям 152-ФЗ, 187-ФЗ, ГОСТ Р 57580, ФСТЭК
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            to="/russian-onboarding"
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <BuildingOfficeIcon className="h-5 w-5 mr-2" />
            Добавить организацию
          </Link>
          <Link
            to="/russian-compliance"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <DocumentDuplicateIcon className="h-5 w-5 mr-2" />
            Документы
          </Link>
        </div>
      </div>

      {/* Company overview card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold">{companyData.name}</h2>
            <p className="text-blue-100">ИНН: {companyData.inn}</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{companyData.overallScore}%</div>
            <div className="text-blue-100">Общий уровень соответствия</div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <ServerStackIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{companyData.ispdnCount}</div>
                <div className="text-sm text-blue-200">ИСПДн</div>
              </div>
            </div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center">
              <UserGroupIcon className="h-8 w-8 text-blue-200" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{companyData.employeeCount}</div>
                <div className="text-sm text-blue-200">Сотрудников</div>
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
                <div className="text-sm text-blue-200">Документов</div>
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
                <div className="text-sm text-blue-200">Задач</div>
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
                <div className="text-xs text-green-600">Выполнено</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-lg font-bold text-blue-700">{framework.inProgress}</div>
                <div className="text-xs text-blue-600">В работе</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-2">
                <div className="text-lg font-bold text-gray-700">{framework.pending}</div>
                <div className="text-xs text-gray-600">Ожидает</div>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <div className="text-lg font-bold text-red-700">{framework.overdue}</div>
                <div className="text-xs text-red-600">Просрочено</div>
              </div>
            </div>

            <div className="mt-4">
              <Link
                to={`/russian-compliance?framework=${framework.framework}`}
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
              >
                Подробнее о требованиях
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
            <h3 className="text-lg font-medium text-gray-900">Последние действия</h3>
            <button className="text-sm text-blue-600 hover:text-blue-700">Показать все</button>
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
            <h3 className="text-lg font-medium text-gray-900">Ближайшие сроки</h3>
            <Link to="/compliance-tasks" className="text-sm text-blue-600 hover:text-blue-700">
              Все задачи
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
                          {deadline.priority === "critical" && "Критично"}
                          {deadline.priority === "high" && "Высокий"}
                          {deadline.priority === "medium" && "Средний"}
                          {deadline.priority === "low" && "Низкий"}
                        </span>
                      </div>
                      <p className="mt-1 text-sm font-medium text-gray-900">{deadline.title}</p>
                      <p className="text-xs text-gray-500">Исполнитель: {deadline.assignee}</p>
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
                          ? "Сегодня"
                          : daysUntil === 1
                          ? "Завтра"
                          : daysUntil < 0
                          ? `${Math.abs(daysUntil)} дн. назад`
                          : `${daysUntil} дн.`}
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
        <h3 className="text-lg font-medium text-gray-900 mb-4">Быстрые действия</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/russian-onboarding"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <BuildingOfficeIcon className="h-8 w-8 text-blue-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">Новая организация</span>
            <span className="text-xs text-gray-500">Полный цикл регистрации</span>
          </Link>
          <Link
            to="/russian-compliance"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <DocumentDuplicateIcon className="h-8 w-8 text-green-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">Генерация документов</span>
            <span className="text-xs text-gray-500">Пакет 152-ФЗ</span>
          </Link>
          <Link
            to="/compliance-tasks"
            className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <ClockIcon className="h-8 w-8 text-orange-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">Управление задачами</span>
            <span className="text-xs text-gray-500">Kanban-доска</span>
          </Link>
          <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <ArrowPathIcon className="h-8 w-8 text-purple-600" />
            <span className="mt-2 text-sm font-medium text-gray-900">Провести аудит</span>
            <span className="text-xs text-gray-500">Самопроверка</span>
          </button>
        </div>
      </div>

      {/* Compliance checklist summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Чек-лист соответствия 152-ФЗ</h3>
          <span className="text-sm text-gray-500">8 из 10 выполнено</span>
        </div>
        <div className="space-y-3">
          {[
            { title: "Назначен ответственный за ПДн", completed: true },
            { title: "Утверждена политика обработки ПДн", completed: true },
            { title: "Определены цели обработки ПДн", completed: true },
            { title: "Проведена классификация ИСПДн", completed: true },
            { title: "Разработана модель угроз", completed: true },
            { title: "Внедрены технические меры защиты", completed: true },
            { title: "Подготовлены согласия на обработку ПДн", completed: true },
            { title: "Обучены сотрудники", completed: true },
            { title: "Подано уведомление в Роскомнадзор", completed: false },
            { title: "Проведён внутренний аудит", completed: false },
          ].map((item, index) => (
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
    </div>
  );
}
