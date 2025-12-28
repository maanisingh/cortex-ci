import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { risksApi } from "../services/api";
import Modal from "../components/common/Modal";
import { useLanguage } from "../contexts/LanguageContext";

// Types
interface RiskRegisterItem {
  id: string;
  risk_id: string;
  title: string;
  description: string | null;
  category: string;
  status: string;
  likelihood: number;
  impact: number;
  inherent_risk_score: number | null;
  inherent_risk_level: string | null;
  residual_likelihood: number | null;
  residual_impact: number | null;
  residual_risk_score: number | null;
  residual_risk_level: string | null;
  treatment: string;
  treatment_plan: string | null;
  risk_owner_name: string | null;
  entity_id: string | null;
  exceeds_appetite: boolean;
  identified_date: string;
  review_date: string | null;
  tags: string[] | null;
  created_at: string;
}

interface RiskSummary {
  total_risks: number;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
  by_level: Record<string, number>;
  exceeds_appetite_count: number;
  overdue_review_count: number;
  average_inherent_score: number;
  average_residual_score: number | null;
}

const categories = [
  "STRATEGIC",
  "OPERATIONAL",
  "FINANCIAL",
  "COMPLIANCE",
  "TECHNOLOGY",
  "REPUTATIONAL",
  "LEGAL",
  "CYBER",
  "THIRD_PARTY",
  "OTHER",
];

const statuses = ["DRAFT", "OPEN", "IN_TREATMENT", "CLOSED", "ACCEPTED"];

const treatments = ["ACCEPT", "MITIGATE", "TRANSFER", "AVOID", "MONITOR"];

const riskLevelColors: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800 border-red-200",
  HIGH: "bg-orange-100 text-orange-800 border-orange-200",
  MEDIUM: "bg-yellow-100 text-yellow-800 border-yellow-200",
  LOW: "bg-green-100 text-green-800 border-green-200",
};

const statusColors: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-800",
  OPEN: "bg-blue-100 text-blue-800",
  IN_TREATMENT: "bg-purple-100 text-purple-800",
  CLOSED: "bg-green-100 text-green-800",
  ACCEPTED: "bg-amber-100 text-amber-800",
};

const categoryColors: Record<string, string> = {
  STRATEGIC: "bg-indigo-100 text-indigo-800",
  OPERATIONAL: "bg-blue-100 text-blue-800",
  FINANCIAL: "bg-emerald-100 text-emerald-800",
  COMPLIANCE: "bg-violet-100 text-violet-800",
  TECHNOLOGY: "bg-cyan-100 text-cyan-800",
  REPUTATIONAL: "bg-pink-100 text-pink-800",
  LEGAL: "bg-amber-100 text-amber-800",
  CYBER: "bg-red-100 text-red-800",
  THIRD_PARTY: "bg-orange-100 text-orange-800",
  OTHER: "bg-gray-100 text-gray-800",
};

