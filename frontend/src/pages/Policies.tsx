import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DocumentTextIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ClockIcon,
  PencilSquareIcon,
  ArchiveBoxIcon,
  EyeIcon,
  TrashIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  ShieldExclamationIcon,
  HandRaisedIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { policiesApi } from "../services/api";
import Modal from "../components/common/Modal";

// Types
interface Policy {
  id: string;
  policy_number: string;
  title: string;
  category: string;
  status: string;
  current_version: string;
  summary: string | null;
  content: string | null;
  owner_department: string | null;
  requires_acknowledgement: boolean;
  effective_date: string | null;
  review_date: string | null;
  tags: string[] | null;
  created_at: string;
}

interface PolicySummary {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  pending_review: number;
  requires_acknowledgement: number;
}

interface PolicyVersion {
  id: string;
  policy_id: string;
  version_number: string;
  version_type: string;
  content: string;
  change_summary: string | null;
  created_by: string | null;
  effective_from: string | null;
  is_current: boolean;
  created_at: string;
}

interface PolicyAcknowledgement {
  id: string;
  policy_id: string;
  user_id: string;
  policy_version: string;
  acknowledged_at: string;
  is_verified: boolean;
  is_expired: boolean;
}

interface PolicyException {
  id: string;
  policy_id: string;
  title: string;
  justification: string;
  scope: string;
  risk_description: string | null;
  compensating_controls: string | null;
  status: string;
  requested_by: string;
  requested_at: string;
  department: string | null;
  effective_from: string | null;
  effective_to: string | null;
  is_permanent: boolean;
}

// Status configuration
const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  DRAFT: { label: "Draft", color: "bg-gray-100 text-gray-800", icon: PencilSquareIcon },
  PENDING_REVIEW: { label: "Pending Review", color: "bg-blue-100 text-blue-800", icon: ClockIcon },
  PENDING_APPROVAL: { label: "Pending Approval", color: "bg-amber-100 text-amber-800", icon: ClockIcon },
  APPROVED: { label: "Approved", color: "bg-green-100 text-green-800", icon: CheckCircleIcon },
  PUBLISHED: { label: "Published", color: "bg-emerald-100 text-emerald-800", icon: CheckCircleIcon },
  UNDER_REVISION: { label: "Under Revision", color: "bg-purple-100 text-purple-800", icon: PencilSquareIcon },
  SUPERSEDED: { label: "Superseded", color: "bg-gray-100 text-gray-500", icon: ArchiveBoxIcon },
  RETIRED: { label: "Retired", color: "bg-gray-100 text-gray-500", icon: ArchiveBoxIcon },
};

const CATEGORIES = [
  "INFORMATION_SECURITY",
  "DATA_PRIVACY",
  "ACCEPTABLE_USE",
  "ACCESS_CONTROL",
  "INCIDENT_RESPONSE",
  "BUSINESS_CONTINUITY",
  "VENDOR_MANAGEMENT",
  "AML_KYC",
  "SANCTIONS",
  "CODE_OF_CONDUCT",
  "RISK_MANAGEMENT",
  "COMPLIANCE",
  "OTHER",
];

