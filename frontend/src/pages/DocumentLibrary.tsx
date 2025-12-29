import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useLanguage } from "../contexts/LanguageContext";
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


interface Company {
  id: string;
  legal_name: string;
  inn: string;
}

export default function DocumentLibrary() {
  const { language } = useLanguage();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | "all">("all");
  const [typeFilter, setTypeFilter] = useState<DocumentType | "all">("all");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [showBulkGenerate, setShowBulkGenerate] = useState(false);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string | null>(null);

  // Fetch companies for selector
  const { data: companies = [] } = useQuery({
    queryKey: ["companies"],
    queryFn: () => russianComplianceApi.companies.list(),
  });

  // Fetch documents for selected company
  const { data: documentsResponse, isLoading } = useQuery({
    queryKey: ["documents", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return { data: [] };
      return russianComplianceApi.documents.list(selectedCompanyId);
    },
    enabled: !!selectedCompanyId,
  });

  // Extract documents array from response
  const documentsData = documentsResponse?.data || [];

  // Bilingual translations
  const t = {
    title: language === "ru" ? "Библиотека документов" : "Document Library",
    subtitle: language === "ru"
      ? "Управление документами соответствия с версионированием и согласованием"
      : "Manage compliance documents with versioning and approval",
    generate152: language === "ru" ? "Сгенерировать пакет 152-ФЗ" : "Generate 152-FZ Package",
    total: language === "ru" ? "Всего" : "Total",
    approved: language === "ru" ? "Утверждено" : "Approved",
    drafts: language === "ru" ? "Черновики" : "Drafts",
    pendingReview: language === "ru" ? "На проверке" : "Pending Review",
    expired: language === "ru" ? "Истёк срок" : "Expired",
    searchPlaceholder: language === "ru" ? "Поиск по названию, коду или тегам..." : "Search by name, code, or tags...",
    allStatuses: language === "ru" ? "Все статусы" : "All Statuses",
    draft: language === "ru" ? "Черновик" : "Draft",
    onReview: language === "ru" ? "На проверке" : "On Review",
    approvedStatus: language === "ru" ? "Утверждён" : "Approved",
    expiredStatus: language === "ru" ? "Истёк срок" : "Expired",
    allTypes: language === "ru" ? "Все типы" : "All Types",
    policies: language === "ru" ? "Политики" : "Policies",
    orders: language === "ru" ? "Приказы" : "Orders",
    instructions: language === "ru" ? "Инструкции" : "Instructions",
    journals: language === "ru" ? "Журналы" : "Journals",
    forms: language === "ru" ? "Формы" : "Forms",
    selected: language === "ru" ? "Выбрано" : "Selected",
    approve: language === "ru" ? "Утвердить" : "Approve",
    export: language === "ru" ? "Экспортировать" : "Export",
    cancelSelection: language === "ru" ? "Отменить выбор" : "Cancel Selection",
    document: language === "ru" ? "Документ" : "Document",
    type: language === "ru" ? "Тип" : "Type",
    status: language === "ru" ? "Статус" : "Status",
    version: language === "ru" ? "Версия" : "Version",
    links: language === "ru" ? "Связи" : "Links",
    updated: language === "ru" ? "Обновлено" : "Updated",
    actions: language === "ru" ? "Действия" : "Actions",
    view: language === "ru" ? "Просмотр" : "View",
    download: language === "ru" ? "Скачать" : "Download",
    noDocuments: language === "ru" ? "Документы не найдены" : "No documents found",
    generateTitle: language === "ru" ? "Генерация пакета документов 152-ФЗ" : "Generate 152-FZ Document Package",
    generateDesc: language === "ru"
      ? "Будет создан полный пакет документов для соответствия 152-ФЗ «О персональных данных»:"
      : "A complete document package will be created for 152-FZ \"Personal Data\" compliance:",
    policiesCount: language === "ru" ? "8 Политик" : "8 Policies",
    ordersCount: language === "ru" ? "6 Приказов" : "6 Orders",
    journalsCount: language === "ru" ? "5 Журналов" : "5 Journals",
    consentsCount: language === "ru" ? "3 Согласия" : "3 Consents",
    cancel: language === "ru" ? "Отмена" : "Cancel",
    generating: language === "ru" ? "Генерация..." : "Generating...",
    generateAll: language === "ru" ? "Сгенерировать все" : "Generate All",
    archived: language === "ru" ? "Архив" : "Archived",
    // Status labels
    statusDraft: language === "ru" ? "Черновик" : "Draft",
    statusPending: language === "ru" ? "На проверке" : "Pending Review",
    statusApproved: language === "ru" ? "Утверждён" : "Approved",
    statusExpired: language === "ru" ? "Истёк срок" : "Expired",
    statusArchived: language === "ru" ? "Архив" : "Archived",
    // Document types
    typePolicy: language === "ru" ? "Политика" : "Policy",
    typeOrder: language === "ru" ? "Приказ" : "Order",
    typeInstruction: language === "ru" ? "Инструкция" : "Instruction",
    typeJournal: language === "ru" ? "Журнал" : "Journal",
    typeForm: language === "ru" ? "Форма" : "Form",
    typeAgreement: language === "ru" ? "Соглашение" : "Agreement",
  };

  // Bilingual status label getter
  const getStatusLabel = (status: DocumentStatus) => {
    const labels: Record<DocumentStatus, string> = {
      draft: t.statusDraft,
      pending_review: t.statusPending,
      approved: t.statusApproved,
      expired: t.statusExpired,
      archived: t.statusArchived,
    };
    return labels[status];
  };

  // Bilingual type label getter
  const getTypeLabel = (type: DocumentType) => {
    const labels: Record<DocumentType, string> = {
      policy: t.typePolicy,
      order: t.typeOrder,
      instruction: t.typeInstruction,
      journal: t.typeJournal,
      form: t.typeForm,
      agreement: t.typeAgreement,
    };
    return labels[type];
  };

  // Transform API documents to component format
  const documents: Document[] = useMemo(() => {
    if (!documentsData || !Array.isArray(documentsData)) return [];
    return documentsData.map((doc: {
      id: string;
      title: string;
      template_code?: string;
      document_type?: string;
      framework?: string;
      status?: string;
      version?: number;
      created_at?: string;
      updated_at?: string;
      approved_by?: string;
      approved_at?: string;
      expires_at?: string;
      linked_controls?: string[];
      linked_evidence?: string[];
      tags?: string[];
    }) => ({
      id: doc.id,
      title: doc.title,
      templateCode: doc.template_code || "",
      documentType: (doc.document_type || "policy") as DocumentType,
      framework: doc.framework || "152-ФЗ",
      status: (doc.status || "draft") as DocumentStatus,
      version: doc.version || 1,
      createdAt: doc.created_at || new Date().toISOString(),
      updatedAt: doc.updated_at || new Date().toISOString(),
      approvedBy: doc.approved_by,
      approvedAt: doc.approved_at,
      expiresAt: doc.expires_at,
      linkedControls: doc.linked_controls,
      linkedEvidence: doc.linked_evidence,
      tags: doc.tags,
    }));
  }, [documentsData]);

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

  // Bulk approve mutation
  const bulkApproveMutation = useMutation({
    mutationFn: async (docIds: string[]) => {
      if (!selectedCompanyId) throw new Error("No company selected");
      return Promise.all(
        docIds.map((id) =>
          russianComplianceApi.documents.update(selectedCompanyId, id, { status: "approved" })
        )
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", selectedCompanyId] });
      setSelectedDocs([]);
    },
  });

  // Bulk export - download documents
  const handleBulkExport = async () => {
    if (!selectedCompanyId) return;
    for (const docId of selectedDocs) {
      try {
        const response = await russianComplianceApi.documents.get(selectedCompanyId, docId);
        // Open document in new tab or trigger download
        if (response?.data?.download_url) {
          window.open(response.data.download_url, "_blank");
        }
      } catch (error) {
        console.error(`Failed to export document ${docId}:`, error);
      }
    }
    setSelectedDocs([]);
  };

  // Handle bulk approve
  const handleBulkApprove = () => {
    if (selectedDocs.length > 0) {
      bulkApproveMutation.mutate(selectedDocs);
    }
  };

  // Bulk document generation - generates full 152-FZ package
  const bulkGenerateMutation = useMutation({
    mutationFn: async () => {
      if (!selectedCompanyId) throw new Error("No company selected");
      return russianComplianceApi.tasks.generateFromTemplate(selectedCompanyId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", selectedCompanyId] });
      setShowBulkGenerate(false);
    },
  });

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
          {/* Company Selector */}
          <select
            value={selectedCompanyId || ""}
            onChange={(e) => setSelectedCompanyId(e.target.value || null)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">{language === "ru" ? "Выберите компанию" : "Select Company"}</option>
            {(companies as Company[]).map((company) => (
              <option key={company.id} value={company.id}>
                {company.legal_name} ({company.inn})
              </option>
            ))}
          </select>
          <button
            onClick={() => setShowBulkGenerate(true)}
            disabled={!selectedCompanyId}
            className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SparklesIcon className="h-5 w-5 mr-2" />
            {t.generate152}
          </button>
        </div>
      </div>

      {/* No company selected message */}
      {!selectedCompanyId && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 text-center">
          <DocumentTextIcon className="h-12 w-12 mx-auto text-blue-400" />
          <h3 className="mt-4 text-lg font-medium text-blue-900 dark:text-blue-100">
            {language === "ru" ? "Выберите компанию" : "Select a Company"}
          </h3>
          <p className="mt-2 text-sm text-blue-600 dark:text-blue-300">
            {language === "ru"
              ? "Выберите компанию из списка выше, чтобы просмотреть её документы"
              : "Select a company from the dropdown above to view its documents"}
          </p>
        </div>
      )}

      {/* Stats - only show when company selected */}
      {selectedCompanyId && (
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
      )}

      {/* Search and Filters - only when company selected */}
      {selectedCompanyId && (
      <>
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

        {filteredDocuments.length === 0 && !isLoading && (
          <div className="py-12 text-center">
            <DocumentTextIcon className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600" />
            <p className="mt-4 text-gray-500 dark:text-gray-400">{t.noDocuments}</p>
          </div>
        )}

        {isLoading && (
          <div className="py-12 text-center">
            <ArrowPathIcon className="h-8 w-8 mx-auto text-blue-500 animate-spin" />
            <p className="mt-4 text-gray-500 dark:text-gray-400">
              {language === "ru" ? "Загрузка документов..." : "Loading documents..."}
            </p>
          </div>
        )}
      </div>
      </>
      )}

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
