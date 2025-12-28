import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { russianComplianceApi } from "../services/api";
import {
  BuildingOfficeIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  ServerStackIcon,
  ClipboardDocumentCheckIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";

interface Company {
  id: string;
  inn: string;
  full_name: string;
  short_name: string | null;
  legal_form: string | null;
  legal_address: string | null;
  is_pdn_operator: boolean;
  is_kii_subject: boolean;
  is_financial_org: boolean;
}

interface DashboardStats {
  total_documents: number;
  completed_documents: number;
  in_progress_documents: number;
  overdue_documents: number;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  ispdn_systems: number;
  responsible_persons: number;
  compliance_score: number;
}

interface Framework {
  code: string;
  name: string;
  full_name: string;
  description: string;
  regulator: string;
  mandatory: boolean;
}

const PROTECTION_LEVEL_COLORS: Record<string, string> = {
  "УЗ-1": "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  "УЗ-2": "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  "УЗ-3": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  "УЗ-4": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
};

export default function RussianCompliance() {
  const queryClient = useQueryClient();
  const [selectedCompanyId, setSelectedCompanyId] = useState<string | null>(null);
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [innInput, setInnInput] = useState("");
  const [lookupResult, setLookupResult] = useState<Record<string, unknown> | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "ispdn" | "documents" | "tasks">("overview");

  // Fetch companies
  const { data: companies = [], isLoading: companiesLoading } = useQuery({
    queryKey: ["russian-companies"],
    queryFn: async () => {
      const response = await russianComplianceApi.companies.list();
      return response.data as Company[];
    },
  });

  // Fetch frameworks
  const { data: frameworks = [] } = useQuery({
    queryKey: ["russian-frameworks"],
    queryFn: async () => {
      const response = await russianComplianceApi.frameworks();
      return response.data as Framework[];
    },
  });

  // Fetch dashboard for selected company
  const { data: dashboard } = useQuery({
    queryKey: ["russian-dashboard", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return null;
      const response = await russianComplianceApi.dashboard(selectedCompanyId);
      return response.data as DashboardStats;
    },
    enabled: !!selectedCompanyId,
  });

  // Fetch ISPDN systems for selected company
  const { data: ispdnSystems = [] } = useQuery({
    queryKey: ["russian-ispdn", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return [];
      const response = await russianComplianceApi.ispdn.list(selectedCompanyId);
      return response.data;
    },
    enabled: !!selectedCompanyId,
  });

  // Fetch responsible persons
  const { data: responsiblePersons = [] } = useQuery({
    queryKey: ["russian-responsible", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return [];
      const response = await russianComplianceApi.responsiblePersons.list(selectedCompanyId);
      return response.data;
    },
    enabled: !!selectedCompanyId,
  });

  // Fetch documents
  const { data: documents = [] } = useQuery({
    queryKey: ["russian-documents", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return [];
      const response = await russianComplianceApi.documents.list(selectedCompanyId);
      return response.data;
    },
    enabled: !!selectedCompanyId,
  });

  // Create company mutation
  const createCompanyMutation = useMutation({
    mutationFn: (inn: string) => russianComplianceApi.companies.create(inn),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["russian-companies"] });
      setShowAddCompany(false);
      setInnInput("");
      setLookupResult(null);
    },
  });

  // Lookup INN
  const handleLookupINN = async () => {
    if (!innInput || innInput.length < 10) return;
    setLookupLoading(true);
    try {
      const response = await russianComplianceApi.companies.lookup(innInput);
      setLookupResult(response.data.data);
    } catch (error) {
      console.error("INN lookup failed:", error);
    } finally {
      setLookupLoading(false);
    }
  };

  const selectedCompany = companies.find((c) => c.id === selectedCompanyId);

  // Select first company by default
  if (companies.length > 0 && !selectedCompanyId) {
    setSelectedCompanyId(companies[0].id);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Russian Compliance
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            152-ФЗ, 187-ФЗ, ГОСТ Р 57580, ФСТЭК Requirements
          </p>
        </div>
        <button
          onClick={() => setShowAddCompany(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Company
        </button>
      </div>

      {/* Add Company Modal */}
      {showAddCompany && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-dark-800 rounded-lg shadow-xl w-full max-w-lg p-6">
            <h2 className="text-xl font-bold mb-4">Add Company by INN</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  INN (ИНН организации)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={innInput}
                    onChange={(e) => setInnInput(e.target.value.replace(/\D/g, "").slice(0, 12))}
                    placeholder="Введите ИНН (10 или 12 цифр)"
                    className="flex-1 rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                  />
                  <button
                    onClick={handleLookupINN}
                    disabled={innInput.length < 10 || lookupLoading}
                    className="btn-secondary flex items-center"
                  >
                    <MagnifyingGlassIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {lookupLoading && (
                <div className="text-center py-4">
                  <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-500">Searching EGRUL...</p>
                </div>
              )}

              {lookupResult && (
                <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Company Found:</h3>
                  <dl className="space-y-1 text-sm">
                    <div>
                      <dt className="text-gray-500 inline">Name: </dt>
                      <dd className="inline font-medium">{lookupResult.full_name as string}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-500 inline">INN: </dt>
                      <dd className="inline">{lookupResult.inn as string}</dd>
                    </div>
                    {Boolean(lookupResult.ogrn) && (
                      <div>
                        <dt className="text-gray-500 inline">OGRN: </dt>
                        <dd className="inline">{String(lookupResult.ogrn)}</dd>
                      </div>
                    )}
                    {Boolean(lookupResult.legal_address) && (
                      <div>
                        <dt className="text-gray-500 inline">Address: </dt>
                        <dd className="inline">{String(lookupResult.legal_address)}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowAddCompany(false);
                    setInnInput("");
                    setLookupResult(null);
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => createCompanyMutation.mutate(innInput)}
                  disabled={!lookupResult || createCompanyMutation.isPending}
                  className="btn-primary"
                >
                  {createCompanyMutation.isPending ? "Creating..." : "Create Company"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Company Selector */}
      {companies.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-4">
            <BuildingOfficeIcon className="h-8 w-8 text-primary-600" />
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Select Company
              </label>
              <select
                value={selectedCompanyId || ""}
                onChange={(e) => setSelectedCompanyId(e.target.value)}
                className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
              >
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.short_name || company.full_name} (ИНН: {company.inn})
                  </option>
                ))}
              </select>
            </div>
            {selectedCompany && (
              <div className="flex gap-2">
                {selectedCompany.is_pdn_operator && (
                  <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full dark:bg-blue-900 dark:text-blue-200">
                    152-ФЗ
                  </span>
                )}
                {selectedCompany.is_kii_subject && (
                  <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full dark:bg-purple-900 dark:text-purple-200">
                    187-ФЗ КИИ
                  </span>
                )}
                {selectedCompany.is_financial_org && (
                  <span className="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-800 rounded-full dark:bg-emerald-900 dark:text-emerald-200">
                    ЦБ РФ
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* No Companies Message */}
      {!companiesLoading && companies.length === 0 && (
        <div className="card text-center py-12">
          <BuildingOfficeIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">
            No Companies Added
          </h2>
          <p className="text-gray-500 mb-6">
            Add a company by INN to start managing Russian compliance requirements.
          </p>
          <button
            onClick={() => setShowAddCompany(true)}
            className="btn-primary inline-flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Company
          </button>
        </div>
      )}

      {/* Dashboard */}
      {selectedCompanyId && dashboard && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Compliance Score</p>
                  <p className="text-3xl font-bold text-primary-600">
                    {dashboard.compliance_score}%
                  </p>
                </div>
                <ShieldCheckIcon className="h-10 w-10 text-primary-200" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Documents</p>
                  <p className="text-2xl font-bold">
                    {dashboard.completed_documents}/{dashboard.total_documents}
                  </p>
                </div>
                <DocumentTextIcon className="h-10 w-10 text-blue-200" />
              </div>
              {dashboard.overdue_documents > 0 && (
                <p className="text-xs text-red-600 mt-2">
                  {dashboard.overdue_documents} overdue
                </p>
              )}
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Tasks</p>
                  <p className="text-2xl font-bold">
                    {dashboard.completed_tasks}/{dashboard.total_tasks}
                  </p>
                </div>
                <ClipboardDocumentCheckIcon className="h-10 w-10 text-green-200" />
              </div>
              {dashboard.overdue_tasks > 0 && (
                <p className="text-xs text-red-600 mt-2">
                  {dashboard.overdue_tasks} overdue
                </p>
              )}
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">ISPDN Systems</p>
                  <p className="text-2xl font-bold">{dashboard.ispdn_systems}</p>
                </div>
                <ServerStackIcon className="h-10 w-10 text-purple-200" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Responsible</p>
                  <p className="text-2xl font-bold">{dashboard.responsible_persons}</p>
                </div>
                <UserGroupIcon className="h-10 w-10 text-orange-200" />
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 dark:border-dark-600">
            <nav className="flex gap-8">
              {[
                { id: "overview", label: "Overview", icon: ShieldCheckIcon },
                { id: "ispdn", label: "ISPDN Systems", icon: ServerStackIcon },
                { id: "documents", label: "Documents", icon: DocumentTextIcon },
                { id: "tasks", label: "Tasks", icon: ClipboardDocumentCheckIcon },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? "border-primary-500 text-primary-600"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <tab.icon className="h-5 w-5" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Applicable Frameworks */}
                <div className="card">
                  <h3 className="text-lg font-medium mb-4">Applicable Frameworks</h3>
                  <div className="space-y-3">
                    {frameworks.map((fw) => (
                      <div
                        key={fw.code}
                        className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">{fw.name}</p>
                          <p className="text-sm text-gray-500">{fw.description}</p>
                        </div>
                        {fw.mandatory && (
                          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                            Mandatory
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Responsible Persons */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium">Responsible Persons</h3>
                    <button className="btn-secondary text-sm">Add Person</button>
                  </div>
                  {responsiblePersons.length > 0 ? (
                    <div className="space-y-3">
                      {responsiblePersons.map((person: { id: string; role_name_ru: string; full_name: string; email: string; training_completed: boolean }) => (
                        <div
                          key={person.id}
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-700 rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{person.role_name_ru}</p>
                            <p className="text-sm text-gray-500">{person.full_name}</p>
                            <p className="text-xs text-gray-400">{person.email}</p>
                          </div>
                          {person.training_completed ? (
                            <CheckCircleIcon className="h-5 w-5 text-green-500" />
                          ) : (
                            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-8">
                      No responsible persons assigned yet.
                    </p>
                  )}
                </div>

                {/* Quick Actions */}
                <div className="card lg:col-span-2">
                  <h3 className="text-lg font-medium mb-4">Quick Actions</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-left hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                      <DocumentTextIcon className="h-8 w-8 text-blue-600 mb-2" />
                      <p className="font-medium text-blue-900 dark:text-blue-100">
                        Generate 152-ФЗ Package
                      </p>
                      <p className="text-xs text-blue-600 dark:text-blue-300">
                        All required documents
                      </p>
                    </button>
                    <button className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-left hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
                      <ServerStackIcon className="h-8 w-8 text-purple-600 mb-2" />
                      <p className="font-medium text-purple-900 dark:text-purple-100">
                        Add ISPDN System
                      </p>
                      <p className="text-xs text-purple-600 dark:text-purple-300">
                        Register new system
                      </p>
                    </button>
                    <button className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg text-left hover:bg-emerald-100 dark:hover:bg-emerald-900/30 transition-colors">
                      <ShieldCheckIcon className="h-8 w-8 text-emerald-600 mb-2" />
                      <p className="font-medium text-emerald-900 dark:text-emerald-100">
                        Calculate УЗ Level
                      </p>
                      <p className="text-xs text-emerald-600 dark:text-emerald-300">
                        Protection level calc
                      </p>
                    </button>
                    <button className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg text-left hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors">
                      <UserGroupIcon className="h-8 w-8 text-orange-600 mb-2" />
                      <p className="font-medium text-orange-900 dark:text-orange-100">
                        Assign Responsible
                      </p>
                      <p className="text-xs text-orange-600 dark:text-orange-300">
                        Required roles
                      </p>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ISPDN Tab */}
            {activeTab === "ispdn" && (
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium">ISPDN Systems</h3>
                  <button className="btn-primary flex items-center">
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Add ISPDN
                  </button>
                </div>

                {ispdnSystems.length > 0 ? (
                  <div className="space-y-4">
                    {ispdnSystems.map((system: {
                      id: string;
                      name: string;
                      description: string;
                      protection_level: string;
                      pdn_category: string;
                      subject_count: string;
                      is_certified: boolean;
                    }) => (
                      <div
                        key={system.id}
                        className="border rounded-lg p-4 dark:border-dark-600 hover:border-primary-300 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-lg">{system.name}</h4>
                            <p className="text-sm text-gray-500 mt-1">
                              {system.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                PROTECTION_LEVEL_COLORS[system.protection_level] ||
                                "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {system.protection_level}
                            </span>
                            {system.is_certified && (
                              <CheckCircleIcon className="h-5 w-5 text-green-500" />
                            )}
                          </div>
                        </div>
                        <div className="flex gap-4 mt-4 text-sm">
                          <div>
                            <span className="text-gray-500">Category: </span>
                            <span className="font-medium">{system.pdn_category}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Subjects: </span>
                            <span className="font-medium">{system.subject_count}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <ServerStackIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">
                      No ISPDN systems registered. Add your first system to determine
                      protection level.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Documents Tab */}
            {activeTab === "documents" && (
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium">Compliance Documents</h3>
                  <button className="btn-primary flex items-center">
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Generate Documents
                  </button>
                </div>

                {documents.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b dark:border-dark-600">
                          <th className="text-left py-3 px-4 font-medium text-gray-500">
                            Document
                          </th>
                          <th className="text-left py-3 px-4 font-medium text-gray-500">
                            Framework
                          </th>
                          <th className="text-left py-3 px-4 font-medium text-gray-500">
                            Status
                          </th>
                          <th className="text-left py-3 px-4 font-medium text-gray-500">
                            Progress
                          </th>
                          <th className="text-left py-3 px-4 font-medium text-gray-500">
                            Due Date
                          </th>
                          <th className="py-3 px-4"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {documents.map((doc: {
                          id: string;
                          title: string;
                          document_type: string;
                          framework: string;
                          status: string;
                          completion_percent: number;
                          due_date: string | null;
                        }) => (
                          <tr
                            key={doc.id}
                            className="border-b dark:border-dark-600 hover:bg-gray-50 dark:hover:bg-dark-700"
                          >
                            <td className="py-3 px-4">
                              <div>
                                <p className="font-medium">{doc.title}</p>
                                <p className="text-xs text-gray-500">{doc.document_type}</p>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded dark:bg-primary-900 dark:text-primary-200">
                                {doc.framework}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`px-2 py-1 text-xs font-medium rounded ${
                                  doc.status === "УТВЕРЖДЁН"
                                    ? "bg-green-100 text-green-800"
                                    : doc.status === "ЧЕРНОВИК"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-gray-100 text-gray-800"
                                }`}
                              >
                                {doc.status}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <div className="w-24">
                                <div className="flex items-center gap-2">
                                  <div className="flex-1 h-2 bg-gray-200 rounded-full dark:bg-dark-600">
                                    <div
                                      className="h-2 bg-primary-500 rounded-full"
                                      style={{ width: `${doc.completion_percent}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-xs text-gray-500">
                                    {doc.completion_percent}%
                                  </span>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              {doc.due_date ? (
                                <span className="flex items-center text-sm text-gray-500">
                                  <ClockIcon className="h-4 w-4 mr-1" />
                                  {new Date(doc.due_date).toLocaleDateString("ru-RU")}
                                </span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              <button className="text-primary-600 hover:text-primary-800">
                                <ChevronRightIcon className="h-5 w-5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">
                      No documents generated yet. Click "Generate Documents" to create
                      compliance documents from templates.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Tasks Tab */}
            {activeTab === "tasks" && (
              <div className="card">
                <h3 className="text-lg font-medium mb-6">Compliance Tasks</h3>
                <div className="text-center py-12">
                  <ClipboardDocumentCheckIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">
                    No tasks assigned yet. Tasks will be created automatically when
                    documents are generated.
                  </p>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
