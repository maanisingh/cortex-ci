import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  FolderOpenIcon,
  MagnifyingGlassIcon,
  DocumentIcon,
  PhotoIcon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  TrashIcon,
  ClockIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { evidenceApi } from "../services/api";
import Modal from "../components/common/Modal";

// Types
interface Evidence {
  id: string;
  evidence_ref: string;
  title: string;
  description: string | null;
  evidence_type: string;
  category: string | null;
  status: string;
  collected_at: string;
  file_name: string | null;
  file_size: number | null;
  external_url: string | null;
  valid_from: string | null;
  valid_to: string | null;
  is_perpetual: boolean;
  tags: string[] | null;
  created_at: string;
}

interface EvidenceSummary {
  total: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  expiring_soon: number;
  pending_review: number;
}

// Evidence types for form
const EVIDENCE_TYPES = [
  "DOCUMENT",
  "SCREENSHOT",
  "LOG_FILE",
  "CONFIG_FILE",
  "REPORT",
  "ATTESTATION",
  "CERTIFICATE",
  "POLICY",
  "PROCEDURE",
  "AUDIT_RESULT",
  "TRAINING_RECORD",
  "OTHER",
];

// Status configuration
const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  DRAFT: { label: "Draft", color: "bg-gray-100 text-gray-800", icon: DocumentIcon },
  PENDING_REVIEW: { label: "Pending Review", color: "bg-yellow-100 text-yellow-800", icon: ClockIcon },
  APPROVED: { label: "Approved", color: "bg-green-100 text-green-800", icon: CheckBadgeIcon },
  REJECTED: { label: "Rejected", color: "bg-red-100 text-red-800", icon: XCircleIcon },
  EXPIRED: { label: "Expired", color: "bg-red-100 text-red-800", icon: ExclamationTriangleIcon },
};

// File type icons
const FILE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  pdf: DocumentIcon,
  doc: DocumentIcon,
  docx: DocumentIcon,
  png: PhotoIcon,
  jpg: PhotoIcon,
  jpeg: PhotoIcon,
  xlsx: TableCellsIcon,
  csv: TableCellsIcon,
};

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

