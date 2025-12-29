import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  TruckIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  DocumentCheckIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";
import { vendorsApi } from "../services/api";

interface Vendor {
  id: string;
  vendor_ref: string;
  legal_name: string;
  trading_name: string | null;
  tier: "critical" | "high" | "medium" | "low";
  status: string;
  category: string;
  risk_score: number;
  residual_risk: "high" | "medium" | "low";
  last_assessment_date: string | null;
  next_assessment_date: string | null;
  certifications: string[];
  has_data_access: boolean;
  data_types: string[];
  primary_contact_name: string | null;
  primary_contact_email: string | null;
}

const TIER_CONFIG = {
  critical: {
    label: "Critical",
    color: "bg-red-100 text-red-800",
    description: "Core business functions",
  },
  high: {
    label: "High",
    color: "bg-orange-100 text-orange-800",
    description: "Important operations",
  },
  medium: {
    label: "Medium",
    color: "bg-amber-100 text-amber-800",
    description: "Standard services",
  },
  low: {
    label: "Low",
    color: "bg-green-100 text-green-800",
    description: "Non-critical services",
  },
};

const RISK_CONFIG = {
  high: { label: "High Risk", color: "bg-red-500", textColor: "text-red-700" },
  medium: {
    label: "Medium Risk",
    color: "bg-amber-500",
    textColor: "text-amber-700",
  },
  low: {
    label: "Low Risk",
    color: "bg-green-500",
    textColor: "text-green-700",
  },
};

export default function Vendors() {
  const [searchQuery, setSearchQuery] = useState("");
  const [tierFilter, setTierFilter] = useState<string | null>(null);

  const { data: vendorsData, isLoading, error } = useQuery({
    queryKey: ["vendors"],
    queryFn: () => vendorsApi.list(),
  });

  const vendors: Vendor[] = vendorsData?.data || [];

  const filteredVendors = vendors.filter((vendor) => {
    const matchesSearch =
      vendor.legal_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (vendor.category?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
    const matchesTier = !tierFilter || vendor.tier === tierFilter;
    return matchesSearch && matchesTier;
  });

  const assessmentsDue = vendors.filter(
    (v) => v.next_assessment_date && new Date(v.next_assessment_date) <= new Date(),
  ).length;
  const highRiskVendors = vendors.filter(
    (v) => v.residual_risk === "high",
  ).length;
  const activeVendors = vendors.filter(
    (v) => v.status === "active",
  ).length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
        <span className="ml-3 text-gray-600">Loading vendors...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading vendors. Please try again.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <TruckIcon className="h-8 w-8 mr-3 text-amber-600" />
            Vendor Risk Management
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Assess, monitor, and manage third-party vendor risks across your
            organization.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button className="inline-flex items-center rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-500">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Vendor
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Vendors</p>
              <p className="text-2xl font-bold text-gray-900">
                {vendors.length}
              </p>
            </div>
            <div className="p-3 bg-amber-100 rounded-lg">
              <TruckIcon className="h-6 w-6 text-amber-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">High Risk</p>
              <p className="text-2xl font-bold text-red-600">
                {highRiskVendors}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-amber-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Assessments Due</p>
              <p className="text-2xl font-bold text-amber-600">
                {assessmentsDue}
              </p>
            </div>
            <div className="p-3 bg-amber-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-amber-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-blue-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Vendors</p>
              <p className="text-2xl font-bold text-blue-600">
                {activeVendors}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <DocumentCheckIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search vendors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
            />
          </div>
        </div>
        <select
          value={tierFilter || ""}
          onChange={(e) => setTierFilter(e.target.value || null)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
        >
          <option value="">All Tiers</option>
          {Object.entries(TIER_CONFIG).map(([key, config]) => (
            <option key={key} value={key}>
              {config.label}
            </option>
          ))}
        </select>
      </div>

      {/* Vendors Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredVendors.map((vendor) => {
          const tierConfig = TIER_CONFIG[vendor.tier] || TIER_CONFIG.medium;
          const riskConfig = RISK_CONFIG[vendor.residual_risk] || RISK_CONFIG.medium;
          const isAssessmentDue = vendor.next_assessment_date && new Date(vendor.next_assessment_date) <= new Date();

          return (
            <div
              key={vendor.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {vendor.legal_name}
                      </h3>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${tierConfig.color}`}
                      >
                        {tierConfig.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{vendor.category || "Uncategorized"}</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1">
                      <div
                        className={`w-3 h-3 rounded-full ${riskConfig.color}`}
                      ></div>
                      <span
                        className={`text-sm font-medium ${riskConfig.textColor}`}
                      >
                        {vendor.risk_score || 0}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">{riskConfig.label}</p>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Data Access</span>
                    <p className="font-medium text-gray-900">
                      {vendor.has_data_access ? "Yes" : "No"}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Status</span>
                    <p className="font-medium text-gray-900">
                      {vendor.status || "N/A"}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Last Assessment</span>
                    <p className="font-medium text-gray-900">
                      {vendor.last_assessment_date ? new Date(vendor.last_assessment_date).toLocaleDateString() : "Never"}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Next Assessment</span>
                    <p
                      className={`font-medium ${isAssessmentDue ? "text-red-600" : "text-gray-900"}`}
                    >
                      {vendor.next_assessment_date ? new Date(vendor.next_assessment_date).toLocaleDateString() : "Not scheduled"}
                      {isAssessmentDue && " (Overdue)"}
                    </p>
                  </div>
                </div>

                {vendor.certifications && vendor.certifications.length > 0 && (
                  <div className="mt-4">
                    <span className="text-sm text-gray-500">Certifications</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {vendor.certifications.map((cert) => (
                        <span
                          key={cert}
                          className="inline-flex items-center px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded"
                        >
                          <CheckBadgeIcon className="h-3 w-3 mr-1" />
                          {cert}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {vendor.data_types && vendor.data_types.length > 0 && (
                  <div className="mt-4">
                    <span className="text-sm text-gray-500">Data Types:</span>
                    <span className="ml-2 text-sm text-gray-700">
                      {vendor.data_types.join(", ")}
                    </span>
                  </div>
                )}
              </div>

              <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  {vendor.primary_contact_name || "No contact"} {vendor.primary_contact_email && `• ${vendor.primary_contact_email}`}
                </div>
                <div className="flex space-x-3">
                  <button className="text-sm text-gray-600 hover:text-gray-900">
                    View Profile
                  </button>
                  <button className="text-sm text-amber-600 hover:text-amber-700 font-medium">
                    Start Assessment
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredVendors.length === 0 && !isLoading && (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <TruckIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No vendors found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {vendors.length === 0
              ? "Get started by adding your first vendor."
              : "Try adjusting your search or filters."}
          </p>
        </div>
      )}
    </div>
  );
}
