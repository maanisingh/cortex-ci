import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowTrendingUpIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  FolderOpenIcon,
  PlusIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  LinkIcon,
  ChevronRightIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";

type GapStatus = "compliant" | "partial" | "non_compliant" | "not_assessed";
type Priority = "critical" | "high" | "medium" | "low";

interface ControlRequirement {
  id: string;
  controlId: string;
  controlName: string;
  frameworkRequirement: string;
  category: string;
  status: GapStatus;
  currentState: string;
  gap: string;
  remediation: string;
  priority: Priority;
  dueDate?: string;
  evidence?: string[];
  assignee?: string;
  progress: number;
}

interface AuditChecklist {
  id: string;
  name: string;
  framework: string;
  totalItems: number;
  completedItems: number;
  status: "not_started" | "in_progress" | "completed";
}

const statusConfig: Record<GapStatus, { label: string; color: string; bgColor: string; icon: typeof CheckCircleIcon }> = {
  compliant: {
    label: "Соответствует",
    color: "text-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    icon: CheckCircleIcon,
  },
  partial: {
    label: "Частично",
    color: "text-yellow-600",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
    icon: ExclamationTriangleIcon,
  },
  non_compliant: {
    label: "Не соответствует",
    color: "text-red-600",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    icon: XCircleIcon,
  },
  not_assessed: {
    label: "Не оценено",
    color: "text-gray-500",
    bgColor: "bg-gray-100 dark:bg-gray-700",
    icon: ClipboardDocumentListIcon,
  },
};

const priorityConfig: Record<Priority, { label: string; color: string }> = {
  critical: { label: "Критический", color: "text-red-600 bg-red-50 dark:bg-red-900/20" },
  high: { label: "Высокий", color: "text-orange-600 bg-orange-50 dark:bg-orange-900/20" },
  medium: { label: "Средний", color: "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20" },
  low: { label: "Низкий", color: "text-gray-600 bg-gray-50 dark:bg-gray-700" },
};

// Mock data for gap analysis
const mockControls: ControlRequirement[] = [
  {
    id: "1",
    controlId: "CTRL-001",
    controlName: "Политика обработки ПДн",
    frameworkRequirement: "ст. 18.1 152-ФЗ",
    category: "Организационные меры",
    status: "compliant",
    currentState: "Политика утверждена и опубликована",
    gap: "",
    remediation: "",
    priority: "high",
    progress: 100,
    evidence: ["POL-001", "ORD-001"],
  },
  {
    id: "2",
    controlId: "CTRL-002",
    controlName: "Назначение ответственного за ПДн",
    frameworkRequirement: "ст. 22.1 152-ФЗ",
    category: "Организационные меры",
    status: "compliant",
    currentState: "Ответственный назначен приказом",
    gap: "",
    remediation: "",
    priority: "critical",
    progress: 100,
    evidence: ["ORD-002"],
    assignee: "Иванов И.И.",
  },
  {
    id: "3",
    controlId: "CTRL-003",
    controlName: "Уведомление Роскомнадзора",
    frameworkRequirement: "ст. 22 152-ФЗ",
    category: "Регуляторные требования",
    status: "partial",
    currentState: "Уведомление подано, ожидает подтверждения",
    gap: "Не получено подтверждение регистрации",
    remediation: "Проверить статус уведомления в ЛК РКН",
    priority: "critical",
    dueDate: "2024-02-01",
    progress: 70,
    assignee: "Петров П.П.",
  },
  {
    id: "4",
    controlId: "CTRL-004",
    controlName: "Модель угроз безопасности ПДн",
    frameworkRequirement: "п. 2 ПП РФ № 1119",
    category: "Технические меры",
    status: "non_compliant",
    currentState: "Модель угроз отсутствует",
    gap: "Не разработана модель угроз для ИСПДн",
    remediation: "Разработать модель угроз по методике ФСТЭК",
    priority: "high",
    dueDate: "2024-02-15",
    progress: 20,
    assignee: "Сидоров С.С.",
  },
  {
    id: "5",
    controlId: "CTRL-005",
    controlName: "Классификация ИСПДн",
    frameworkRequirement: "ПП РФ № 1119",
    category: "Технические меры",
    status: "partial",
    currentState: "Классификация выполнена для 2 из 3 ИСПДн",
    gap: "Не классифицирована CRM-система",
    remediation: "Провести классификацию CRM как ИСПДн",
    priority: "high",
    dueDate: "2024-01-25",
    progress: 66,
    assignee: "Сидоров С.С.",
  },
  {
    id: "6",
    controlId: "CTRL-006",
    controlName: "Обучение персонала",
    frameworkRequirement: "ст. 18.1 152-ФЗ",
    category: "Организационные меры",
    status: "partial",
    currentState: "Обучено 80% сотрудников",
    gap: "20% сотрудников не прошли обучение",
    remediation: "Провести обучение для оставшихся сотрудников",
    priority: "medium",
    dueDate: "2024-02-28",
    progress: 80,
    assignee: "HR отдел",
  },
  {
    id: "7",
    controlId: "CTRL-007",
    controlName: "Согласия на обработку ПДн",
    frameworkRequirement: "ст. 9 152-ФЗ",
    category: "Правовые основания",
    status: "compliant",
    currentState: "Согласия получены от всех субъектов",
    gap: "",
    remediation: "",
    priority: "high",
    progress: 100,
    evidence: ["FORM-001"],
  },
  {
    id: "8",
    controlId: "CTRL-008",
    controlName: "Журнал учёта обращений",
    frameworkRequirement: "ст. 20 152-ФЗ",
    category: "Организационные меры",
    status: "not_assessed",
    currentState: "Не проверено",
    gap: "Требуется оценка",
    remediation: "Провести проверку наличия журнала",
    priority: "medium",
    progress: 0,
  },
];

