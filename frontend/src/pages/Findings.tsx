import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { auditsApi } from "../services/api";
import {
  ListBulletIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";

interface Finding {
  id: string;
  audit_id: string;
  finding_ref: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  recommendation?: string;
  root_cause?: string;
  impact?: string;
  management_response?: string;
  target_remediation_date?: string;
  actual_remediation_date?: string;
  owner_department?: string;
  is_repeat: boolean;
  created_at?: string;
  audit_title?: string;
}

interface FindingSummary {
  total_open: number;
  critical_open: number;
  high_open: number;
  medium_open: number;
  low_open: number;
  overdue: number;
  pending_validation: number;
  closed_this_month: number;
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
  avg_days_to_close: number | null;
}

const SEVERITY_CONFIG: Record<string, { label: string; color: string; icon: typeof ExclamationCircleIcon; dotColor: string }> = {
  CRITICAL: {
    label: "Critical",
    color: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400",
    icon: ExclamationCircleIcon,
    dotColor: "bg-red-500",
  },
  HIGH: {
    label: "High",
    color: "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400",
    icon: ExclamationTriangleIcon,
    dotColor: "bg-orange-500",
  },
  MEDIUM: {
    label: "Medium",
    color: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400",
    icon: InformationCircleIcon,
    dotColor: "bg-amber-500",
  },
  LOW: {
    label: "Low",
    color: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400",
    icon: InformationCircleIcon,
    dotColor: "bg-green-500",
  },
};

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  OPEN: { label: "Open", color: "text-red-600 bg-red-50 dark:bg-red-900/30" },
  IN_PROGRESS: { label: "In Progress", color: "text-amber-600 bg-amber-50 dark:bg-amber-900/30" },
  PENDING_VALIDATION: { label: "Pending Validation", color: "text-blue-600 bg-blue-50 dark:bg-blue-900/30" },
  CLOSED: { label: "Closed", color: "text-green-600 bg-green-50 dark:bg-green-900/30" },
};