export default function Risks() {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editRisk, setEditRisk] = useState<RiskRegisterItem | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch risk register summary
  const { data: summary } = useQuery<RiskSummary>({
    queryKey: ["risk-register-summary"],
    queryFn: async () => {
      const response = await risksApi.register.summary();
      return response.data;
    },
  });

  // Fetch risk register list
  const { data: risksData, isLoading } = useQuery({
    queryKey: ["risk-register", search, categoryFilter, statusFilter],
    queryFn: async () => {
      const response = await risksApi.register.list({
        search: search || undefined,
        category: categoryFilter || undefined,
        status: statusFilter || undefined,
        page_size: 50,
      });
      return response.data;
    },
  });

  const risks = risksData?.items || [];

  // Risk matrix helper
  const getRiskMatrixColor = (likelihood: number, impact: number) => {
    const score = likelihood * impact;
    if (score >= 20) return "bg-red-500";
    if (score >= 12) return "bg-orange-500";
    if (score >= 6) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {t("riskRegister")}
          </h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            {t("riskRegisterDescription")}
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="btn-primary"
            onClick={() => {
              setEditRisk(null);
              setShowForm(true);
            }}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            {t("addRisk")}
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="card bg-white dark:bg-dark-800">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-4">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {t("totalRisks")}
              </dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {summary?.total_risks || 0}
              </dd>
            </div>
          </div>
        </div>

        <div className="card bg-white dark:bg-dark-800 border-l-4 border-red-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <XMarkIcon className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-4">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {t("exceedsAppetite")}
              </dt>
              <dd className="mt-1 text-2xl font-semibold text-red-600">
                {summary?.exceeds_appetite_count || 0}
              </dd>
            </div>
          </div>
        </div>

        <div className="card bg-white dark:bg-dark-800 border-l-4 border-orange-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-4">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {t("overdueReviews")}
              </dt>
              <dd className="mt-1 text-2xl font-semibold text-orange-600">
                {summary?.overdue_review_count || 0}
              </dd>
            </div>
          </div>
        </div>

        <div className="card bg-white dark:bg-dark-800">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {t("avgRiskScore")}
              </dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                {summary?.average_inherent_score?.toFixed(1) || "0.0"}
              </dd>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Level Breakdown */}
      {summary?.by_level && Object.keys(summary.by_level).length > 0 && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((level) => (
            <div
              key={level}
              className={`p-4 rounded-lg border-2 ${riskLevelColors[level]}`}
            >
              <div className="text-xs font-semibold uppercase">{level}</div>
              <div className="text-2xl font-bold mt-1">
                {summary.by_level[level] || 0}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchRisks")}
            className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-dark-700 dark:border-dark-600 dark:text-gray-100"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-secondary flex items-center ${showFilters ? "bg-primary-100" : ""}`}
        >
          <FunnelIcon className="h-5 w-5 mr-2" />
          {t("filters")}
          {(categoryFilter || statusFilter) && (
            <span className="ml-2 bg-primary-500 text-white text-xs rounded-full px-2 py-0.5">
              {(categoryFilter ? 1 : 0) + (statusFilter ? 1 : 0)}
            </span>
          )}
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-600">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t("category")}
              </label>
              <select
                value={categoryFilter || ""}
                onChange={(e) => setCategoryFilter(e.target.value || null)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-dark-700 dark:border-dark-600"
              >
                <option value="">{t("allCategories")}</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t("status")}
              </label>
              <select
                value={statusFilter || ""}
                onChange={(e) => setStatusFilter(e.target.value || null)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-dark-700 dark:border-dark-600"
              >
                <option value="">{t("allStatuses")}</option>
                {statuses.map((status) => (
                  <option key={status} value={status}>
                    {status.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {(categoryFilter || statusFilter) && (
            <button
              onClick={() => {
                setCategoryFilter(null);
                setStatusFilter(null);
              }}
              className="mt-3 text-sm text-primary-600 hover:text-primary-800"
            >
              {t("clearAllFilters")}
            </button>
          )}
        </div>
      )}

      {/* Risk Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-600">
            <thead className="bg-gray-50 dark:bg-dark-700">
              <tr>
                <th className="table-header">{t("riskId")}</th>
                <th className="table-header">{t("title")}</th>
                <th className="table-header">{t("category")}</th>
                <th className="table-header">{t("status")}</th>
                <th className="table-header">{t("riskMatrix")}</th>
                <th className="table-header">{t("inherentLevel")}</th>
                <th className="table-header">{t("residualLevel")}</th>
                <th className="table-header">{t("treatment")}</th>
                <th className="table-header">{t("owner")}</th>
                <th className="table-header">{t("actions")}</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-dark-800 divide-y divide-gray-200 dark:divide-dark-600">
              {isLoading ? (
                <tr>
                  <td colSpan={10} className="px-6 py-4 text-center text-gray-500">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-2"></div>
                      {t("loadingRisks")}
                    </div>
                  </td>
                </tr>
              ) : risks.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-6 py-4 text-center text-gray-500">
                    {t("noRisksFound")}
                  </td>
                </tr>
              ) : (
                risks.map((risk: RiskRegisterItem) => (
                  <tr key={risk.id} className="hover:bg-gray-50 dark:hover:bg-dark-700">
                    <td className="table-cell">
                      <span className="font-mono text-sm text-primary-600">
                        {risk.risk_id}
                      </span>
                      {risk.exceeds_appetite && (
                        <ExclamationTriangleIcon
                          className="h-4 w-4 text-red-500 inline ml-1"
                          title="Exceeds risk appetite"
                        />
                      )}
                    </td>
                    <td className="table-cell">
                      <Link
                        to={`/risks/${risk.id}`}
                        className="font-medium text-gray-900 dark:text-gray-100 hover:text-primary-600"
                      >
                        {risk.title}
                      </Link>
                      {risk.description && (
                        <p className="text-xs text-gray-500 truncate max-w-xs">
                          {risk.description}
                        </p>
                      )}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${categoryColors[risk.category] || "bg-gray-100"}`}
                      >
                        {risk.category.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${statusColors[risk.status] || "bg-gray-100"}`}
                      >
                        {risk.status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center space-x-1">
                        <div
                          className={`w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold ${getRiskMatrixColor(risk.likelihood, risk.impact)}`}
                          title={`Likelihood: ${risk.likelihood}, Impact: ${risk.impact}`}
                        >
                          {risk.likelihood * risk.impact}
                        </div>
                        <span className="text-xs text-gray-500">
                          ({risk.likelihood}x{risk.impact})
                        </span>
                      </div>
                    </td>
                    <td className="table-cell">
                      {risk.inherent_risk_level ? (
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${riskLevelColors[risk.inherent_risk_level]}`}
                        >
                          {risk.inherent_risk_level}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="table-cell">
                      {risk.residual_risk_level ? (
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${riskLevelColors[risk.residual_risk_level]}`}
                        >
                          {risk.residual_risk_level}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="table-cell text-sm capitalize">
                      {risk.treatment.toLowerCase()}
                    </td>
                    <td className="table-cell text-sm text-gray-500">
                      {risk.risk_owner_name || "-"}
                    </td>
                    <td className="table-cell">
                      <button
                        onClick={() => {
                          setEditRisk(risk);
                          setShowForm(true);
                        }}
                        className="text-primary-600 hover:text-primary-900 text-sm"
                      >
                        {t("edit")}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Risk Modal */}
      <RiskFormModal
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setEditRisk(null);
        }}
        risk={editRisk}
      />
    </div>
  );
}

// Risk Form Modal Component
function RiskFormModal({
  isOpen,
  onClose,
  risk,
}: {
  isOpen: boolean;
  onClose: () => void;
  risk: RiskRegisterItem | null;
}) {
  const queryClient = useQueryClient();
  const isEdit = !!risk;

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "OPERATIONAL",
    status: "DRAFT",
    likelihood: 3,
    impact: 3,
    residual_likelihood: null as number | null,
    residual_impact: null as number | null,
    treatment: "MONITOR",
    treatment_plan: "",
    risk_owner_name: "",
    risk_appetite_threshold: null as number | null,
    review_date: "",
    source: "",
    tags: "",
  });

  const [error, setError] = useState("");

  // Reset form when modal opens
  useState(() => {
    if (risk) {
      setFormData({
        title: risk.title,
        description: risk.description || "",
        category: risk.category,
        status: risk.status,
        likelihood: risk.likelihood,
        impact: risk.impact,
        residual_likelihood: risk.residual_likelihood,
        residual_impact: risk.residual_impact,
        treatment: risk.treatment,
        treatment_plan: risk.treatment_plan || "",
        risk_owner_name: risk.risk_owner_name || "",
        risk_appetite_threshold: null,
        review_date: risk.review_date?.split("T")[0] || "",
        source: "",
        tags: risk.tags?.join(", ") || "",
      });
    } else {
      setFormData({
        title: "",
        description: "",
        category: "OPERATIONAL",
        status: "DRAFT",
        likelihood: 3,
        impact: 3,
        residual_likelihood: null,
        residual_impact: null,
        treatment: "MONITOR",
        treatment_plan: "",
        risk_owner_name: "",
        risk_appetite_threshold: null,
        review_date: "",
        source: "",
        tags: "",
      });
    }
    setError("");
  });

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => risksApi.register.create(data as any),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risk-register"] });
      queryClient.invalidateQueries({ queryKey: ["risk-register-summary"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to create risk");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      risksApi.register.update(risk!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risk-register"] });
      queryClient.invalidateQueries({ queryKey: ["risk-register-summary"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to update risk");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      ...formData,
      tags: formData.tags
        ? formData.tags.split(",").map((t) => t.trim()).filter(Boolean)
        : [],
      review_date: formData.review_date || null,
      description: formData.description || null,
      treatment_plan: formData.treatment_plan || null,
      risk_owner_name: formData.risk_owner_name || null,
      source: formData.source || null,
    };

    if (isEdit) {
      updateMutation.mutate(payload);
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "number" ? (value ? parseInt(value) : null) : value,
    }));
  };

  const inherentScore = formData.likelihood * formData.impact * 4;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Risk" : "Add New Risk"}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Brief risk title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Detailed description of the risk"
            />
          </div>

          {/* Risk Assessment */}
          <div className="col-span-2 border-t pt-4 mt-2">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Inherent Risk Assessment
            </h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Likelihood (1-5)
                </label>
                <select
                  name="likelihood"
                  value={formData.likelihood}
                  onChange={handleChange}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n} - {["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"][n - 1]}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Impact (1-5)
                </label>
                <select
                  name="impact"
                  value={formData.impact}
                  onChange={handleChange}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n} - {["Negligible", "Minor", "Moderate", "Major", "Severe"][n - 1]}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Inherent Score
                </label>
                <div
                  className={`p-2 rounded text-center font-bold text-white ${
                    inherentScore >= 80
                      ? "bg-red-500"
                      : inherentScore >= 60
                        ? "bg-orange-500"
                        : inherentScore >= 40
                          ? "bg-yellow-500"
                          : "bg-green-500"
                  }`}
                >
                  {inherentScore}
                </div>
              </div>
            </div>
          </div>

          {/* Treatment */}
          <div className="col-span-2 border-t pt-4 mt-2">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Risk Treatment
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Treatment Strategy
                </label>
                <select
                  name="treatment"
                  value={formData.treatment}
                  onChange={handleChange}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  {treatments.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Risk Owner
                </label>
                <input
                  type="text"
                  name="risk_owner_name"
                  value={formData.risk_owner_name}
                  onChange={handleChange}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  placeholder="Person responsible"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Treatment Plan
                </label>
                <textarea
                  name="treatment_plan"
                  value={formData.treatment_plan}
                  onChange={handleChange}
                  rows={2}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  placeholder="Describe the treatment actions..."
                />
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Review Date
            </label>
            <input
              type="date"
              name="review_date"
              value={formData.review_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source
            </label>
            <input
              type="text"
              name="source"
              value={formData.source}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., Audit, Assessment"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., critical, Q1-2025, IT"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending || updateMutation.isPending}
            className="btn-primary"
          >
            {createMutation.isPending || updateMutation.isPending
              ? "Saving..."
              : isEdit
                ? "Update Risk"
                : "Create Risk"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
