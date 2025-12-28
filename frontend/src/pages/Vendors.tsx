import { useState } from "react";
import {
  TruckIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  DocumentCheckIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";

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

// Mock vendors data
const mockVendors = [
  {
    id: "1",
    name: "CloudSecure Inc.",
    tier: "critical" as const,
    category: "Cloud Infrastructure",
    riskScore: 25,
    riskLevel: "low" as const,
    lastAssessment: "2024-10-15",
    nextAssessment: "2025-04-15",
    certifications: ["SOC 2 Type II", "ISO 27001", "FedRAMP"],
    contractEnd: "2025-12-31",
    dataAccess: "Customer PII",
    questionnaireStatus: "completed",
    contactName: "John Smith",
    contactEmail: "john@cloudsecure.com",
  },
  {
    id: "2",
    name: "DataFlow Analytics",
    tier: "high" as const,
    category: "Analytics Platform",
    riskScore: 45,
    riskLevel: "medium" as const,
    lastAssessment: "2024-08-20",
    nextAssessment: "2025-02-20",
    certifications: ["SOC 2 Type II"],
    contractEnd: "2025-06-30",
    dataAccess: "Aggregated Metrics",
    questionnaireStatus: "pending",
    contactName: "Jane Doe",
    contactEmail: "jane@dataflow.io",
  },
  {
    id: "3",
    name: "PaySecure Gateway",
    tier: "critical" as const,
    category: "Payment Processing",
    riskScore: 18,
    riskLevel: "low" as const,
    lastAssessment: "2024-11-01",
    nextAssessment: "2025-05-01",
    certifications: ["PCI-DSS Level 1", "SOC 2 Type II", "ISO 27001"],
    contractEnd: "2026-03-31",
    dataAccess: "Payment Card Data",
    questionnaireStatus: "completed",
    contactName: "Mike Johnson",
    contactEmail: "mike@paysecure.com",
  },
  {
    id: "4",
    name: "TalentHub HR",
    tier: "medium" as const,
    category: "HR Management",
    riskScore: 62,
    riskLevel: "high" as const,
    lastAssessment: "2024-03-15",
    nextAssessment: "2024-09-15",
    certifications: ["SOC 2 Type I"],
    contractEnd: "2025-01-31",
    dataAccess: "Employee PII",
    questionnaireStatus: "overdue",
    contactName: "Sarah Wilson",
    contactEmail: "sarah@talenthub.io",
  },
  {
    id: "5",
    name: "SecureComms",
    tier: "high" as const,
    category: "Communications",
    riskScore: 35,
    riskLevel: "medium" as const,
    lastAssessment: "2024-09-01",
    nextAssessment: "2025-03-01",
    certifications: ["SOC 2 Type II", "HIPAA"],
    contractEnd: "2025-09-30",
    dataAccess: "Internal Communications",
    questionnaireStatus: "completed",
    contactName: "Tom Brown",
    contactEmail: "tom@securecomms.net",
  },
];

export default function Vendors() {
  const [searchQuery, setSearchQuery] = useState("");
  const [tierFilter, setTierFilter] = useState<string | null>(null);

  const filteredVendors = mockVendors.filter((vendor) => {
    const matchesSearch =
      vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTier = !tierFilter || vendor.tier === tierFilter;
    return matchesSearch && matchesTier;
  });

  const assessmentsDue = mockVendors.filter(
    (v) => new Date(v.nextAssessment) <= new Date(),
  ).length;
  const highRiskVendors = mockVendors.filter(
    (v) => v.riskLevel === "high",
  ).length;
  const pendingQuestionnaires = mockVendors.filter(
    (v) =>
      v.questionnaireStatus === "pending" ||
      v.questionnaireStatus === "overdue",
  ).length;

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
                {mockVendors.length}
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
              <p className="text-sm text-gray-500">Pending Questionnaires</p>
              <p className="text-2xl font-bold text-blue-600">
                {pendingQuestionnaires}
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
          const tierConfig = TIER_CONFIG[vendor.tier];
          const riskConfig = RISK_CONFIG[vendor.riskLevel];
          const isAssessmentDue = new Date(vendor.nextAssessment) <= new Date();

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
                        {vendor.name}
                      </h3>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${tierConfig.color}`}
                      >
                        {tierConfig.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{vendor.category}</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1">
                      <div
                        className={`w-3 h-3 rounded-full ${riskConfig.color}`}
                      ></div>
                      <span
                        className={`text-sm font-medium ${riskConfig.textColor}`}
                      >
                        {vendor.riskScore}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">{riskConfig.label}</p>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Data Access</span>
                    <p className="font-medium text-gray-900">
                      {vendor.dataAccess}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Contract Ends</span>
                    <p className="font-medium text-gray-900">
                      {new Date(vendor.contractEnd).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Last Assessment</span>
                    <p className="font-medium text-gray-900">
                      {new Date(vendor.lastAssessment).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Next Assessment</span>
                    <p
                      className={`font-medium ${isAssessmentDue ? "text-red-600" : "text-gray-900"}`}
                    >
                      {new Date(vendor.nextAssessment).toLocaleDateString()}
                      {isAssessmentDue && " (Overdue)"}
                    </p>
                  </div>
                </div>

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

                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center text-sm">
                    <span className="text-gray-500">Questionnaire:</span>
                    <span
                      className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${
                        vendor.questionnaireStatus === "completed"
                          ? "bg-green-100 text-green-800"
                          : vendor.questionnaireStatus === "pending"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-red-100 text-red-800"
                      }`}
                    >
                      {vendor.questionnaireStatus === "completed"
                        ? "Completed"
                        : vendor.questionnaireStatus === "pending"
                          ? "Pending"
                          : "Overdue"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  {vendor.contactName} • {vendor.contactEmail}
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

      {filteredVendors.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <TruckIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No vendors found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search or add a new vendor.
          </p>
        </div>
      )}
    </div>
  );
}
