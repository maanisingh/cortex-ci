import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ExclamationCircleIcon,
  PlusIcon,
  BellAlertIcon,
  ShieldExclamationIcon,
  ClockIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  FireIcon,
} from "@heroicons/react/24/outline";
import { incidentsApi } from "../services/api";

interface Incident {
  id: string;
  incident_ref: string;
  title: string;
  description: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "new" | "investigating" | "contained" | "eradicated" | "recovered" | "closed";
  detected_at: string;
  assigned_to: string | null;
  affected_systems: string[];
  is_breach: boolean;
  affected_records_count: number;
}

const SEVERITY_CONFIG = {
  critical: {
    label: "P1 - Critical",
    color: "bg-red-600 text-white",
    borderColor: "border-red-500",
  },
  high: {
    label: "P2 - High",
    color: "bg-orange-500 text-white",
    borderColor: "border-orange-500",
  },
  medium: {
    label: "P3 - Medium",
    color: "bg-amber-500 text-white",
    borderColor: "border-amber-500",
  },
  low: {
    label: "P4 - Low",
    color: "bg-blue-500 text-white",
    borderColor: "border-blue-500",
  },
};

const STATUS_CONFIG = {
  new: { label: "New", color: "bg-red-100 text-red-800", icon: BellAlertIcon },
  investigating: {
    label: "Investigating",
    color: "bg-amber-100 text-amber-800",
    icon: ArrowPathIcon,
  },
  contained: {
    label: "Contained",
    color: "bg-blue-100 text-blue-800",
    icon: ShieldExclamationIcon,
  },
  eradicated: {
    label: "Eradicated",
    color: "bg-purple-100 text-purple-800",
    icon: FireIcon,
  },
  recovered: {
    label: "Recovered",
    color: "bg-green-100 text-green-800",
    icon: CheckCircleIcon,
  },
  closed: {
    label: "Closed",
    color: "bg-gray-100 text-gray-800",
    icon: CheckCircleIcon,
  },
};

function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) return `${diffDays}d ago`;
  if (diffHours > 0) return `${diffHours}h ago`;
  return "Just now";
}

export default function Incidents() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const { data: incidentsData, isLoading, error } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => incidentsApi.list(),
  });

  const incidents: Incident[] = incidentsData?.data || [];

  const filteredIncidents = incidents.filter((incident) => {
    return !statusFilter || incident.status === statusFilter;
  });

  const activeIncidents = incidents.filter(
    (i) => !["closed", "recovered"].includes(i.status),
  );
  const criticalActive = activeIncidents.filter(
    (i) => i.severity === "critical",
  ).length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
        <span className="ml-3 text-gray-600">Loading incidents...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading incidents. Please try again.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <ExclamationCircleIcon className="h-8 w-8 mr-3 text-red-600" />
            Incident Management
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Report, track, and respond to security incidents across your
            organization.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button className="inline-flex items-center rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500">
            <PlusIcon className="h-5 w-5 mr-2" />
            Report Incident
          </button>
        </div>
      </div>

      {/* Active Incident Alert */}
      {criticalActive > 0 && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <div className="flex items-center">
            <FireIcon className="h-6 w-6 text-red-500 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">
                {criticalActive} Critical Incident
                {criticalActive > 1 ? "s" : ""} Active
              </h3>
              <p className="text-sm text-red-700">
                Immediate attention required. Click to view details.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Incidents</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeIncidents.length}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <BellAlertIcon className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Investigating</p>
              <p className="text-2xl font-bold text-amber-600">
                {incidents.filter((i) => i.status === "investigating").length}
              </p>
            </div>
            <div className="p-3 bg-amber-100 rounded-lg">
              <ArrowPathIcon className="h-6 w-6 text-amber-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Contained</p>
              <p className="text-2xl font-bold text-blue-600">
                {incidents.filter((i) => i.status === "contained").length}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <ShieldExclamationIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Resolved This Month</p>
              <p className="text-2xl font-bold text-green-600">
                {incidents.filter(
                  (i) => i.status === "closed" || i.status === "recovered",
                ).length}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-6 overflow-x-auto">
          {[
            { key: null, label: "All Incidents" },
            { key: "new", label: "New" },
            { key: "investigating", label: "Investigating" },
            { key: "contained", label: "Contained" },
            { key: "eradicated", label: "Eradicated" },
            { key: "recovered", label: "Recovered" },
            { key: "closed", label: "Closed" },
          ].map((tab) => (
            <button
              key={tab.key || "all"}
              onClick={() => setStatusFilter(tab.key)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                statusFilter === tab.key
                  ? "border-red-500 text-red-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Incidents List */}
      <div className="space-y-4">
        {filteredIncidents.map((incident) => {
          const severityConfig = SEVERITY_CONFIG[incident.severity] || SEVERITY_CONFIG.medium;
          const statusConfig = STATUS_CONFIG[incident.status] || STATUS_CONFIG.new;
          const StatusIcon = statusConfig.icon;

          return (
            <div
              key={incident.id}
              className={`bg-white rounded-lg shadow-sm border-l-4 ${severityConfig.borderColor} overflow-hidden hover:shadow-md transition-shadow`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-mono text-gray-500">
                        {incident.incident_ref}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${severityConfig.color}`}
                      >
                        {severityConfig.label}
                      </span>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusConfig.color}`}
                      >
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {statusConfig.label}
                      </span>
                      {incident.is_breach && (
                        <span className="px-2 py-0.5 bg-red-600 text-white rounded text-xs font-medium">
                          Data Breach
                        </span>
                      )}
                    </div>
                    <h3 className="mt-2 text-lg font-semibold text-gray-900">
                      {incident.title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600">
                      {incident.description}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        Detected: {incident.detected_at ? getTimeAgo(incident.detected_at) : "Unknown"}
                      </span>
                      <span>Category: {incident.category || "Unknown"}</span>
                      <span>Ref: {incident.incident_ref || "Unassigned"}</span>
                      {incident.affected_records_count > 0 && (
                        <span className="text-red-600">
                          {incident.affected_records_count.toLocaleString()} records
                          affected
                        </span>
                      )}
                    </div>
                    {incident.affected_systems && incident.affected_systems.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {incident.affected_systems.map((system) => (
                          <span
                            key={system}
                            className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                          >
                            {system}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex justify-end space-x-3">
                <button className="text-sm text-gray-600 hover:text-gray-900">
                  View Timeline
                </button>
                <button className="text-sm text-red-600 hover:text-red-700 font-medium">
                  Manage Incident
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filteredIncidents.length === 0 && !isLoading && (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No incidents found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {incidents.length === 0
              ? "No incidents recorded. Great job keeping things secure!"
              : statusFilter
                ? "No incidents match your filter."
                : "No active incidents."}
          </p>
        </div>
      )}
    </div>
  );
}
