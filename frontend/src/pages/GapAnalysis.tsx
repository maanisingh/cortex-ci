import { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useLanguage } from "../contexts/LanguageContext";
import { complianceScoringApi, complianceControlsApi, auditsApi, evidenceApi } from "../services/api";
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
  ArrowPathIcon,
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


// Map API implementation status to component status
const mapImplementationStatus = (apiStatus: string): GapStatus => {
  const statusMap: Record<string, GapStatus> = {
    "FULLY_IMPLEMENTED": "compliant",
    "PARTIALLY_IMPLEMENTED": "partial",
    "NOT_IMPLEMENTED": "non_compliant",
    "NOT_ASSESSED": "not_assessed",
    "NOT_APPLICABLE": "compliant",
    "PLANNED": "partial",
  };
  return statusMap[apiStatus] || "not_assessed";
};

export default function GapAnalysis() {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState<"gaps" | "checklists" | "evidence">("gaps");
  const [statusFilter, setStatusFilter] = useState<GapStatus | "all">("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [selectedControl, setSelectedControl] = useState<ControlRequirement | null>(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingControlId, setEditingControlId] = useState<string | null>(null);

  // Fetch controls from API
  const { data: controlsData, isLoading: controlsLoading } = useQuery({
    queryKey: ["compliance-controls"],
    queryFn: () => complianceControlsApi.list(),
  });

  // Fetch gaps from API
  const { data: gapsData, isLoading: gapsLoading } = useQuery({
    queryKey: ["compliance-gaps"],
    queryFn: () => complianceScoringApi.gaps(),
  });

  // Fetch audits/checklists
  const { data: auditsData, isLoading: auditsLoading } = useQuery({
    queryKey: ["audits"],
    queryFn: () => auditsApi.list(),
  });

  // Transform API controls to component format
  const controls: ControlRequirement[] = useMemo(() => {
    if (!controlsData || !Array.isArray(controlsData)) return [];
    return controlsData.map((control: {
      id: string;
      control_id?: string;
      title?: string;
      family?: string;
      category?: string;
      implementation_status?: string;
      description?: string;
      guidance?: string;
      priority?: number;
      references?: string[];
    }) => ({
      id: control.id,
      controlId: control.control_id || `CTRL-${control.id.slice(0, 4)}`,
      controlName: control.title || "Untitled Control",
      frameworkRequirement: control.family || "",
      category: control.category || "General",
      status: mapImplementationStatus(control.implementation_status || "NOT_ASSESSED"),
      currentState: control.description || "",
      gap: control.implementation_status === "NOT_IMPLEMENTED" ? "Требуется внедрение" : "",
      remediation: control.guidance || "",
      priority: (["critical", "high", "medium", "low"][control.priority || 2] || "medium") as Priority,
      progress: control.implementation_status === "FULLY_IMPLEMENTED" ? 100 :
                control.implementation_status === "PARTIALLY_IMPLEMENTED" ? 50 : 0,
      evidence: control.references,
    }));
  }, [controlsData]);

  // Transform audits to checklists format
  const checklists: AuditChecklist[] = useMemo(() => {
    if (!auditsData || !Array.isArray(auditsData)) return [];
    return auditsData.map((audit: {
      id: string;
      name: string;
      assessment_type?: string;
      status?: string;
      controls_assessed?: number;
      controls_compliant?: number;
    }) => ({
      id: audit.id,
      name: audit.name,
      framework: audit.assessment_type || "152-ФЗ",
      totalItems: audit.controls_assessed || 0,
      completedItems: audit.controls_compliant || 0,
      status: (audit.status === "COMPLETED" ? "completed" :
               audit.status === "IN_PROGRESS" ? "in_progress" : "not_started") as "not_started" | "in_progress" | "completed",
    }));
  }, [auditsData]);

  // Handler functions
  const handleOpenChecklist = (checklistId: string) => {
    navigate(`/audits/${checklistId}`);
  };

  const handleUploadEvidence = () => {
    setShowEvidenceModal(true);
  };

  const handleEditControl = (controlId: string) => {
    setEditingControlId(controlId);
    setShowEditModal(true);
  };

  const isLoading = controlsLoading || gapsLoading || auditsLoading;

  // Bilingual translations
  const t = {
    title: language === "ru" ? "Анализ разрывов и подготовка к аудиту" : "Gap Analysis & Audit Preparation",
    subtitle: language === "ru" ? "Оценка соответствия требованиям, отслеживание устранения разрывов" : "Assess compliance requirements, track gap remediation",
    export: language === "ru" ? "Экспорт" : "Export",
    selfAssess: language === "ru" ? "Автооценка" : "Self Assessment",
    overallCompliance: language === "ru" ? "Общий уровень соответствия" : "Overall Compliance Level",
    compliant: language === "ru" ? "Соответствует" : "Compliant",
    partial: language === "ru" ? "Частично" : "Partial",
    nonCompliant: language === "ru" ? "Не соответствует" : "Non-compliant",
    notAssessed: language === "ru" ? "Не оценено" : "Not Assessed",
    gapAnalysis: language === "ru" ? "Анализ разрывов" : "Gap Analysis",
    auditChecklists: language === "ru" ? "Чек-листы аудита" : "Audit Checklists",
    evidenceCollection: language === "ru" ? "Сбор доказательств" : "Evidence Collection",
    allStatuses: language === "ru" ? "Все статусы" : "All Statuses",
    allCategories: language === "ru" ? "Все категории" : "All Categories",
    critical: language === "ru" ? "Критический" : "Critical",
    high: language === "ru" ? "Высокий" : "High",
    medium: language === "ru" ? "Средний" : "Medium",
    low: language === "ru" ? "Низкий" : "Low",
    progress: language === "ru" ? "Прогресс" : "Progress",
    viewDetails: language === "ru" ? "Подробнее" : "View Details",
    startChecklist: language === "ru" ? "Начать проверку" : "Start Checklist",
    continueChecklist: language === "ru" ? "Продолжить" : "Continue",
    viewResults: language === "ru" ? "Результаты" : "View Results",
    items: language === "ru" ? "пунктов" : "items",
    uploadEvidence: language === "ru" ? "Загрузить документ" : "Upload Evidence",
    noResults: language === "ru" ? "Нет результатов" : "No results",
    tryDifferent: language === "ru" ? "Попробуйте изменить фильтры" : "Try different filters",
    // Table headers
    control: language === "ru" ? "Контроль" : "Control",
    requirement: language === "ru" ? "Требование" : "Requirement",
    status: language === "ru" ? "Статус" : "Status",
    priority: language === "ru" ? "Приоритет" : "Priority",
    dueDate: language === "ru" ? "Срок" : "Due Date",
    // Checklist statuses
    completed: language === "ru" ? "Завершено" : "Completed",
    inProgress: language === "ru" ? "В работе" : "In Progress",
    notStarted: language === "ru" ? "Не начато" : "Not Started",
    openChecklist: language === "ru" ? "Открыть чек-лист" : "Open Checklist",
    // Evidence tab
    evidenceTitle: language === "ru" ? "Сбор доказательств" : "Evidence Collection",
    evidenceDesc: language === "ru"
      ? "Загрузите документы, скриншоты и другие доказательства соответствия требованиям для подготовки к аудиту."
      : "Upload documents, screenshots and other compliance evidence for audit preparation.",
    uploadEvidenceBtn: language === "ru" ? "Загрузить доказательства" : "Upload Evidence",
    // Modal labels
    currentState: language === "ru" ? "Текущее состояние" : "Current State",
    identifiedGap: language === "ru" ? "Выявленный разрыв" : "Identified Gap",
    remediationPlan: language === "ru" ? "План устранения" : "Remediation Plan",
    relatedDocs: language === "ru" ? "Связанные документы" : "Related Documents",
    close: language === "ru" ? "Закрыть" : "Close",
    edit: language === "ru" ? "Редактировать" : "Edit",
    // Categories
    organizationalMeasures: language === "ru" ? "Организационные меры" : "Organizational Measures",
    technicalMeasures: language === "ru" ? "Технические меры" : "Technical Measures",
    regulatoryReqs: language === "ru" ? "Регуляторные требования" : "Regulatory Requirements",
    legalBasis: language === "ru" ? "Правовые основания" : "Legal Basis",
  };

  // Bilingual status labels
  const getStatusLabel = (status: GapStatus) => {
    const labels: Record<GapStatus, string> = {
      compliant: t.compliant,
      partial: t.partial,
      non_compliant: t.nonCompliant,
      not_assessed: t.notAssessed,
    };
    return labels[status];
  };

  // Bilingual priority labels
  const getPriorityLabel = (priority: Priority) => {
    const labels: Record<Priority, string> = {
      critical: t.critical,
      high: t.high,
      medium: t.medium,
      low: t.low,
    };
    return labels[priority];
  };

  // Calculate stats from controls
  const stats = useMemo(() => {
    const total = controls.length;
    const compliant = controls.filter((c) => c.status === "compliant").length;
    const partial = controls.filter((c) => c.status === "partial").length;
    const nonCompliant = controls.filter((c) => c.status === "non_compliant").length;
    const notAssessed = controls.filter((c) => c.status === "not_assessed").length;
    const overallScore = total > 0 ? Math.round(
      (compliant * 100 + partial * 50) / (total - notAssessed || 1)
    ) : 0;
    return { total, compliant, partial, nonCompliant, notAssessed, overallScore };
  }, [controls]);

  // Filter controls
  const filteredControls = useMemo(() => {
    return controls.filter((control) => {
      if (statusFilter !== "all" && control.status !== statusFilter) return false;
      if (categoryFilter !== "all" && control.category !== categoryFilter) return false;
      return true;
    });
  }, [controls, statusFilter, categoryFilter]);

  // Get unique categories
  const categories = useMemo(() => {
    return [...new Set(controls.map((c) => c.category))];
  }, [controls]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t.title}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t.subtitle}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            {t.export}
          </button>
          <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <SparklesIcon className="h-5 w-5 mr-2" />
            {t.selfAssess}
          </button>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl shadow-lg p-6 text-white">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h2 className="text-lg font-medium text-blue-100">{t.overallCompliance}</h2>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-5xl font-bold">{stats.overallScore}%</span>
              <span className="text-blue-200">152-ФЗ</span>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-green-300">{stats.compliant}</p>
              <p className="text-xs text-blue-200">{t.compliant}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-yellow-300">{stats.partial}</p>
              <p className="text-xs text-blue-200">{t.partial}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-red-300">{stats.nonCompliant}</p>
              <p className="text-xs text-blue-200">{t.nonCompliant}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-gray-300">{stats.notAssessed}</p>
              <p className="text-xs text-blue-200">{t.notAssessed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-6">
          {[
            { id: "gaps", label: t.gapAnalysis, icon: ChartBarIcon },
            { id: "checklists", label: t.auditChecklists, icon: ClipboardDocumentListIcon },
            { id: "evidence", label: t.evidenceCollection, icon: FolderOpenIcon },
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
              <option value="all">{t.allStatuses}</option>
              <option value="compliant">{t.compliant}</option>
              <option value="partial">{t.partial}</option>
              <option value="non_compliant">{t.nonCompliant}</option>
              <option value="not_assessed">{t.notAssessed}</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
            >
              <option value="all">{t.allCategories}</option>
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
                      {t.control}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {t.requirement}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {t.status}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {t.progress}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {t.priority}
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {t.dueDate}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {isLoading ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center">
                        <ArrowPathIcon className="h-8 w-8 mx-auto text-blue-500 animate-spin" />
                        <p className="mt-4 text-gray-500">{language === "ru" ? "Загрузка контролей..." : "Loading controls..."}</p>
                      </td>
                    </tr>
                  ) : filteredControls.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center">
                        <ChartBarIcon className="h-12 w-12 mx-auto text-gray-300" />
                        <p className="mt-4 text-gray-500">{language === "ru" ? "Контроли не найдены" : "No controls found"}</p>
                      </td>
                    </tr>
                  ) : filteredControls.map((control) => {
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
                            {getStatusLabel(control.status)}
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
                            {getPriorityLabel(control.priority)}
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
          {isLoading ? (
            <div className="col-span-2 py-12 text-center">
              <ArrowPathIcon className="h-8 w-8 mx-auto text-blue-500 animate-spin" />
              <p className="mt-4 text-gray-500">{language === "ru" ? "Загрузка..." : "Loading..."}</p>
            </div>
          ) : checklists.length === 0 ? (
            <div className="col-span-2 py-12 text-center">
              <ClipboardDocumentListIcon className="h-12 w-12 mx-auto text-gray-300" />
              <p className="mt-4 text-gray-500">{language === "ru" ? "Нет чек-листов" : "No checklists"}</p>
            </div>
          ) : checklists.map((checklist) => (
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
                    ? t.completed
                    : checklist.status === "in_progress"
                    ? t.inProgress
                    : t.notStarted}
                </span>
              </div>
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-500 dark:text-gray-400">{t.progress}</span>
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
              <button
                onClick={() => handleOpenChecklist(checklist.id)}
                className="mt-4 w-full py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              >
                {t.openChecklist}
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
              {t.evidenceTitle}
            </h3>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              {t.evidenceDesc}
            </p>
            <button
              onClick={handleUploadEvidence}
              className="mt-6 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              {t.uploadEvidenceBtn}
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
                      {t.currentState}
                    </label>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {selectedControl.currentState}
                    </p>
                  </div>

                  {selectedControl.gap && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t.identifiedGap}
                      </label>
                      <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                        {selectedControl.gap}
                      </p>
                    </div>
                  )}

                  {selectedControl.remediation && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t.remediationPlan}
                      </label>
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {selectedControl.remediation}
                      </p>
                    </div>
                  )}

                  {selectedControl.evidence && selectedControl.evidence.length > 0 && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t.relatedDocs}
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
                      {t.close}
                    </button>
                    <button
                      onClick={() => {
                        handleEditControl(selectedControl.id);
                        setSelectedControl(null);
                      }}
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      {t.edit}
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
