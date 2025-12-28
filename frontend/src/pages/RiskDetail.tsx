import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon,
  CalendarIcon,
  TagIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";
import { risksApi } from "../services/api";

interface RiskRegisterDetail {
  id: string;
  tenant_id: string;
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
  risk_owner_id: string | null;
  risk_owner_name: string | null;
  entity_id: string | null;
  entity_name: string | null;
  risk_appetite_threshold: number | null;
  exceeds_appetite: boolean;
  identified_date: string;
  review_date: string | null;
  target_closure_date: string | null;
  closed_date: string | null;
  source: string | null;
  reference_id: string | null;
  control_ids: string[] | null;
  tags: string[] | null;
  custom_fields: Record<string, unknown> | null;
  last_assessed_at: string | null;
  last_assessed_by: string | null;
  created_at: string;
  updated_at: string;
}

const riskLevelColors: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800 border-red-300",
  HIGH: "bg-orange-100 text-orange-800 border-orange-300",
  MEDIUM: "bg-yellow-100 text-yellow-800 border-yellow-300",
  LOW: "bg-green-100 text-green-800 border-green-300",
};

const statusColors: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-800",
  OPEN: "bg-blue-100 text-blue-800",
  IN_TREATMENT: "bg-purple-100 text-purple-800",
  CLOSED: "bg-green-100 text-green-800",
  ACCEPTED: "bg-amber-100 text-amber-800",
};

const treatmentDescriptions: Record<string, string> = {
  ACCEPT: "Accept the risk without taking any specific action",
  MITIGATE: "Implement controls to reduce likelihood or impact",
  TRANSFER: "Transfer risk to a third party (insurance, outsourcing)",
  AVOID: "Eliminate the risk by removing the source",
  MONITOR: "Continuously monitor the risk for changes",
};

