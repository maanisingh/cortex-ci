import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "../services/api";
import { useAuthStore } from "../stores/authStore";
import {
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

export default function Settings() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: async () => {
      const response = await adminApi.settings.get();
      return response.data;
    },
    enabled: user?.role === "admin",
  });

  // Risk Appetite State
  const [riskAppetite, setRiskAppetite] = useState({
    overall_threshold: 60,
    strategic_threshold: 70,
    operational_threshold: 50,
    financial_threshold: 40,
    compliance_threshold: 30,
    cyber_threshold: 40,
    review_frequency_days: 90,
    escalation_enabled: true,
  });

  const [appetiteSaved, setAppetiteSaved] = useState(false);

  const handleAppetiteChange = (field: string, value: number | boolean) => {
    setRiskAppetite((prev) => ({ ...prev, [field]: value }));
    setAppetiteSaved(false);
  };

  const saveAppetite = () => {
    // In a real implementation, this would call an API
    setAppetiteSaved(true);
    setTimeout(() => setAppetiteSaved(false), 3000);
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          System configuration and GRC preferences
        </p>
      </div>

      {/* User Profile */}
      <div className="card mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile</h3>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Full Name</dt>
            <dd className="mt-1 text-sm text-gray-900">{user?.full_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Email</dt>
            <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Role</dt>
            <dd className="mt-1 text-sm text-gray-900 capitalize">
              {user?.role}
            </dd>
          </div>
        </dl>
      </div>

      {/* Risk Weights (Admin only) */}
      {user?.role === "admin" && settings && (
        <div className="card mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Risk Calculation Weights
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Configure how different factors contribute to overall risk scores
          </p>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(settings.risk_weights || {}).map(([key, value]) => (
              <div key={key}>
                <dt className="text-sm font-medium text-gray-500 capitalize">
                  {key.replace("_", " ")}
                </dt>
                <dd className="mt-1">
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold text-gray-900">
                      {((value as number) * 100).toFixed(0)}%
                    </span>
                  </div>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Risk Appetite Configuration (Admin only) */}
      {user?.role === "admin" && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <ShieldCheckIcon className="h-6 w-6 text-primary-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Risk Appetite Configuration
              </h3>
            </div>
            {appetiteSaved && (
              <span className="flex items-center text-green-600 text-sm">
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Saved
              </span>
            )}
          </div>
          <p className="text-sm text-gray-500 mb-6">
            Define organizational risk tolerance thresholds. Risks exceeding these thresholds will be flagged for escalation.
          </p>

          <div className="space-y-6">
            {/* Overall Threshold */}
            <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Overall Risk Appetite Threshold
                </label>
                <span className="text-lg font-bold text-primary-600">{riskAppetite.overall_threshold}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={riskAppetite.overall_threshold}
                onChange={(e) => handleAppetiteChange("overall_threshold", parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low (0)</span>
                <span>Medium (50)</span>
                <span>High (100)</span>
              </div>
            </div>

            {/* Category-Specific Thresholds */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Category-Specific Thresholds
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { key: "strategic_threshold", label: "Strategic Risk", color: "indigo" },
                  { key: "operational_threshold", label: "Operational Risk", color: "blue" },
                  { key: "financial_threshold", label: "Financial Risk", color: "emerald" },
                  { key: "compliance_threshold", label: "Compliance Risk", color: "violet" },
                  { key: "cyber_threshold", label: "Cyber Risk", color: "red" },
                ].map((item) => (
                  <div key={item.key} className="border rounded-lg p-3 dark:border-dark-600">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm text-gray-600 dark:text-gray-400">{item.label}</label>
                      <span className="font-semibold">{riskAppetite[item.key as keyof typeof riskAppetite]}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={riskAppetite[item.key as keyof typeof riskAppetite] as number}
                      onChange={(e) => handleAppetiteChange(item.key, parseInt(e.target.value))}
                      className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Review Settings */}
            <div className="border-t pt-4 dark:border-dark-600">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Review & Escalation Settings
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Default Review Frequency
                  </label>
                  <select
                    value={riskAppetite.review_frequency_days}
                    onChange={(e) => handleAppetiteChange("review_frequency_days", parseInt(e.target.value))}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-dark-700 dark:border-dark-600"
                  >
                    <option value={30}>Monthly (30 days)</option>
                    <option value={90}>Quarterly (90 days)</option>
                    <option value={180}>Semi-annually (180 days)</option>
                    <option value={365}>Annually (365 days)</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={riskAppetite.escalation_enabled}
                    onChange={(e) => handleAppetiteChange("escalation_enabled", e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    Auto-escalate risks exceeding appetite threshold
                  </label>
                </div>
              </div>
            </div>

            {/* Risk Matrix Preview */}
            <div className="border-t pt-4 dark:border-dark-600">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Risk Matrix Thresholds
              </h4>
              <div className="grid grid-cols-5 gap-1 max-w-md">
                {[5, 4, 3, 2, 1].map((impact) => (
                  [1, 2, 3, 4, 5].map((likelihood) => {
                    const score = likelihood * impact * 4;
                    const isAboveThreshold = score > riskAppetite.overall_threshold;
                    return (
                      <div
                        key={`${likelihood}-${impact}`}
                        className={`h-8 rounded flex items-center justify-center text-xs font-medium text-white ${
                          score >= 80
                            ? "bg-red-500"
                            : score >= 60
                              ? "bg-orange-500"
                              : score >= 40
                                ? "bg-yellow-500"
                                : "bg-green-500"
                        } ${isAboveThreshold ? "ring-2 ring-red-600 ring-offset-1" : ""}`}
                        title={`L:${likelihood} x I:${impact} = ${score}`}
                      >
                        {score}
                      </div>
                    );
                  })
                ))}
              </div>
              <div className="flex items-center mt-2 text-xs text-gray-500">
                <ExclamationTriangleIcon className="h-4 w-4 text-red-500 mr-1" />
                Cells with red border exceed the overall appetite threshold
              </div>
            </div>

            <div className="flex justify-end">
              <button onClick={saveAppetite} className="btn-primary">
                Save Risk Appetite Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tenant Info (Admin only) */}
      {user?.role === "admin" && settings && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            Organization
          </h3>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Tenant Name</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">
                {settings.tenant_name}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Tenant ID</dt>
              <dd className="mt-1 text-sm text-gray-500 font-mono text-xs">
                {settings.tenant_id}
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
