import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  MagnifyingGlassCircleIcon,
  PlusIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  PlayCircleIcon,
  XCircleIcon,
  EyeIcon,
  TrashIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { auditsApi } from "../services/api";
import Modal from "../components/common/Modal";

// Types
interface Audit {
  id: string;
  audit_ref: string;
  title: string;
  description: string | null;
  audit_type: string;
  status: string;
  scope_description: string | null;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  overall_rating: string | null;
  created_at: string;
}

interface Finding {
  id: string;
  audit_id: string;
  finding_ref: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  recommendation: string | null;
  root_cause: string | null;
  impact: string | null;
  management_response: string | null;
  target_remediation_date: string | null;
  owner_department: string | null;
  is_repeat: boolean;
  created_at: string;
}

interface AuditSummary {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  in_progress: number;
  completed_this_year: number;
  total_open_findings: number;
}

const AUDIT_TYPES = ["INTERNAL", "EXTERNAL", "REGULATORY", "CERTIFICATION", "SOC2_TYPE1", "SOC2_TYPE2", "ISO27001", "PCI_DSS"];

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  PLANNED: { label: "Planned", color: "bg-blue-100 text-blue-800", icon: CalendarIcon },
  IN_PROGRESS: { label: "In Progress", color: "bg-amber-100 text-amber-800", icon: PlayCircleIcon },
  FIELDWORK_COMPLETE: { label: "Fieldwork Complete", color: "bg-purple-100 text-purple-800", icon: ClockIcon },
  DRAFT_REPORT: { label: "Draft Report", color: "bg-indigo-100 text-indigo-800", icon: ClockIcon },
  FINAL_REPORT: { label: "Final Report", color: "bg-teal-100 text-teal-800", icon: CheckCircleIcon },
  REMEDIATION: { label: "Remediation", color: "bg-orange-100 text-orange-800", icon: ExclamationTriangleIcon },
  CLOSED: { label: "Closed", color: "bg-green-100 text-green-800", icon: CheckCircleIcon },
  CANCELLED: { label: "Cancelled", color: "bg-gray-100 text-gray-500", icon: XCircleIcon },
};

const SEVERITY_CONFIG: Record<string, { label: string; color: string }> = {
  CRITICAL: { label: "Critical", color: "bg-red-100 text-red-800" },
  HIGH: { label: "High", color: "bg-orange-100 text-orange-800" },
  MEDIUM: { label: "Medium", color: "bg-yellow-100 text-yellow-800" },
  LOW: { label: "Low", color: "bg-blue-100 text-blue-800" },
  INFORMATIONAL: { label: "Info", color: "bg-gray-100 text-gray-800" },
};

