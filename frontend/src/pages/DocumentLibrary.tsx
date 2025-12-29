import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  DocumentDuplicateIcon,
  ArrowPathIcon,
  LinkIcon,
  ChevronRightIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { russianComplianceApi } from "../services/api";

type DocumentStatus = "draft" | "pending_review" | "approved" | "expired" | "archived";
type DocumentType = "policy" | "order" | "instruction" | "journal" | "form" | "agreement";

interface Document {
  id: string;
  title: string;
  templateCode: string;
  documentType: DocumentType;
  framework: string;
  status: DocumentStatus;
  version: number;
  createdAt: string;
  updatedAt: string;
  approvedBy?: string;
  approvedAt?: string;
  expiresAt?: string;
  linkedControls?: string[];
  linkedEvidence?: string[];
  tags?: string[];
}

const statusConfig: Record<DocumentStatus, { label: string; color: string; bgColor: string; icon: typeof CheckCircleIcon }> = {
  draft: {
    label: "Черновик",
    color: "text-gray-600",
    bgColor: "bg-gray-100 dark:bg-gray-700",
    icon: PencilSquareIcon,
  },
  pending_review: {
    label: "На проверке",
    color: "text-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
    icon: ClockIcon,
  },
  approved: {
    label: "Утверждён",
    color: "text-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    icon: CheckCircleIcon,
  },
  expired: {
    label: "Истёк срок",
    color: "text-red-600",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    icon: ExclamationCircleIcon,
  },
  archived: {
    label: "Архив",
    color: "text-gray-500",
    bgColor: "bg-gray-50 dark:bg-gray-800",
    icon: DocumentTextIcon,
  },
};

const documentTypeConfig: Record<DocumentType, { label: string; labelEn: string }> = {
  policy: { label: "Политика", labelEn: "Policy" },
  order: { label: "Приказ", labelEn: "Order" },
  instruction: { label: "Инструкция", labelEn: "Instruction" },
  journal: { label: "Журнал", labelEn: "Journal" },
  form: { label: "Форма", labelEn: "Form" },
  agreement: { label: "Соглашение", labelEn: "Agreement" },
};

// Mock documents data
const mockDocuments: Document[] = [
  {
    id: "1",
    title: "Политика обработки персональных данных",
    templateCode: "POLICY_PD_PROCESSING",
    documentType: "policy",
    framework: "152-ФЗ",
    status: "approved",
    version: 3,
    createdAt: "2024-01-10T10:00:00Z",
    updatedAt: "2024-01-15T14:30:00Z",
    approvedBy: "Иванов И.И.",
    approvedAt: "2024-01-15T14:30:00Z",
    expiresAt: "2025-01-15T00:00:00Z",
    linkedControls: ["CTRL-001", "CTRL-002"],
    tags: ["ПДн", "обработка"],
  },
  {
    id: "2",
    title: "Приказ о назначении ответственного за ПДн",
    templateCode: "ORDER_RESPONSIBLE",
    documentType: "order",
    framework: "152-ФЗ",
    status: "approved",
    version: 1,
    createdAt: "2024-01-10T10:00:00Z",
    updatedAt: "2024-01-10T10:00:00Z",
    approvedBy: "Директор",
    approvedAt: "2024-01-10T10:00:00Z",
    linkedControls: ["CTRL-003"],
    tags: ["ПДн", "ответственный"],
  },
  {
    id: "3",
    title: "Положение о защите персональных данных",
    templateCode: "POLICY_PD_PROTECTION",
    documentType: "policy",
    framework: "152-ФЗ",
    status: "pending_review",
    version: 2,
    createdAt: "2024-01-12T09:00:00Z",
    updatedAt: "2024-01-18T11:00:00Z",
    tags: ["ПДн", "защита"],
  },
  {
    id: "4",
    title: "Журнал учёта обращений субъектов ПДн",
    templateCode: "JOURNAL_REQUESTS",
    documentType: "journal",
    framework: "152-ФЗ",
    status: "draft",
    version: 1,
    createdAt: "2024-01-14T08:00:00Z",
    updatedAt: "2024-01-14T08:00:00Z",
    tags: ["журнал", "обращения"],
  },
  {
    id: "5",
    title: "Согласие на обработку персональных данных",
    templateCode: "FORM_CONSENT",
    documentType: "form",
    framework: "152-ФЗ",
    status: "approved",
    version: 2,
    createdAt: "2024-01-08T10:00:00Z",
    updatedAt: "2024-01-12T16:00:00Z",
    approvedBy: "Юрист",
    approvedAt: "2024-01-12T16:00:00Z",
    tags: ["согласие", "форма"],
  },
  {
    id: "6",
    title: "Инструкция пользователя ИСПДн",
    templateCode: "INSTRUCTION_USER",
    documentType: "instruction",
    framework: "152-ФЗ",
    status: "expired",
    version: 1,
    createdAt: "2023-01-10T10:00:00Z",
    updatedAt: "2023-01-10T10:00:00Z",
    expiresAt: "2024-01-10T00:00:00Z",
    tags: ["ИСПДн", "пользователь"],
  },
];