const mockChecklists: AuditChecklist[] = [
  {
    id: "1",
    name: "Чек-лист 152-ФЗ: Организационные меры",
    framework: "152-ФЗ",
    totalItems: 25,
    completedItems: 20,
    status: "in_progress",
  },
  {
    id: "2",
    name: "Чек-лист 152-ФЗ: Технические меры",
    framework: "152-ФЗ",
    totalItems: 30,
    completedItems: 18,
    status: "in_progress",
  },
  {
    id: "3",
    name: "Чек-лист 152-ФЗ: Правовые основания",
    framework: "152-ФЗ",
    totalItems: 15,
    completedItems: 15,
    status: "completed",
  },
  {
    id: "4",
    name: "Подготовка к проверке РКН",
    framework: "152-ФЗ",
    totalItems: 40,
    completedItems: 0,
    status: "not_started",
  },
];

export default function GapAnalysis() {
  const [selectedTab, setSelectedTab] = useState<"gaps" | "checklists" | "evidence">("gaps");
  const [statusFilter, setStatusFilter] = useState<GapStatus | "all">("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [selectedControl, setSelectedControl] = useState<ControlRequirement | null>(null);

  // Calculate stats
  const stats = useMemo(() => {
    const total = mockControls.length;
    const compliant = mockControls.filter((c) => c.status === "compliant").length;
    const partial = mockControls.filter((c) => c.status === "partial").length;
    const nonCompliant = mockControls.filter((c) => c.status === "non_compliant").length;
    const notAssessed = mockControls.filter((c) => c.status === "not_assessed").length;
    const overallScore = Math.round(
      (compliant * 100 + partial * 50) / (total - notAssessed || 1)
    );
    return { total, compliant, partial, nonCompliant, notAssessed, overallScore };
  }, []);

  // Filter controls
  const filteredControls = useMemo(() => {
    return mockControls.filter((control) => {
      if (statusFilter !== "all" && control.status !== statusFilter) return false;
      if (categoryFilter !== "all" && control.category !== categoryFilter) return false;
      return true;
    });
  }, [statusFilter, categoryFilter]);

  // Get unique categories
  const categories = useMemo(() => {
    return [...new Set(mockControls.map((c) => c.category))];
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Анализ разрывов и подготовка к аудиту
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Оценка соответствия требованиям, отслеживание устранения разрывов
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            Экспорт
          </button>
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <SparklesIcon className="h-5 w-5 mr-2" />
            Автооценка
          </button>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl shadow-lg p-6 text-white">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h2 className="text-lg font-medium text-blue-100">Общий уровень соответствия</h2>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-5xl font-bold">{stats.overallScore}%</span>
              <span className="text-blue-200">152-ФЗ</span>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-green-300">{stats.compliant}</p>
              <p className="text-xs text-blue-200">Соответствует</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-yellow-300">{stats.partial}</p>
              <p className="text-xs text-blue-200">Частично</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-300">{stats.nonCompliant}</p>
              <p className="text-xs text-blue-200">Не соответствует</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-gray-300">{stats.notAssessed}</p>
              <p className="text-xs text-blue-200">Не оценено</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-6">
          {[
            { id: "gaps", label: "Анализ разрывов", icon: ChartBarIcon },
            { id: "checklists", label: "Чек-листы аудита", icon: ClipboardDocumentListIcon },
            { id: "evidence", label: "Сбор доказательств", icon: FolderOpenIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id as any)}
              className={`flex items-center gap-2 py-3 border-b-2 text-sm font-medium transition-colors ${
                selectedTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Gap Analysis Tab */}
      {selectedTab === "gaps" && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as GapStatus | "all")}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
            >
              <option value="all">Все статусы</option>
              <option value="compliant">Соответствует</option>
              <option value="partial">Частично</option>
              <option value="non_compliant">Не соответствует</option>
              <option value="not_assessed">Не оценено</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
            >
              <option value="all">Все категории</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Controls Table */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Контроль
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Требование
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Статус
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Прогресс
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Приоритет
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Срок
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredControls.map((control) => {
                    const statusConf = statusConfig[control.status];
                    const StatusIcon = statusConf.icon;
                    const priorityConf = priorityConfig[control.priority];

                    return (
                      <tr
                        key={control.id}
                        onClick={() => setSelectedControl(control)}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                      >
                        <td className="px-4 py-4">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {control.controlName}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {control.controlId} • {control.category}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <span className="text-sm text-blue-600 dark:text-blue-400">
                            {control.frameworkRequirement}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusConf.bgColor} ${statusConf.color}`}
                          >
                            <StatusIcon className="h-3.5 w-3.5" />
                            {statusConf.label}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className="w-24">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${
                                    control.progress >= 80
                                      ? "bg-green-500"
                                      : control.progress >= 50
                                      ? "bg-yellow-500"
                                      : "bg-red-500"
                                  }`}
                                  style={{ width: `${control.progress}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500">{control.progress}%</span>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-medium ${priorityConf.color}`}
                          >
                            {priorityConf.label}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          {control.dueDate ? (
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              {new Date(control.dueDate).toLocaleDateString("ru-RU")}
                            </span>
                          ) : (
                            <span className="text-sm text-gray-400">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Checklists Tab */}
      {selectedTab === "checklists" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockChecklists.map((checklist) => (
            <div
              key={checklist.id}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">{checklist.name}</h3>
                  <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                    {checklist.framework}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    checklist.status === "completed"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : checklist.status === "in_progress"
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      : "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400"
                  }`}
                >
                  {checklist.status === "completed"
                    ? "Завершено"
                    : checklist.status === "in_progress"
                    ? "В работе"
                    : "Не начато"}
                </span>
              </div>
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-500 dark:text-gray-400">Прогресс</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {checklist.completedItems}/{checklist.totalItems}
                  </span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{
                      width: `${(checklist.completedItems / checklist.totalItems) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <button className="mt-4 w-full py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
                Открыть чек-лист
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Evidence Tab */}
      {selectedTab === "evidence" && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="text-center py-12">
            <FolderOpenIcon className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600" />
            <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
              Сбор доказательств
            </h3>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              Загрузите документы, скриншоты и другие доказательства соответствия требованиям
              для подготовки к аудиту.
            </p>
            <button className="mt-6 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <PlusIcon className="h-5 w-5 mr-2" />
              Загрузить доказательства
            </button>
          </div>
        </div>
      )}

      {/* Control Detail Modal */}
      {selectedControl && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setSelectedControl(null)} />
            <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedControl.controlName}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {selectedControl.controlId} • {selectedControl.frameworkRequirement}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedControl(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Текущее состояние
                    </label>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {selectedControl.currentState}
                    </p>
                  </div>

                  {selectedControl.gap && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Выявленный разрыв
                      </label>
                      <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                        {selectedControl.gap}
                      </p>
                    </div>
                  )}

                  {selectedControl.remediation && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        План устранения
                      </label>
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {selectedControl.remediation}
                      </p>
                    </div>
                  )}

                  {selectedControl.evidence && selectedControl.evidence.length > 0 && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Связанные документы
                      </label>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {selectedControl.evidence.map((doc) => (
                          <span
                            key={doc}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded text-sm"
                          >
                            <LinkIcon className="h-3.5 w-3.5" />
                            {doc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 flex justify-end gap-3">
                    <button
                      onClick={() => setSelectedControl(null)}
                      className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900"
                    >
                      Закрыть
                    </button>
                    <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Редактировать
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