export default function RiskDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: risk, isLoading, error } = useQuery<RiskRegisterDetail>({
    queryKey: ["risk-detail", id],
    queryFn: async () => {
      const response = await risksApi.register.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => risksApi.register.delete(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risk-register"] });
      navigate("/risks");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !risk) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Risk not found</p>
        <button
          onClick={() => navigate("/risks")}
          className="mt-2 text-red-600 underline"
        >
          Back to Risk Register
        </button>
      </div>
    );
  }

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
      <div className="mb-6">
        <button
          onClick={() => navigate("/risks")}
          className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Risk Register
        </button>

        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center space-x-3">
              <span className="font-mono text-sm bg-gray-100 dark:bg-dark-700 px-2 py-1 rounded text-primary-600">
                {risk.risk_id}
              </span>
              <span
                className={`px-2 py-1 rounded text-sm font-medium ${statusColors[risk.status]}`}
              >
                {risk.status.replace(/_/g, " ")}
              </span>
              {risk.exceeds_appetite && (
                <span className="px-2 py-1 rounded text-sm font-medium bg-red-100 text-red-800 flex items-center">
                  <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                  Exceeds Appetite
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              {risk.title}
            </h1>
            {risk.description && (
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                {risk.description}
              </p>
            )}
          </div>

          <div className="flex space-x-2">
            <button
              onClick={() => navigate(`/risks?edit=${risk.id}`)}
              className="btn-secondary flex items-center"
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              Edit
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="btn-secondary text-red-600 hover:bg-red-50 flex items-center"
            >
              <TrashIcon className="h-4 w-4 mr-1" />
              Delete
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Risk Assessment Card */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <ShieldCheckIcon className="h-5 w-5 mr-2 text-primary-600" />
              Risk Assessment
            </h2>

            <div className="grid grid-cols-2 gap-6">
              {/* Inherent Risk */}
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Inherent Risk
                </h3>
                <div className="flex items-center space-x-4">
                  <div
                    className={`w-16 h-16 rounded-lg flex items-center justify-center text-white text-2xl font-bold ${getRiskMatrixColor(risk.likelihood, risk.impact)}`}
                  >
                    {risk.likelihood * risk.impact}
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">
                      Likelihood: <span className="font-medium">{risk.likelihood}/5</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Impact: <span className="font-medium">{risk.impact}/5</span>
                    </div>
                    {risk.inherent_risk_level && (
                      <span
                        className={`mt-2 inline-block px-2 py-1 rounded text-xs font-medium ${riskLevelColors[risk.inherent_risk_level]}`}
                      >
                        {risk.inherent_risk_level}
                      </span>
                    )}
                  </div>
                </div>
                {risk.inherent_risk_score && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-1">Score: {risk.inherent_risk_score}/100</div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getRiskMatrixColor(risk.likelihood, risk.impact)}`}
                        style={{ width: `${risk.inherent_risk_score}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Residual Risk */}
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Residual Risk (After Controls)
                </h3>
                {risk.residual_likelihood && risk.residual_impact ? (
                  <>
                    <div className="flex items-center space-x-4">
                      <div
                        className={`w-16 h-16 rounded-lg flex items-center justify-center text-white text-2xl font-bold ${getRiskMatrixColor(risk.residual_likelihood, risk.residual_impact)}`}
                      >
                        {risk.residual_likelihood * risk.residual_impact}
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">
                          Likelihood: <span className="font-medium">{risk.residual_likelihood}/5</span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Impact: <span className="font-medium">{risk.residual_impact}/5</span>
                        </div>
                        {risk.residual_risk_level && (
                          <span
                            className={`mt-2 inline-block px-2 py-1 rounded text-xs font-medium ${riskLevelColors[risk.residual_risk_level]}`}
                          >
                            {risk.residual_risk_level}
                          </span>
                        )}
                      </div>
                    </div>
                    {risk.residual_risk_score && (
                      <div className="mt-3">
                        <div className="text-xs text-gray-500 mb-1">Score: {risk.residual_risk_score}/100</div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${getRiskMatrixColor(risk.residual_likelihood, risk.residual_impact)}`}
                            style={{ width: `${risk.residual_risk_score}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-gray-400 text-sm italic">
                    No residual assessment yet. Update risk with residual values after controls are implemented.
                  </div>
                )}
              </div>
            </div>

            {/* Risk Appetite */}
            {risk.risk_appetite_threshold && (
              <div className="mt-4 p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Risk Appetite Threshold
                  </span>
                  <span className="font-medium">{risk.risk_appetite_threshold}</span>
                </div>
                {risk.exceeds_appetite && (
                  <div className="mt-2 text-sm text-red-600 flex items-center">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    Current risk exceeds organizational risk appetite
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Treatment Plan Card */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Treatment Plan</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm text-gray-500">Treatment Strategy</label>
                <div className="mt-1">
                  <span className="inline-flex px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                    {risk.treatment}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {treatmentDescriptions[risk.treatment]}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Target Closure</label>
                <div className="mt-1 font-medium">
                  {risk.target_closure_date
                    ? new Date(risk.target_closure_date).toLocaleDateString()
                    : "Not set"}
                </div>
              </div>
            </div>

            {risk.treatment_plan ? (
              <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                <label className="text-sm text-gray-500 block mb-2">Plan Details</label>
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {risk.treatment_plan}
                </p>
              </div>
            ) : (
              <div className="text-gray-400 italic text-sm">
                No treatment plan defined yet.
              </div>
            )}

            {/* Linked Controls */}
            {risk.control_ids && risk.control_ids.length > 0 && (
              <div className="mt-4">
                <label className="text-sm text-gray-500 block mb-2">Linked Controls</label>
                <div className="flex flex-wrap gap-2">
                  {risk.control_ids.map((controlId) => (
                    <span
                      key={controlId}
                      className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm"
                    >
                      {controlId}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Details Card */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Details</h2>

            <dl className="space-y-4">
              <div>
                <dt className="text-sm text-gray-500 flex items-center">
                  <TagIcon className="h-4 w-4 mr-1" />
                  Category
                </dt>
                <dd className="mt-1 font-medium">{risk.category.replace(/_/g, " ")}</dd>
              </div>

              <div>
                <dt className="text-sm text-gray-500 flex items-center">
                  <UserIcon className="h-4 w-4 mr-1" />
                  Risk Owner
                </dt>
                <dd className="mt-1 font-medium">
                  {risk.risk_owner_name || "Unassigned"}
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-500 flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  Identified Date
                </dt>
                <dd className="mt-1 font-medium">
                  {new Date(risk.identified_date).toLocaleDateString()}
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-500 flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  Review Date
                </dt>
                <dd className="mt-1 font-medium">
                  {risk.review_date
                    ? new Date(risk.review_date).toLocaleDateString()
                    : "Not scheduled"}
                  {risk.review_date && new Date(risk.review_date) < new Date() && (
                    <span className="ml-2 text-xs text-red-600">(Overdue)</span>
                  )}
                </dd>
              </div>

              {risk.source && (
                <div>
                  <dt className="text-sm text-gray-500">Source</dt>
                  <dd className="mt-1 font-medium">{risk.source}</dd>
                </div>
              )}

              {risk.reference_id && (
                <div>
                  <dt className="text-sm text-gray-500">Reference ID</dt>
                  <dd className="mt-1 font-mono text-sm">{risk.reference_id}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Tags */}
          {risk.tags && risk.tags.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {risk.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 dark:bg-dark-700 text-gray-700 dark:text-gray-300 rounded text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Audit Trail */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-3">Audit Trail</h2>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Created</dt>
                <dd>{new Date(risk.created_at).toLocaleString()}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Last Updated</dt>
                <dd>{new Date(risk.updated_at).toLocaleString()}</dd>
              </div>
              {risk.last_assessed_at && (
                <div>
                  <dt className="text-gray-500">Last Assessed</dt>
                  <dd>
                    {new Date(risk.last_assessed_at).toLocaleString()}
                    {risk.last_assessed_by && (
                      <span className="text-gray-400"> by {risk.last_assessed_by}</span>
                    )}
                  </dd>
                </div>
              )}
              {risk.closed_date && (
                <div>
                  <dt className="text-gray-500">Closed</dt>
                  <dd>{new Date(risk.closed_date).toLocaleString()}</dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-dark-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Delete Risk</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Are you sure you want to delete "{risk.title}"? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                className="btn-primary bg-red-600 hover:bg-red-700"
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