export default function Evidence() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [dragActive, setDragActive] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [viewEvidence, setViewEvidence] = useState<Evidence | null>(null);
  const [page, setPage] = useState(1);

  // Fetch summary
  const { data: summary } = useQuery<EvidenceSummary>({
    queryKey: ["evidence-summary"],
    queryFn: async () => {
      const res = await evidenceApi.summary();
      return res.data;
    },
  });

  // Fetch evidence list
  const { data: evidenceData, isLoading } = useQuery({
    queryKey: ["evidence", page, typeFilter, statusFilter, searchQuery],
    queryFn: async () => {
      const res = await evidenceApi.list({
        page,
        page_size: 20,
        evidence_type: typeFilter || undefined,
        status: statusFilter || undefined,
        search: searchQuery || undefined,
      });
      return res.data;
    },
  });

  // Fetch expiring evidence
  const { data: expiringEvidence } = useQuery<Evidence[]>({
    queryKey: ["evidence-expiring"],
    queryFn: async () => {
      const res = await evidenceApi.expiring(30);
      return res.data;
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => evidenceApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["evidence-summary"] });
    },
  });

  // Submit for review mutation
  const submitForReviewMutation = useMutation({
    mutationFn: (id: string) => evidenceApi.submitForReview(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["evidence-summary"] });
    },
  });

  // Review mutation
  const reviewMutation = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: string }) =>
      evidenceApi.review(id, { decision }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["evidence-summary"] });
      setViewEvidence(null);
    },
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    // Handle file upload here (would need file upload endpoint)
    setShowCreateModal(true);
  };

  const evidenceList = evidenceData?.items || [];
  const totalPages = evidenceData ? Math.ceil(evidenceData.total / 20) : 0;

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
            <FolderOpenIcon className="h-8 w-8 mr-3 text-teal-600" />
            Evidence Library
          </h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Centralized repository for compliance evidence, audit artifacts, and supporting documentation.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 bg-teal-600 text-white text-sm font-medium rounded-md hover:bg-teal-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Evidence
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        className={`mb-6 border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? "border-teal-500 bg-teal-50 dark:bg-teal-900/20"
            : "border-gray-300 dark:border-dark-600 hover:border-gray-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <FolderOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <label className="cursor-pointer">
            <span className="text-teal-600 hover:text-teal-500 font-medium">Upload evidence</span>
            <input type="file" className="hidden" multiple onChange={() => setShowCreateModal(true)} />
          </label>
          <span className="text-gray-500 dark:text-gray-400"> or drag and drop</span>
        </div>
        <p className="mt-1 text-xs text-gray-500">PDF, DOC, DOCX, XLS, XLSX, PNG, JPG up to 50MB</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 p-4">
          <div className="text-sm text-gray-500">Total Evidence</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{summary?.total || 0}</div>
        </div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg shadow-sm border border-green-200 dark:border-green-800 p-4">
          <div className="text-sm text-green-600">Approved</div>
          <div className="text-2xl font-bold text-green-700">{summary?.by_status?.APPROVED || 0}</div>
        </div>
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg shadow-sm border border-yellow-200 dark:border-yellow-800 p-4">
          <div className="text-sm text-yellow-600">Pending Review</div>
          <div className="text-2xl font-bold text-yellow-700">{summary?.pending_review || 0}</div>
        </div>
        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg shadow-sm border border-orange-200 dark:border-orange-800 p-4">
          <div className="text-sm text-orange-600">Expiring Soon</div>
          <div className="text-2xl font-bold text-orange-700">{summary?.expiring_soon || 0}</div>
        </div>
      </div>

      {/* Expiring Soon Alert */}
      {expiringEvidence && expiringEvidence.length > 0 && (
        <div className="mb-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-500 mr-2" />
            <h3 className="text-sm font-medium text-orange-800 dark:text-orange-200">
              {expiringEvidence.length} evidence item(s) expiring within 30 days
            </h3>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {expiringEvidence.slice(0, 5).map((e) => (
              <span key={e.id} className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                {e.title}
              </span>
            ))}
            {expiringEvidence.length > 5 && (
              <span className="text-xs text-orange-600">+{expiringEvidence.length - 5} more</span>
            )}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search evidence..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md text-sm"
            />
          </div>
        </div>
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md text-sm"
        >
          <option value="">All Types</option>
          {EVIDENCE_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.replace(/_/g, " ")}
            </option>
          ))}
        </select>
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
            <option key={key} value={key}>
              {cfg.label}
            </option>
          ))}
        </select>
      </div>

      {/* Evidence Grid */}
      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {evidenceList.map((evidence: Evidence) => {
              const ext = evidence.file_name?.split(".").pop()?.toLowerCase() || "";
              const FileIcon = FILE_ICONS[ext] || DocumentIcon;
              const statusConfig = STATUS_CONFIG[evidence.status] || STATUS_CONFIG.DRAFT;
              const StatusIcon = statusConfig.icon;

              return (
                <div
                  key={evidence.id}
                  className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-dark-700 p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center">
                      <div className="p-2 bg-gray-100 dark:bg-dark-700 rounded-lg">
                        <FileIcon className="h-6 w-6 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate max-w-[200px]">
                          {evidence.title}
                        </h3>
                        <p className="text-xs text-gray-500">{evidence.evidence_ref}</p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusConfig.color}`}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {statusConfig.label}
                    </span>
                  </div>

                  <div className="mt-4 space-y-2 text-xs text-gray-500 dark:text-gray-400">
                    <div><span className="font-medium">Type:</span> {evidence.evidence_type.replace(/_/g, " ")}</div>
                    <div><span className="font-medium">Collected:</span> {new Date(evidence.collected_at).toLocaleDateString()}</div>
                    {evidence.valid_to && !evidence.is_perpetual && (
                      <div><span className="font-medium">Valid Until:</span> {new Date(evidence.valid_to).toLocaleDateString()}</div>
                    )}
                    {evidence.is_perpetual && (
                      <div><span className="font-medium text-green-600">Perpetual Validity</span></div>
                    )}
                    {evidence.file_size && (
                      <div><span className="font-medium">Size:</span> {formatFileSize(evidence.file_size)}</div>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-100 dark:border-dark-600 flex justify-between">
                    <div className="flex space-x-2">
                      {evidence.status === "DRAFT" && (
                        <button
                          onClick={() => submitForReviewMutation.mutate(evidence.id)}
                          className="text-xs px-2 py-1 bg-teal-100 text-teal-700 rounded hover:bg-teal-200"
                        >
                          Submit for Review
                        </button>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setViewEvidence(evidence)}
                        className="p-1.5 text-gray-400 hover:text-gray-600"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button className="p-1.5 text-gray-400 hover:text-gray-600">
                        <ArrowDownTrayIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm("Delete this evidence?")) {
                            deleteMutation.mutate(evidence.id);
                          }
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
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
              <span className="px-3 py-1 text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}

          {evidenceList.length === 0 && (
            <div className="text-center py-12 bg-white dark:bg-dark-800 rounded-lg shadow-sm">
              <FolderOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No evidence found</h3>
              <p className="mt-1 text-sm text-gray-500">Upload evidence or adjust your search filters.</p>
            </div>
          )}
        </>
      )}

      {/* Create Evidence Modal */}
      <EvidenceFormModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />

      {/* View Evidence Modal */}
      {viewEvidence && (
        <Modal isOpen={!!viewEvidence} onClose={() => setViewEvidence(null)} title={viewEvidence.title} size="lg">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-500">{viewEvidence.evidence_ref}</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_CONFIG[viewEvidence.status]?.color}`}>
                {STATUS_CONFIG[viewEvidence.status]?.label}
              </span>
            </div>

            {viewEvidence.description && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{viewEvidence.description}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Type:</span> <span className="font-medium">{viewEvidence.evidence_type}</span></div>
              <div><span className="text-gray-500">Category:</span> <span className="font-medium">{viewEvidence.category || "—"}</span></div>
              <div><span className="text-gray-500">Collected:</span> <span className="font-medium">{new Date(viewEvidence.collected_at).toLocaleString()}</span></div>
              <div><span className="text-gray-500">Valid Until:</span> <span className="font-medium">{viewEvidence.is_perpetual ? "Perpetual" : viewEvidence.valid_to ? new Date(viewEvidence.valid_to).toLocaleDateString() : "—"}</span></div>
            </div>

            {viewEvidence.external_url && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">External URL</h4>
                <a href={viewEvidence.external_url} target="_blank" rel="noopener noreferrer" className="text-sm text-teal-600 hover:underline">
                  {viewEvidence.external_url}
                </a>
              </div>
            )}

            {/* Review Actions */}
            {viewEvidence.status === "PENDING_REVIEW" && (
              <div className="pt-4 border-t flex space-x-3">
                <button
                  onClick={() => reviewMutation.mutate({ id: viewEvidence.id, decision: "APPROVE" })}
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
                >
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                  Approve
                </button>
                <button
                  onClick={() => reviewMutation.mutate({ id: viewEvidence.id, decision: "REJECT" })}
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700"
                >
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  Reject
                </button>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}

// Evidence Form Modal
function EvidenceFormModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    evidence_type: "DOCUMENT",
    category: "",
    external_url: "",
    valid_to: "",
    is_perpetual: false,
  });

  const createMutation = useMutation({
    mutationFn: () => evidenceApi.create(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["evidence-summary"] });
      onClose();
      setFormData({
        title: "",
        description: "",
        evidence_type: "DOCUMENT",
        category: "",
        external_url: "",
        valid_to: "",
        is_perpetual: false,
      });
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Evidence" size="lg">
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Evidence Type *</label>
            <select
              value={formData.evidence_type}
              onChange={(e) => setFormData({ ...formData, evidence_type: e.target.value })}
              className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
            >
              {EVIDENCE_TYPES.map((type) => (
                <option key={type} value={type}>{type.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Category</label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="e.g., Audit, Security, Compliance"
              className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">External URL</label>
          <input
            type="url"
            value={formData.external_url}
            onChange={(e) => setFormData({ ...formData, external_url: e.target.value })}
            placeholder="https://..."
            className="mt-1 block w-full border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_perpetual}
              onChange={(e) => setFormData({ ...formData, is_perpetual: e.target.checked })}
              className="h-4 w-4 text-teal-600 border-gray-300 rounded"
            />
            <label className="ml-2 text-sm text-gray-600 dark:text-gray-400">Perpetual Validity</label>
          </div>
          {!formData.is_perpetual && (
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mr-2">Valid Until:</label>
              <input
                type="date"
                value={formData.valid_to}
                onChange={(e) => setFormData({ ...formData, valid_to: e.target.value })}
                className="border border-gray-300 dark:border-dark-600 dark:bg-dark-700 rounded-md px-2 py-1 text-sm"
              />
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
            Cancel
          </button>
          <button
            type="submit"
            disabled={!formData.title || createMutation.isPending}
            className="px-4 py-2 bg-teal-600 text-white text-sm font-medium rounded-md hover:bg-teal-700 disabled:opacity-50"
          >
            {createMutation.isPending ? "Creating..." : "Create Evidence"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