export default function Policies() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editPolicy, setEditPolicy] = useState<Policy | null>(null);
  const [viewPolicy, setViewPolicy] = useState<Policy | null>(null);

  // Fetch summary
  const { data: summary } = useQuery<PolicySummary>({
    queryKey: ["policies-summary"],
    queryFn: async () => {
      const res = await policiesApi.summary();
      return res.data;
    },
  });

  // Fetch policies
  const { data: policiesData, isLoading } = useQuery({
    queryKey: ["policies", searchQuery, statusFilter],
    queryFn: async () => {
      const res = await policiesApi.list({
        search: searchQuery || undefined,
        status: statusFilter || undefined,
        page_size: 50,
      });
      return res.data;
    },
  });

  const policies = policiesData?.items || [];

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => policiesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      queryClient.invalidateQueries({ queryKey: ["policies-summary"] });
    },
  });

  // Publish mutation
  const publishMutation = useMutation({
    mutationFn: (id: string) => policiesApi.publish(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      queryClient.invalidateQueries({ queryKey: ["policies-summary"] });
    },
  });

  const statusCounts = {
    all: summary?.total || 0,
    DRAFT: summary?.by_status?.DRAFT || 0,
    PENDING_REVIEW: summary?.by_status?.PENDING_REVIEW || 0,
    PUBLISHED: summary?.by_status?.PUBLISHED || 0,
    RETIRED: summary?.by_status?.RETIRED || 0,
  };

  const formatCategory = (cat: string) => cat.replace(/_/g, " ");

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
            <DocumentTextIcon className="h-8 w-8 mr-3 text-purple-600" />
            Policy Management
          </h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Create, manage, and track organizational policies throughout their lifecycle.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => {
              setEditPolicy(null);
              setShowForm(true);
            }}
            className="inline-flex items-center rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Policy
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div className="card bg-white dark:bg-dark-800">
          <dt className="text-sm text-gray-500">Total Policies</dt>
          <dd className="text-2xl font-bold text-gray-900 dark:text-gray-100">{summary?.total || 0}</dd>
        </div>
        <div className="card bg-white dark:bg-dark-800 border-l-4 border-orange-500">
          <dt className="text-sm text-gray-500">Pending Review</dt>
          <dd className="text-2xl font-bold text-orange-600">{summary?.pending_review || 0}</dd>
        </div>
        <div className="card bg-white dark:bg-dark-800 border-l-4 border-green-500">
          <dt className="text-sm text-gray-500">Published</dt>
          <dd className="text-2xl font-bold text-green-600">{summary?.by_status?.PUBLISHED || 0}</dd>
        </div>
        <div className="card bg-white dark:bg-dark-800">
          <dt className="text-sm text-gray-500">Require Acknowledgement</dt>
          <dd className="text-2xl font-bold text-gray-900 dark:text-gray-100">{summary?.requires_acknowledgement || 0}</dd>
        </div>
      </div>

      {/* Status Tabs */}
      <div className="border-b border-gray-200 dark:border-dark-600 mb-6">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {[
            { key: null, label: "All", count: statusCounts.all },
            { key: "DRAFT", label: "Draft", count: statusCounts.DRAFT },
            { key: "PENDING_REVIEW", label: "Pending Review", count: statusCounts.PENDING_REVIEW },
            { key: "PUBLISHED", label: "Published", count: statusCounts.PUBLISHED },
            { key: "RETIRED", label: "Retired", count: statusCounts.RETIRED },
          ].map((tab) => (
            <button
              key={tab.key || "all"}
              onClick={() => setStatusFilter(tab.key)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                statusFilter === tab.key
                  ? "border-purple-500 text-purple-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.label}
              <span
                className={`ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium ${
                  statusFilter === tab.key
                    ? "bg-purple-100 text-purple-600"
                    : "bg-gray-100 text-gray-600 dark:bg-dark-700"
                }`}
              >
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search policies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-purple-500 focus:border-purple-500 dark:bg-dark-700 dark:border-dark-600"
          />
        </div>
      </div>

      {/* Policies Table */}
      <div className="bg-white dark:bg-dark-800 shadow-sm rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-600">
          <thead className="bg-gray-50 dark:bg-dark-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Policy
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Department
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Review Date
              </th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-dark-800 divide-y divide-gray-200 dark:divide-dark-600">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mr-2"></div>
                    Loading policies...
                  </div>
                </td>
              </tr>
            ) : policies.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-12">
                  <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                    No policies found
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {searchQuery
                      ? "Try adjusting your search terms."
                      : "Get started by creating your first policy."}
                  </p>
                </td>
              </tr>
            ) : (
              policies.map((policy: Policy) => {
                const statusConfig = STATUS_CONFIG[policy.status] || STATUS_CONFIG.DRAFT;
                const StatusIcon = statusConfig.icon;
                return (
                  <tr key={policy.id} className="hover:bg-gray-50 dark:hover:bg-dark-700">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {policy.title}
                        </div>
                        <div className="text-sm text-gray-500">
                          {policy.policy_number} • v{policy.current_version}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-dark-600 text-gray-700 dark:text-gray-300 rounded">
                        {formatCategory(policy.category)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.color}`}
                      >
                        <StatusIcon className="h-3.5 w-3.5 mr-1" />
                        {statusConfig.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {policy.owner_department || "—"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {policy.review_date
                        ? new Date(policy.review_date).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                      <button
                        onClick={() => setViewPolicy(policy)}
                        className="text-purple-600 hover:text-purple-900"
                      >
                        <EyeIcon className="h-4 w-4 inline" />
                      </button>
                      <button
                        onClick={() => {
                          setEditPolicy(policy);
                          setShowForm(true);
                        }}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        <PencilSquareIcon className="h-4 w-4 inline" />
                      </button>
                      {policy.status === "DRAFT" && (
                        <button
                          onClick={() => publishMutation.mutate(policy.id)}
                          className="text-green-600 hover:text-green-900 text-xs"
                        >
                          Publish
                        </button>
                      )}
                      <button
                        onClick={() => {
                          if (confirm("Delete this policy?")) {
                            deleteMutation.mutate(policy.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="h-4 w-4 inline" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Policy Form Modal */}
      <PolicyFormModal
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setEditPolicy(null);
        }}
        policy={editPolicy}
      />

      {/* View Policy Modal with Tabs */}
      {viewPolicy && (
        <PolicyDetailModal
          isOpen={!!viewPolicy}
          onClose={() => setViewPolicy(null)}
          policy={viewPolicy}
        />
      )}
    </div>
  );
}

// Policy Detail Modal with Tabs
function PolicyDetailModal({
  isOpen,
  onClose,
  policy,
}: {
  isOpen: boolean;
  onClose: () => void;
  policy: Policy;
}) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"details" | "versions" | "acknowledgements" | "exceptions">("details");
  const [showExceptionForm, setShowExceptionForm] = useState(false);
  const [showVersionForm, setShowVersionForm] = useState(false);

  const formatCategory = (cat: string) => cat.replace(/_/g, " ");

  // Fetch versions
  const { data: versions = [] } = useQuery<PolicyVersion[]>({
    queryKey: ["policy-versions", policy.id],
    queryFn: async () => {
      const res = await policiesApi.versions.list(policy.id);
      return res.data;
    },
    enabled: activeTab === "versions",
  });

  // Fetch acknowledgements
  const { data: acknowledgements = [] } = useQuery<PolicyAcknowledgement[]>({
    queryKey: ["policy-acknowledgements", policy.id],
    queryFn: async () => {
      const res = await policiesApi.acknowledgements.list(policy.id);
      return res.data;
    },
    enabled: activeTab === "acknowledgements",
  });

  // Fetch acknowledgement stats
  const { data: ackStats } = useQuery({
    queryKey: ["policy-ack-stats", policy.id],
    queryFn: async () => {
      const res = await policiesApi.acknowledgements.stats(policy.id);
      return res.data;
    },
    enabled: activeTab === "acknowledgements",
  });

  // Fetch exceptions
  const { data: exceptions = [] } = useQuery<PolicyException[]>({
    queryKey: ["policy-exceptions", policy.id],
    queryFn: async () => {
      const res = await policiesApi.exceptions.list(policy.id);
      return res.data;
    },
    enabled: activeTab === "exceptions",
  });

  // Acknowledge mutation
  const acknowledgeMutation = useMutation({
    mutationFn: () => policiesApi.acknowledge(policy.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policy-acknowledgements", policy.id] });
      queryClient.invalidateQueries({ queryKey: ["policy-ack-stats", policy.id] });
    },
  });

  // Create version mutation
  const createVersionMutation = useMutation({
    mutationFn: (data: { change_summary: string; version_type: string; content?: string }) =>
      policiesApi.versions.create(policy.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policy-versions", policy.id] });
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      setShowVersionForm(false);
    },
  });

  // Exception review mutation
  const reviewExceptionMutation = useMutation({
    mutationFn: ({ exceptionId, action, notes }: { exceptionId: string; action: "approve" | "deny"; notes?: string }) =>
      policiesApi.exceptions.review(policy.id, exceptionId, action, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policy-exceptions", policy.id] });
    },
  });

  const tabs = [
    { key: "details", label: "Details", icon: DocumentTextIcon },
    { key: "versions", label: "Versions", icon: ClipboardDocumentListIcon },
    { key: "acknowledgements", label: "Acknowledgements", icon: UserGroupIcon },
    { key: "exceptions", label: "Exceptions", icon: ShieldExclamationIcon },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={policy.title} size="xl">
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-sm text-gray-500">{policy.policy_number}</span>
        <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_CONFIG[policy.status]?.color}`}>
          {STATUS_CONFIG[policy.status]?.label}
        </span>
        <span className="text-sm text-gray-500">v{policy.current_version}</span>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-dark-600 mb-4">
        <nav className="-mb-px flex space-x-6">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center py-3 px-1 border-b-2 text-sm font-medium ${
                  activeTab === tab.key
                    ? "border-purple-500 text-purple-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="max-h-[60vh] overflow-y-auto">
        {activeTab === "details" && (
          <div className="space-y-4">
            {policy.summary && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Summary</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{policy.summary}</p>
              </div>
            )}
            {policy.content && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Content</h4>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1 max-h-64 overflow-y-auto whitespace-pre-wrap bg-gray-50 dark:bg-dark-700 p-4 rounded">
                  {policy.content}
                </div>
              </div>
            )}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Category:</span>{" "}
                <span className="font-medium">{formatCategory(policy.category)}</span>
              </div>
              <div>
                <span className="text-gray-500">Department:</span>{" "}
                <span className="font-medium">{policy.owner_department || "—"}</span>
              </div>
              <div>
                <span className="text-gray-500">Effective:</span>{" "}
                <span className="font-medium">
                  {policy.effective_date ? new Date(policy.effective_date).toLocaleDateString() : "—"}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Review Date:</span>{" "}
                <span className="font-medium">
                  {policy.review_date ? new Date(policy.review_date).toLocaleDateString() : "—"}
                </span>
              </div>
            </div>

            {policy.requires_acknowledgement && (
              <div className="pt-4 border-t">
                <button
                  onClick={() => acknowledgeMutation.mutate()}
                  disabled={acknowledgeMutation.isPending}
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700"
                >
                  <HandRaisedIcon className="h-4 w-4 mr-2" />
                  {acknowledgeMutation.isPending ? "Acknowledging..." : "Acknowledge Policy"}
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === "versions" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Version History</h4>
              <button
                onClick={() => setShowVersionForm(!showVersionForm)}
                className="text-sm text-purple-600 hover:text-purple-700"
              >
                + Create New Version
              </button>
            </div>

            {showVersionForm && (
              <VersionForm
                onSubmit={(data) => createVersionMutation.mutate(data)}
                onCancel={() => setShowVersionForm(false)}
                isLoading={createVersionMutation.isPending}
              />
            )}

            {versions.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No version history available</p>
            ) : (
              <div className="space-y-3">
                {versions.map((version) => (
                  <div
                    key={version.id}
                    className={`p-3 rounded-lg border ${
                      version.is_current ? "border-purple-300 bg-purple-50 dark:bg-purple-900/20" : "border-gray-200 dark:border-dark-600"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">v{version.version_number}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          version.version_type === "MAJOR" ? "bg-red-100 text-red-700" :
                          version.version_type === "MINOR" ? "bg-blue-100 text-blue-700" :
                          "bg-gray-100 text-gray-700"
                        }`}>
                          {version.version_type}
                        </span>
                        {version.is_current && (
                          <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">Current</span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(version.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {version.change_summary && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{version.change_summary}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "acknowledgements" && (
          <div className="space-y-4">
            {ackStats && (
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-50 dark:bg-dark-700 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{ackStats.total_acknowledged}</div>
                  <div className="text-xs text-gray-500">Acknowledged</div>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{ackStats.pending}</div>
                  <div className="text-xs text-gray-500">Pending</div>
                </div>
                <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{ackStats.expired}</div>
                  <div className="text-xs text-gray-500">Expired</div>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{ackStats.compliance_rate}%</div>
                  <div className="text-xs text-gray-500">Compliance</div>
                </div>
              </div>
            )}

            {acknowledgements.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No acknowledgements yet</p>
            ) : (
              <div className="space-y-2">
                {acknowledgements.map((ack) => (
                  <div key={ack.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <CheckCircleIcon className={`h-5 w-5 ${ack.is_expired ? "text-gray-400" : "text-green-500"}`} />
                      <div>
                        <div className="text-sm font-medium">User {ack.user_id.slice(0, 8)}...</div>
                        <div className="text-xs text-gray-500">v{ack.policy_version}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm">{new Date(ack.acknowledged_at).toLocaleDateString()}</div>
                      {ack.is_expired && <span className="text-xs text-red-500">Expired</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "exceptions" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Policy Exceptions</h4>
              <button
                onClick={() => setShowExceptionForm(!showExceptionForm)}
                className="text-sm text-purple-600 hover:text-purple-700"
              >
                + Request Exception
              </button>
            </div>

            {showExceptionForm && (
              <ExceptionForm
                policyId={policy.id}
                onSuccess={() => {
                  setShowExceptionForm(false);
                  queryClient.invalidateQueries({ queryKey: ["policy-exceptions", policy.id] });
                }}
                onCancel={() => setShowExceptionForm(false)}
              />
            )}

            {exceptions.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No exceptions requested</p>
            ) : (
              <div className="space-y-3">
                {exceptions.map((exception) => (
                  <div key={exception.id} className="p-4 border rounded-lg dark:border-dark-600">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium text-gray-900 dark:text-gray-100">{exception.title}</h5>
                        <p className="text-sm text-gray-500 mt-1">{exception.justification}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        exception.status === "APPROVED" ? "bg-green-100 text-green-700" :
                        exception.status === "DENIED" ? "bg-red-100 text-red-700" :
                        exception.status === "PENDING" ? "bg-yellow-100 text-yellow-700" :
                        "bg-gray-100 text-gray-700"
                      }`}>
                        {exception.status}
                      </span>
                    </div>
                    <div className="mt-3 text-xs text-gray-500">
                      <span>Requested: {new Date(exception.requested_at).toLocaleDateString()}</span>
                      {exception.effective_to && !exception.is_permanent && (
                        <span className="ml-4">Expires: {new Date(exception.effective_to).toLocaleDateString()}</span>
                      )}
                      {exception.is_permanent && <span className="ml-4 text-purple-600">Permanent</span>}
                    </div>
                    {exception.status === "PENDING" && (
                      <div className="mt-3 flex space-x-2">
                        <button
                          onClick={() => reviewExceptionMutation.mutate({ exceptionId: exception.id, action: "approve" })}
                          className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => reviewExceptionMutation.mutate({ exceptionId: exception.id, action: "deny" })}
                          className="text-xs px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          Deny
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
}

// Version Form Component
function VersionForm({
  onSubmit,
  onCancel,
  isLoading,
}: {
  onSubmit: (data: { change_summary: string; version_type: string; content?: string }) => void;
  onCancel: () => void;
  isLoading: boolean;
}) {
  const [data, setData] = useState({ change_summary: "", version_type: "MINOR", content: "" });

  return (
    <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg space-y-3">
      <select
        value={data.version_type}
        onChange={(e) => setData({ ...data, version_type: e.target.value })}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
      >
        <option value="PATCH">Patch (minor fixes)</option>
        <option value="MINOR">Minor (small changes)</option>
        <option value="MAJOR">Major (significant changes)</option>
      </select>
      <textarea
        value={data.change_summary}
        onChange={(e) => setData({ ...data, change_summary: e.target.value })}
        placeholder="Describe the changes..."
        rows={2}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        required
      />
      <textarea
        value={data.content}
        onChange={(e) => setData({ ...data, content: e.target.value })}
        placeholder="Updated content (optional - leave blank to keep current)"
        rows={4}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
      />
      <div className="flex justify-end space-x-2">
        <button onClick={onCancel} className="text-sm px-3 py-1 text-gray-600 hover:text-gray-800">Cancel</button>
        <button
          onClick={() => onSubmit(data)}
          disabled={!data.change_summary || isLoading}
          className="text-sm px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        >
          {isLoading ? "Creating..." : "Create Version"}
        </button>
      </div>
    </div>
  );
}

// Exception Form Component
function ExceptionForm({
  policyId,
  onSuccess,
  onCancel,
}: {
  policyId: string;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const [data, setData] = useState({
    title: "",
    justification: "",
    scope: "",
    risk_description: "",
    compensating_controls: "",
    department: "",
    is_permanent: false,
    effective_to: "",
  });

  const createMutation = useMutation({
    mutationFn: () => policiesApi.exceptions.create(policyId, {
      ...data,
      effective_to: data.is_permanent ? undefined : data.effective_to || undefined,
    }),
    onSuccess,
  });

  return (
    <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg space-y-3">
      <input
        type="text"
        value={data.title}
        onChange={(e) => setData({ ...data, title: e.target.value })}
        placeholder="Exception title"
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        required
      />
      <textarea
        value={data.justification}
        onChange={(e) => setData({ ...data, justification: e.target.value })}
        placeholder="Business justification for this exception..."
        rows={2}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        required
      />
      <textarea
        value={data.scope}
        onChange={(e) => setData({ ...data, scope: e.target.value })}
        placeholder="Scope of the exception..."
        rows={2}
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
        required
      />
      <input
        type="text"
        value={data.compensating_controls}
        onChange={(e) => setData({ ...data, compensating_controls: e.target.value })}
        placeholder="Compensating controls (if any)"
        className="w-full text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
      />
      <div className="flex items-center space-x-4">
        <label className="flex items-center text-sm">
          <input
            type="checkbox"
            checked={data.is_permanent}
            onChange={(e) => setData({ ...data, is_permanent: e.target.checked })}
            className="mr-2 rounded border-gray-300"
          />
          Permanent exception
        </label>
        {!data.is_permanent && (
          <input
            type="date"
            value={data.effective_to}
            onChange={(e) => setData({ ...data, effective_to: e.target.value })}
            className="text-sm rounded border-gray-300 dark:bg-dark-600 dark:border-dark-500"
          />
        )}
      </div>
      <div className="flex justify-end space-x-2">
        <button onClick={onCancel} className="text-sm px-3 py-1 text-gray-600 hover:text-gray-800">Cancel</button>
        <button
          onClick={() => createMutation.mutate()}
          disabled={!data.title || !data.justification || !data.scope || createMutation.isPending}
          className="text-sm px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Submitting..." : "Submit Request"}
        </button>
      </div>
    </div>
  );
}

// Policy Form Modal
function PolicyFormModal({
  isOpen,
  onClose,
  policy,
}: {
  isOpen: boolean;
  onClose: () => void;
  policy: Policy | null;
}) {
  const queryClient = useQueryClient();
  const isEdit = !!policy;

  const [formData, setFormData] = useState({
    policy_number: "",
    title: "",
    category: "INFORMATION_SECURITY",
    content: "",
    summary: "",
    purpose: "",
    scope: "",
    owner_department: "",
    requires_acknowledgement: true,
    review_frequency_months: 12,
    tags: "",
  });

  const [error, setError] = useState("");

  // Reset form on open
  useState(() => {
    if (policy) {
      setFormData({
        policy_number: policy.policy_number,
        title: policy.title,
        category: policy.category,
        content: policy.content || "",
        summary: policy.summary || "",
        purpose: "",
        scope: "",
        owner_department: policy.owner_department || "",
        requires_acknowledgement: policy.requires_acknowledgement,
        review_frequency_months: 12,
        tags: policy.tags?.join(", ") || "",
      });
    } else {
      setFormData({
        policy_number: `POL-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 1000)).padStart(3, "0")}`,
        title: "",
        category: "INFORMATION_SECURITY",
        content: "",
        summary: "",
        purpose: "",
        scope: "",
        owner_department: "",
        requires_acknowledgement: true,
        review_frequency_months: 12,
        tags: "",
      });
    }
    setError("");
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => policiesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      queryClient.invalidateQueries({ queryKey: ["policies-summary"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to create policy");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => policiesApi.update(policy!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      queryClient.invalidateQueries({ queryKey: ["policies-summary"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to update policy");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      ...formData,
      tags: formData.tags ? formData.tags.split(",").map((t) => t.trim()).filter(Boolean) : [],
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
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Policy" : "Create New Policy"}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Policy Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="policy_number"
              value={formData.policy_number}
              onChange={handleChange}
              required
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
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
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

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
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              placeholder="Policy title"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Summary
            </label>
            <textarea
              name="summary"
              value={formData.summary}
              onChange={handleChange}
              rows={2}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              placeholder="Brief summary of the policy"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content <span className="text-red-500">*</span>
            </label>
            <textarea
              name="content"
              value={formData.content}
              onChange={handleChange}
              required
              rows={6}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              placeholder="Full policy content..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Owner Department
            </label>
            <input
              type="text"
              name="owner_department"
              value={formData.owner_department}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              placeholder="e.g., IT Security"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Review Frequency
            </label>
            <select
              name="review_frequency_months"
              value={formData.review_frequency_months}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
            >
              <option value={6}>Every 6 months</option>
              <option value={12}>Annually</option>
              <option value={24}>Every 2 years</option>
            </select>
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
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              placeholder="e.g., security, mandatory, 2025"
            />
          </div>

          <div className="col-span-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="requires_acknowledgement"
                checked={formData.requires_acknowledgement}
                onChange={handleChange}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">
                Requires employee acknowledgement
              </span>
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending || updateMutation.isPending}
            className="inline-flex items-center rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500"
          >
            {createMutation.isPending || updateMutation.isPending
              ? "Saving..."
              : isEdit
                ? "Update Policy"
                : "Create Policy"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