export default function DocumentLibrary() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | "all">("all");
  const [typeFilter, setTypeFilter] = useState<DocumentType | "all">("all");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [showBulkGenerate, setShowBulkGenerate] = useState(false);

  // Use mock data for now
  const documents = mockDocuments;
  const isLoading = false;

  // Filter documents
  const filteredDocuments = useMemo(() => {
    return documents.filter((doc) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !doc.title.toLowerCase().includes(query) &&
          !doc.templateCode.toLowerCase().includes(query) &&
          !doc.tags?.some((tag) => tag.toLowerCase().includes(query))
        ) {
          return false;
        }
      }
      if (statusFilter !== "all" && doc.status !== statusFilter) return false;
      if (typeFilter !== "all" && doc.documentType !== typeFilter) return false;
      return true;
    });
  }, [documents, searchQuery, statusFilter, typeFilter]);

  // Stats
  const stats = useMemo(() => {
    const total = documents.length;
    const approved = documents.filter((d) => d.status === "approved").length;
    const draft = documents.filter((d) => d.status === "draft").length;
    const pending = documents.filter((d) => d.status === "pending_review").length;
    const expired = documents.filter((d) => d.status === "expired").length;
    return { total, approved, draft, pending, expired };
  }, [documents]);

  // Handle bulk selection
  const toggleSelectDoc = (id: string) => {
    setSelectedDocs((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const selectAllDocs = () => {
    if (selectedDocs.length === filteredDocuments.length) {
      setSelectedDocs([]);
    } else {
      setSelectedDocs(filteredDocuments.map((d) => d.id));
    }
  };

  // Handle bulk actions
  const handleBulkApprove = () => {
    console.log("Approving documents:", selectedDocs);
    setSelectedDocs([]);
  };

  const handleBulkExport = () => {
    console.log("Exporting documents:", selectedDocs);
    setSelectedDocs([]);
  };

  // Bulk document generation
  const bulkGenerateMutation = useMutation({
    mutationFn: async () => {
      // In production, this would call the API to generate all documents
      await new Promise((resolve) => setTimeout(resolve, 2000));
      return { success: true, documentsGenerated: 22 };
    },
    onSuccess: () => {
      setShowBulkGenerate(false);
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Библиотека документов
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Управление документами соответствия с версионированием и согласованием
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowBulkGenerate(true)}
            className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-sm"
          >
            <SparklesIcon className="h-5 w-5 mr-2" />
            Сгенерировать пакет 152-ФЗ
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <DocumentTextIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Всего</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Утверждено</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <PencilSquareIcon className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-600">{stats.draft}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Черновики</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <ClockIcon className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{stats.pending}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">На проверке</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <ExclamationCircleIcon className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats.expired}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Истёк срок</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по названию, коду или тегам..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as DocumentStatus | "all")}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="all">Все статусы</option>
              <option value="draft">Черновик</option>
              <option value="pending_review">На проверке</option>
              <option value="approved">Утверждён</option>
              <option value="expired">Истёк срок</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as DocumentType | "all")}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value="all">Все типы</option>
              <option value="policy">Политики</option>
              <option value="order">Приказы</option>
              <option value="instruction">Инструкции</option>
              <option value="journal">Журналы</option>
              <option value="form">Формы</option>
            </select>
          </div>
        </div>

        {/* Bulk Actions */}
        {selectedDocs.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Выбрано: {selectedDocs.length}
            </span>
            <button
              onClick={handleBulkApprove}
              className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Утвердить
            </button>
            <button
              onClick={handleBulkExport}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Экспортировать
            </button>
            <button
              onClick={() => setSelectedDocs([])}
              className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              Отменить выбор
            </button>
          </div>
        )}
      </div>

      {/* Documents List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                <th className="w-10 px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedDocs.length === filteredDocuments.length && filteredDocuments.length > 0}
                    onChange={selectAllDocs}
                    className="rounded border-gray-300 dark:border-gray-600"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Документ
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Тип
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Версия
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Связи
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Обновлено
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredDocuments.map((doc) => {
                const statusConf = statusConfig[doc.status];
                const StatusIcon = statusConf.icon;
                const typeConf = documentTypeConfig[doc.documentType];

                return (
                  <tr
                    key={doc.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedDocs.includes(doc.id)}
                        onChange={() => toggleSelectDoc(doc.id)}
                        className="rounded border-gray-300 dark:border-gray-600"
                      />
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-start gap-3">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <Link
                            to={`/documents/${doc.id}`}
                            className="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400"
                          >
                            {doc.title}
                          </Link>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                            {doc.templateCode}
                          </p>
                          {doc.tags && doc.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {doc.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {typeConf.label}
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
                      <span className="text-sm text-gray-600 dark:text-gray-400">v{doc.version}</span>
                    </td>
                    <td className="px-4 py-4">
                      {doc.linkedControls && doc.linkedControls.length > 0 && (
                        <span className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400">
                          <LinkIcon className="h-3.5 w-3.5" />
                          {doc.linkedControls.length}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(doc.updatedAt).toLocaleDateString("ru-RU")}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/documents/${doc.id}`}
                          className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Просмотр"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </Link>
                        <button
                          className="p-1.5 text-gray-400 hover:text-green-600 transition-colors"
                          title="Скачать"
                        >
                          <ArrowDownTrayIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredDocuments.length === 0 && (
          <div className="py-12 text-center">
            <DocumentTextIcon className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600" />
            <p className="mt-4 text-gray-500 dark:text-gray-400">Документы не найдены</p>
          </div>
        )}
      </div>

      {/* Bulk Generate Modal */}
      {showBulkGenerate && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowBulkGenerate(false)} />
            <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Генерация пакета документов 152-ФЗ
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Будет создан полный пакет документов для соответствия 152-ФЗ «О персональных данных»:
              </p>
              <ul className="space-y-2 mb-6 text-sm text-gray-600 dark:text-gray-400">
                <li className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  8 Политик
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  6 Приказов
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  5 Журналов
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  3 Согласия
                </li>
              </ul>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowBulkGenerate(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                >
                  Отмена
                </button>
                <button
                  onClick={() => bulkGenerateMutation.mutate()}
                  disabled={bulkGenerateMutation.isPending}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 inline-flex items-center gap-2"
                >
                  {bulkGenerateMutation.isPending ? (
                    <>
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      Генерация...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4" />
                      Сгенерировать все
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