export default function Audits() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [viewAudit, setViewAudit] = useState<Audit | null>(null);
  const [page, setPage] = useState(1);

  // Fetch summary
  const { data: summary } = useQuery<AuditSummary>({
    queryKey: ["audits-summary"],
    queryFn: async () => {
      const res = await auditsApi.summary();
      return res.data;
    },
  });

  // Fetch audits list
  const { data: auditsData, isLoading } = useQuery({
    queryKey: ["audits", page, statusFilter, typeFilter],
    queryFn: async () => {
      const res = await auditsApi.list({
        page,
        page_size: 20,
        status: statusFilter || undefined,
        audit_type: typeFilter || undefined,
      });
      return res.data;
    },
  });

  // Fetch open findings
  const { data: openFindings } = useQuery<Finding[]>({
    queryKey: ["findings-open"],
    queryFn: async () => {
      const res = await auditsApi.findings.open();
      return res.data;
    },
  });

  // Fetch overdue findings
  const { data: overdueFindings } = useQuery<Finding[]>({
    queryKey: ["findings-overdue"],
    queryFn: async () => {
      const res = await auditsApi.findings.overdue();
      return res.data;
    },
  });

  // Start audit mutation
  const startMutation = useMutation({
    mutationFn: (id: string) => auditsApi.start(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      queryClient.invalidateQueries({ queryKey: ["audits-summary"] });
    },
  });

  // Complete audit mutation
  const completeMutation = useMutation({
    mutationFn: (id: string) => auditsApi.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      queryClient.invalidateQueries({ queryKey: ["audits-summary"] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => auditsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      queryClient.invalidateQueries({ queryKey: ["audits-summary"] });
    },
  });

  const auditsList = auditsData?.items || [];
  const totalPages = auditsData ? Math.ceil(auditsData.total / 20) : 0;

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
            <MagnifyingGlassCircleIcon className="h-8 w-8 mr-3 text-green-600" />
            Audit Management
          </h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Plan, execute, and track internal and external audits across your organization.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Audit
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 p-4">
          <div className="text-sm text-gray-500">Total Audits</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{summary?.total || 0}</div>
        </div>
        <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg shadow-sm border border-amber-200 dark:border-amber-800 p-4">
          <div className="text-sm text-amber-600">In Progress</div>
          <div className="text-2xl font-bold text-amber-700">{summary?.in_progress || 0}</div>
        </div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg shadow-sm border border-green-200 dark:border-green-800 p-4">
          <div className="text-sm text-green-600">Completed (Year)</div>
          <div className="text-2xl font-bold text-green-700">{summary?.completed_this_year || 0}</div>
        </div>
        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg shadow-sm border border-red-200 dark:border-red-800 p-4">
          <div className="text-sm text-red-600">Open Findings</div>
          <div className="text-2xl font-bold text-red-700">{summary?.total_open_findings || 0}</div>
        </div>
        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg shadow-sm border border-orange-200 dark:border-orange-800 p-4">
          <div className="text-sm text-orange-600">Overdue Findings</div>
          <div className="text-2xl font-bold text-orange-700">{overdueFindings?.length || 0}</div>
        </div>
      </div>

      {/* Overdue Findings Alert */}
      {overdueFindings && overdueFindings.length > 0 && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              {overdueFindings.length} overdue finding(s) require attention
            </h3>
          </div>
          <div className="mt-2 space-y-1">
            {overdueFindings.slice(0, 3).map((f) => (
              <div key={f.id} className="text-xs text-red-700 flex items-center justify-between">
                <span>{f.title}</span>
                <span className={`px-1.5 py-0.5 rounded ${SEVERITY_CONFIG[f.severity]?.color}`}>
                  {f.severity}
                </span>
              </div>
            ))}
            {overdueFindings.length > 3 && (
              <div className="text-xs text-red-600">+{overdueFindings.length - 3} more...</div>
            )}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md text-sm"
        >
          <option value="">All Status</option>
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
            <option key={key} value={key}>{cfg.label}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md text-sm"
        >
          <option value="">All Types</option>
          {AUDIT_TYPES.map((type) => (
            <option key={type} value={type}>{type.replace(/_/g, " ")}</option>
          ))}
        </select>
      </div>

      {/* Audits Grid */}
      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {auditsList.map((audit: Audit) => {
              const statusConfig = STATUS_CONFIG[audit.status] || STATUS_CONFIG.PLANNED;
              const StatusIcon = statusConfig.icon;

              return (
                <div
                  key={audit.id}
                  className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.color}`}>
                          <StatusIcon className="h-3.5 w-3.5 mr-1" />
                          {statusConfig.label}
                        </span>
                        <h3 className="mt-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {audit.title}
                        </h3>
                        <p className="text-xs text-gray-500">{audit.audit_ref}</p>
                      </div>
                      <span className="px-2 py-1 bg-gray-100 dark:bg-dark-700 text-gray-700 dark:text-gray-300 text-xs font-medium rounded">
                        {audit.audit_type.replace(/_/g, " ")}
                      </span>
                    </div>

                    {audit.description && (
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{audit.description}</p>
                    )}

                    <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Timeline</span>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          {audit.planned_start ? new Date(audit.planned_start).toLocaleDateString() : "—"} - {audit.planned_end ? new Date(audit.planned_end).toLocaleDateString() : "—"}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Findings</span>
                        <p className="font-medium">
                          {audit.total_findings > 0 ? (
                            <span className="text-amber-600">
                              {audit.total_findings} ({audit.critical_findings}C / {audit.high_findings}H)
                            </span>
                          ) : (
                            <span className="text-green-600">No findings</span>
                          )}
                        </p>
                      </div>
                    </div>

                    {audit.overall_rating && (
                      <div className="mt-3">
                        <span className="text-gray-500 text-sm">Rating: </span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{audit.overall_rating}</span>
                      </div>
                    )}
                  </div>

                  <div className="px-6 py-3 bg-gray-50 dark:bg-dark-700 border-t border-gray-100 dark:border-dark-600 flex justify-between">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setViewAudit(audit)}
                        className="p-1.5 text-gray-400 hover:text-gray-600"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm("Delete this audit?")) {
                            deleteMutation.mutate(audit.id);
                          }
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="flex space-x-2">
                      {audit.status === "PLANNED" && (
                        <button
                          onClick={() => startMutation.mutate(audit.id)}
                          className="text-sm text-green-600 hover:text-green-700 font-medium"
                        >
                          Start Audit
                        </button>
                      )}
                      {audit.status === "IN_PROGRESS" && (
                        <button
                          onClick={() => completeMutation.mutate(audit.id)}
                          className="text-sm text-green-600 hover:text-green-700 font-medium"
                        >
                          Complete Audit
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm">Page {page} of {totalPages}</span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}

          {auditsList.length === 0 && (
            <div className="text-center py-12 bg-white dark:bg-dark-800 rounded-lg shadow-sm">
              <MagnifyingGlassCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No audits found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating your first audit.</p>
            </div>
          )}
        </>
      )}

      {/* Create Audit Modal */}
      <AuditFormModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />

      {/* View Audit Modal */}
      {viewAudit && (
        <AuditDetailModal
          isOpen={!!viewAudit}
          onClose={() => setViewAudit(null)}
          audit={viewAudit}
        />
      )}
    </div>
  );
}

// Audit Form Modal
function AuditFormModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    title: "",
    audit_type: "INTERNAL",
    description: "",
    scope_description: "",
    planned_start: "",
    planned_end: "",
  });

  const createMutation = useMutation({
    mutationFn: () => auditsApi.create(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      queryClient.invalidateQueries({ queryKey: ["audits-summary"] });
      onClose();
      setFormData({
        title: "",
        audit_type: "INTERNAL",
        description: "",
        scope_description: "",
        planned_start: "",
        planned_end: "",
      });
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Audit" size="lg">
      <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(); }} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Title *</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Audit Type *</label>
          <select
            value={formData.audit_type}
            onChange={(e) => setFormData({ ...formData, audit_type: e.target.value })}
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
          >
            {AUDIT_TYPES.map((type) => (
              <option key={type} value={type}>{type.replace(/_/g, " ")}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Scope Description</label>
          <textarea
            value={formData.scope_description}
            onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
            rows={2}
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Planned Start</label>
            <input
              type="date"
              value={formData.planned_start}
              onChange={(e) => setFormData({ ...formData, planned_start: e.target.value })}
              className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Planned End</label>
            <input
              type="date"
              value={formData.planned_end}
              onChange={(e) => setFormData({ ...formData, planned_end: e.target.value })}
              className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
            Cancel
          </button>
          <button
            type="submit"
            disabled={!formData.title || createMutation.isPending}
            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {createMutation.isPending ? "Creating..." : "Create Audit"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

// Audit Detail Modal with Findings
function AuditDetailModal({ isOpen, onClose, audit }: { isOpen: boolean; onClose: () => void; audit: Audit }) {
  const queryClient = useQueryClient();
  const [showFindingForm, setShowFindingForm] = useState(false);
  const statusConfig = STATUS_CONFIG[audit.status] || STATUS_CONFIG.PLANNED;

  // Fetch findings for this audit
  const { data: findings = [] } = useQuery<Finding[]>({
    queryKey: ["audit-findings", audit.id],
    queryFn: async () => {
      const res = await auditsApi.findings.list(audit.id);
      return res.data;
    },
  });

  // Close finding mutation
  const closeFindinMutation = useMutation({
    mutationFn: (findingId: string) => auditsApi.findings.close(findingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audit-findings", audit.id] });
      queryClient.invalidateQueries({ queryKey: ["audits"] });
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={audit.title} size="xl">
      <div className="space-y-6">
        {/* Audit Header */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500">{audit.audit_ref}</span>
          <span className={`px-2 py-1 rounded text-xs font-medium ${statusConfig.color}`}>
            {statusConfig.label}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
            {audit.audit_type.replace(/_/g, " ")}
          </span>
        </div>

        {/* Audit Info */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Planned Start:</span>{" "}
            <span className="font-medium">{audit.planned_start ? new Date(audit.planned_start).toLocaleDateString() : "—"}</span>
          </div>
          <div>
            <span className="text-gray-500">Planned End:</span>{" "}
            <span className="font-medium">{audit.planned_end ? new Date(audit.planned_end).toLocaleDateString() : "—"}</span>
          </div>
          <div>
            <span className="text-gray-500">Actual Start:</span>{" "}
            <span className="font-medium">{audit.actual_start ? new Date(audit.actual_start).toLocaleDateString() : "—"}</span>
          </div>
          <div>
            <span className="text-gray-500">Actual End:</span>{" "}
            <span className="font-medium">{audit.actual_end ? new Date(audit.actual_end).toLocaleDateString() : "—"}</span>
          </div>
        </div>

        {audit.scope_description && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Scope</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{audit.scope_description}</p>
          </div>
        )}

        {/* Findings Summary */}
        <div className="border-t pt-4">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Findings ({audit.total_findings})
            </h4>
            <button
              onClick={() => setShowFindingForm(!showFindingForm)}
              className="text-sm text-green-600 hover:text-green-700"
            >
              + Add Finding
            </button>
          </div>

          <div className="flex space-x-4 mb-4 text-xs">
            <span className="px-2 py-1 bg-red-100 text-red-700 rounded">Critical: {audit.critical_findings}</span>
            <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded">High: {audit.high_findings}</span>
            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">Medium: {audit.medium_findings}</span>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">Low: {audit.low_findings}</span>
          </div>

          {showFindingForm && (
            <FindingForm
              auditId={audit.id}
              onSuccess={() => {
                setShowFindingForm(false);
                queryClient.invalidateQueries({ queryKey: ["audit-findings", audit.id] });
                queryClient.invalidateQueries({ queryKey: ["audits"] });
              }}
              onCancel={() => setShowFindingForm(false)}
            />
          )}

          {/* Findings List */}
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {findings.map((finding) => (
              <div key={finding.id} className="p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">{finding.finding_ref}</span>
                      <span className={`px-1.5 py-0.5 rounded text-xs ${SEVERITY_CONFIG[finding.severity]?.color}`}>
                        {finding.severity}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-xs ${finding.status === "CLOSED" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                        {finding.status}
                      </span>
                    </div>
                    <h5 className="font-medium text-gray-900 dark:text-gray-100 mt-1">{finding.title}</h5>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-2">{finding.description}</p>
                  </div>
                  {finding.status !== "CLOSED" && (
                    <button
                      onClick={() => closeFindinMutation.mutate(finding.id)}
                      className="text-xs text-green-600 hover:text-green-700"
                    >
                      Close
                    </button>
                  )}
                </div>
              </div>
            ))}
            {findings.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No findings recorded</p>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}

// Finding Form Component
function FindingForm({ auditId, onSuccess, onCancel }: { auditId: string; onSuccess: () => void; onCancel: () => void }) {
  const [data, setData] = useState({
    title: "",
    severity: "MEDIUM",
    description: "",
    recommendation: "",
    root_cause: "",
    impact: "",
    target_remediation_date: "",
    owner_department: "",
  });

  const createMutation = useMutation({
    mutationFn: () => auditsApi.findings.create(auditId, data),
    onSuccess,
  });

  return (
    <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg mb-4 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <input
          type="text"
          value={data.title}
          onChange={(e) => setData({ ...data, title: e.target.value })}
          placeholder="Finding title *"
          className="col-span-2 text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
          required
        />
        <select
          value={data.severity}
          onChange={(e) => setData({ ...data, severity: e.target.value })}
          className="text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        >
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
          <option value="INFORMATIONAL">Informational</option>
        </select>
        <input
          type="date"
          value={data.target_remediation_date}
          onChange={(e) => setData({ ...data, target_remediation_date: e.target.value })}
          className="text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
          placeholder="Target Date"
        />
      </div>
      <textarea
        value={data.description}
        onChange={(e) => setData({ ...data, description: e.target.value })}
        placeholder="Description *"
        rows={2}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        required
      />
      <textarea
        value={data.recommendation}
        onChange={(e) => setData({ ...data, recommendation: e.target.value })}
        placeholder="Recommendation"
        rows={2}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
      />
      <div className="flex justify-end space-x-2">
        <button onClick={onCancel} className="text-sm px-3 py-1 text-gray-600 hover:text-gray-800">Cancel</button>
        <button
          onClick={() => createMutation.mutate()}
          disabled={!data.title || !data.description || createMutation.isPending}
          className="text-sm px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Creating..." : "Add Finding"}
        </button>
      </div>
    </div>
  );
}