function FindingDetailModal({
  finding,
  onClose,
}: {
  finding: Finding;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [responseText, setResponseText] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [verificationNotes, setVerificationNotes] = useState("");

  const respondMutation = useMutation({
    mutationFn: () => auditsApi.findings.respond(finding.id, responseText, targetDate || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["findings"] });
      setResponseText("");
      setTargetDate("");
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => auditsApi.findings.close(finding.id, verificationNotes || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["findings"] });
      onClose();
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: (newStatus: string) => auditsApi.findings.updateStatus(finding.id, newStatus),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["findings"] });
    },
  });

  const severityConfig = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.MEDIUM;
  const statusConfig = STATUS_CONFIG[finding.status] || STATUS_CONFIG.OPEN;
  const SeverityIcon = severityConfig.icon;
  const isOverdue =
    finding.status !== "CLOSED" &&
    finding.target_remediation_date &&
    new Date(finding.target_remediation_date) < new Date();

  const daysOpen = finding.created_at
    ? Math.floor((Date.now() - new Date(finding.created_at).getTime()) / (1000 * 60 * 60 * 24))
    : 0;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-dark-800 rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b dark:border-dark-700 flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className={`p-2 rounded-lg ${severityConfig.color}`}>
              <SeverityIcon className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono text-gray-500">{finding.finding_ref}</span>
                {isOverdue && (
                  <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded dark:bg-red-900/30 dark:text-red-400">
                    Overdue
                  </span>
                )}
                {finding.is_repeat && (
                  <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded dark:bg-purple-900/30 dark:text-purple-400">
                    Repeat Finding
                  </span>
                )}
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                {finding.title}
              </h2>
              <p className="text-sm text-gray-500 mt-1">From: {finding.audit_title || "Unknown Audit"}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Status & Severity */}
          <div className="flex items-center space-x-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${severityConfig.color}`}>
              {severityConfig.label} Severity
            </span>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusConfig.color}`}>
              {statusConfig.label}
            </span>
            {finding.status !== "CLOSED" && (
              <select
                value={finding.status}
                onChange={(e) => updateStatusMutation.mutate(e.target.value)}
                className="text-sm border rounded-md px-2 py-1 dark:bg-dark-700 dark:border-dark-600"
              >
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="PENDING_VALIDATION">Pending Validation</option>
              </select>
            )}
          </div>

          {/* Key Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-gray-500">Owner</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">{finding.owner_department || "Unassigned"}</p>
            </div>
            <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-gray-500">Target Date</p>
              <p className={`font-medium ${isOverdue ? "text-red-600" : "text-gray-900 dark:text-gray-100"}`}>
                {finding.target_remediation_date
                  ? new Date(finding.target_remediation_date).toLocaleDateString()
                  : "Not set"}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-gray-500">Days Open</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">{daysOpen}</p>
            </div>
            <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-3">
              <p className="text-xs text-gray-500">Created</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {finding.created_at ? new Date(finding.created_at).toLocaleDateString() : "Unknown"}
              </p>
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Description</h4>
            <p className="text-gray-600 dark:text-gray-400">{finding.description}</p>
          </div>

          {/* Root Cause & Impact */}
          {(finding.root_cause || finding.impact) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {finding.root_cause && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Root Cause</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">{finding.root_cause}</p>
                </div>
              )}
              {finding.impact && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Impact</h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">{finding.impact}</p>
                </div>
              )}
            </div>
          )}

          {/* Recommendation */}
          {finding.recommendation && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Recommendation</h4>
              <p className="text-gray-600 dark:text-gray-400">{finding.recommendation}</p>
            </div>
          )}

          {/* Management Response */}
          {finding.management_response && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-2 flex items-center">
                <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2" />
                Management Response
              </h4>
              <p className="text-blue-800 dark:text-blue-300 text-sm">{finding.management_response}</p>
            </div>
          )}

          {/* Add Management Response */}
          {finding.status !== "CLOSED" && !finding.management_response && (
            <div className="border-t pt-4 dark:border-dark-700">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2" />
                Add Management Response
              </h4>
              <textarea
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                placeholder="Enter management response..."
                rows={3}
                className="w-full rounded-lg border-gray-300 dark:border-dark-600 dark:bg-dark-700 mb-3"
              />
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <label className="text-xs text-gray-500">Updated Target Date (optional)</label>
                  <input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    className="w-full rounded-md border-gray-300 dark:border-dark-600 dark:bg-dark-700"
                  />
                </div>
                <button
                  onClick={() => respondMutation.mutate()}
                  disabled={!responseText || respondMutation.isPending}
                  className="btn-primary mt-5"
                >
                  {respondMutation.isPending ? "Saving..." : "Submit Response"}
                </button>
              </div>
            </div>
          )}

          {/* Close Finding */}
          {finding.status === "PENDING_VALIDATION" && (
            <div className="border-t pt-4 dark:border-dark-700">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                <CheckCircleIcon className="h-4 w-4 mr-2" />
                Verify & Close Finding
              </h4>
              <textarea
                value={verificationNotes}
                onChange={(e) => setVerificationNotes(e.target.value)}
                placeholder="Verification notes (optional)..."
                rows={2}
                className="w-full rounded-lg border-gray-300 dark:border-dark-600 dark:bg-dark-700 mb-3"
              />
              <button
                onClick={() => closeMutation.mutate()}
                disabled={closeMutation.isPending}
                className="btn-primary bg-green-600 hover:bg-green-700"
              >
                {closeMutation.isPending ? "Closing..." : "Close Finding"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Findings() {
  const queryClient = useQueryClient();
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["findings", "summary"],
    queryFn: async () => {
      const response = await auditsApi.findings.summary();
      return response.data as FindingSummary;
    },
  });

  const { data: findingsData, isLoading: findingsLoading, refetch } = useQuery({
    queryKey: ["findings", "all", { severity: severityFilter, status: statusFilter, search: searchTerm, page }],
    queryFn: async () => {
      const response = await auditsApi.findings.listAll({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        search: searchTerm || undefined,
        page,
        page_size: 20,
      });
      return response.data as { items: Finding[]; total: number; page: number; page_size: number };
    },
  });

  const { data: overdueFindings } = useQuery({
    queryKey: ["findings", "overdue"],
    queryFn: async () => {
      const response = await auditsApi.findings.overdue();
      return response.data as Finding[];
    },
  });

  const findings = findingsData?.items || [];
  const totalPages = findingsData ? Math.ceil(findingsData.total / findingsData.page_size) : 1;

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
            <ListBulletIcon className="h-8 w-8 mr-3 text-orange-600" />
            Findings & Issues
          </h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Track and remediate audit findings and compliance issues.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="mt-4 sm:mt-0 btn-secondary flex items-center"
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Open Findings</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {summaryLoading ? "..." : summary?.total_open || 0}
              </p>
            </div>
            <div className="p-3 bg-gray-100 dark:bg-dark-700 rounded-lg">
              <ListBulletIcon className="h-6 w-6 text-gray-600 dark:text-gray-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-red-200 dark:border-red-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Critical/High</p>
              <p className="text-2xl font-bold text-red-600">
                {summaryLoading ? "..." : (summary?.critical_open || 0) + (summary?.high_open || 0)}
              </p>
            </div>
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <ExclamationCircleIcon className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-amber-200 dark:border-amber-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Overdue</p>
              <p className="text-2xl font-bold text-amber-600">
                {summaryLoading ? "..." : summary?.overdue || 0}
              </p>
            </div>
            <div className="p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <ClockIcon className="h-6 w-6 text-amber-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-blue-200 dark:border-blue-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Pending Validation</p>
              <p className="text-2xl font-bold text-blue-600">
                {summaryLoading ? "..." : summary?.pending_validation || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-green-200 dark:border-green-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Closed This Month</p>
              <p className="text-2xl font-bold text-green-600">
                {summaryLoading ? "..." : summary?.closed_this_month || 0}
              </p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Overdue Alert */}
      {overdueFindings && overdueFindings.length > 0 && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start">
            <ExclamationCircleIcon className="h-5 w-5 text-red-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-semibold text-red-800 dark:text-red-400">
                {overdueFindings.length} Overdue Finding{overdueFindings.length > 1 ? "s" : ""} Require Attention
              </h3>
              <ul className="mt-2 space-y-1">
                {overdueFindings.slice(0, 3).map((f) => (
                  <li key={f.id} className="text-sm text-red-700 dark:text-red-300">
                    <button
                      onClick={() => setSelectedFinding(f)}
                      className="hover:underline text-left"
                    >
                      {f.finding_ref}: {f.title} - Due {f.target_remediation_date ? new Date(f.target_remediation_date).toLocaleDateString() : "N/A"}
                    </button>
                  </li>
                ))}
                {overdueFindings.length > 3 && (
                  <li className="text-sm text-red-600 dark:text-red-400">
                    +{overdueFindings.length - 3} more overdue findings
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Average Days to Close */}
      {summary?.avg_days_to_close && (
        <div className="mb-6 bg-gray-50 dark:bg-dark-700 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center">
            <ClockIcon className="h-5 w-5 text-gray-500 mr-2" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Average Time to Close</span>
          </div>
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {Math.round(summary.avg_days_to_close)} days
          </span>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="relative flex-1 min-w-[200px]">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search findings..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-dark-600 rounded-md focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 dark:bg-dark-700"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => {
            setSeverityFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 dark:border-dark-600 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 dark:bg-dark-700"
        >
          <option value="">All Severities</option>
          {Object.entries(SEVERITY_CONFIG).map(([key, config]) => (
            <option key={key} value={key}>
              {config.label}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 dark:border-dark-600 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 dark:bg-dark-700"
        >
          <option value="">All Statuses</option>
          {Object.entries(STATUS_CONFIG).map(([key, config]) => (
            <option key={key} value={key}>
              {config.label}
            </option>
          ))}
        </select>
      </div>

      {/* Findings List */}
      {findingsLoading ? (
        <div className="bg-white dark:bg-dark-800 shadow-sm rounded-lg p-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading findings...</p>
        </div>
      ) : findings.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-dark-800 rounded-lg shadow-sm">
          <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            No findings match your filters
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filter criteria.
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-dark-800 shadow-sm rounded-lg overflow-hidden">
          <div className="divide-y divide-gray-200 dark:divide-dark-700">
            {findings.map((finding) => {
              const severityConfig = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.MEDIUM;
              const statusConfig = STATUS_CONFIG[finding.status] || STATUS_CONFIG.OPEN;
              const SeverityIcon = severityConfig.icon;
              const isOverdue =
                finding.status !== "CLOSED" &&
                finding.target_remediation_date &&
                new Date(finding.target_remediation_date) < new Date();
              const daysOpen = finding.created_at
                ? Math.floor((Date.now() - new Date(finding.created_at).getTime()) / (1000 * 60 * 60 * 24))
                : 0;

              return (
                <div
                  key={finding.id}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-dark-700 cursor-pointer transition-colors"
                  onClick={() => setSelectedFinding(finding)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className={`p-2 rounded-lg ${severityConfig.color}`}>
                        <SeverityIcon className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono text-gray-400">{finding.finding_ref}</span>
                          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                            {finding.title}
                          </h3>
                          {isOverdue && (
                            <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-medium rounded dark:bg-red-900/30 dark:text-red-400">
                              Overdue
                            </span>
                          )}
                          {finding.is_repeat && (
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded dark:bg-purple-900/30 dark:text-purple-400">
                              Repeat
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                          {finding.description}
                        </p>
                        <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                          <span>From: {finding.audit_title || "Unknown"}</span>
                          <span>•</span>
                          <span>Owner: {finding.owner_department || "Unassigned"}</span>
                          <span>•</span>
                          <span>
                            Due:{" "}
                            {finding.target_remediation_date
                              ? new Date(finding.target_remediation_date).toLocaleDateString()
                              : "Not set"}
                          </span>
                          {finding.status !== "CLOSED" && (
                            <>
                              <span>•</span>
                              <span>{daysOpen} days open</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityConfig.color}`}
                      >
                        {severityConfig.label}
                      </span>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.color}`}
                      >
                        {statusConfig.label}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t dark:border-dark-700 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, findingsData?.total || 0)} of {findingsData?.total || 0} findings
              </p>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed dark:border-dark-600"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed dark:border-dark-600"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Finding Detail Modal */}
      {selectedFinding && (
        <FindingDetailModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
        />
      )}
    </div>
  );
}
