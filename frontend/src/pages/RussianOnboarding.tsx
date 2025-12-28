import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { russianComplianceApi } from "../services/api";
import {
  BuildingOfficeIcon,
  UserGroupIcon,
  ServerStackIcon,
  DocumentTextIcon,
  ClipboardDocumentCheckIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";

interface ResponsiblePerson {
  role: string;
  full_name: string;
  email: string;
  position: string;
  phone: string;
}

interface ISPDNSystem {
  name: string;
  description: string;
  pdn_category: string;
  subject_count: string;
  threat_type: string;
  processing_purposes: string[];
  subject_categories: string[];
  pdn_types: string[];
}

const STEPS = [
  { id: 1, name: "Company", title: "Company Registration", icon: BuildingOfficeIcon },
  { id: 2, name: "Responsible", title: "Responsible Persons", icon: UserGroupIcon },
  { id: 3, name: "ISPDN", title: "ISPDN Systems", icon: ServerStackIcon },
  { id: 4, name: "Documents", title: "Document Package", icon: DocumentTextIcon },
  { id: 5, name: "Tasks", title: "Tasks & Timeline", icon: ClipboardDocumentCheckIcon },
];

const PDN_CATEGORIES = [
  { value: "СПЕЦИАЛЬНЫЕ", label: "Special (race, politics, health, etc.)" },
  { value: "БИОМЕТРИЧЕСКИЕ", label: "Biometric" },
  { value: "ОБЩЕДОСТУПНЫЕ", label: "Public" },
  { value: "ИНЫЕ", label: "Other" },
];

const SUBJECT_COUNTS = [
  { value: "<1000", label: "Less than 1,000" },
  { value: "<100000", label: "1,000 - 100,000" },
  { value: ">100000", label: "More than 100,000" },
];

const THREAT_TYPES = [
  { value: "1", label: "Type 1 - Undocumented system software capabilities" },
  { value: "2", label: "Type 2 - Undocumented application software capabilities" },
  { value: "3", label: "Type 3 - No undocumented capabilities" },
];

const RESPONSIBLE_ROLES = [
  { value: "ОТВЕТСТВЕННЫЙ_ПДН", label: "PDN Responsible", required: true },
  { value: "АДМИНИСТРАТОР_ИБ", label: "Security Administrator", required: true },
  { value: "РУКОВОДИТЕЛЬ", label: "CEO / Director", required: false },
];

export default function RussianOnboarding() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Step 1: Company
  const [inn, setInn] = useState("");
  const [companyData, setCompanyData] = useState<Record<string, unknown> | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);

  // Step 2: Responsible Persons
  const [responsiblePersons, setResponsiblePersons] = useState<ResponsiblePerson[]>([
    { role: "ОТВЕТСТВЕННЫЙ_ПДН", full_name: "", email: "", position: "", phone: "" },
    { role: "АДМИНИСТРАТОР_ИБ", full_name: "", email: "", position: "", phone: "" },
  ]);

  // Step 3: ISPDN Systems
  const [ispdnSystems, setIspdnSystems] = useState<ISPDNSystem[]>([
    {
      name: "",
      description: "",
      pdn_category: "ИНЫЕ",
      subject_count: "<1000",
      threat_type: "3",
      processing_purposes: [],
      subject_categories: [],
      pdn_types: [],
    },
  ]);

  // Step 4: Documents
  const [generateAllDocs, setGenerateAllDocs] = useState(true);

  // Step 5: Tasks
  const [assignTasks, setAssignTasks] = useState(true);
  const [deadlineDays, setDeadlineDays] = useState(30);

  // Results
  const [onboardingResult, setOnboardingResult] = useState<Record<string, unknown> | null>(null);

  // Lookup company by INN
  const handleLookupINN = async () => {
    if (!inn || inn.length < 10) return;
    setLookupLoading(true);
    try {
      const response = await russianComplianceApi.companies.lookup(inn);
      if (response.data.found) {
        setCompanyData(response.data.data);
      } else {
        setCompanyData(null);
        alert("Company not found. Please check the INN.");
      }
    } catch (error) {
      console.error("INN lookup failed:", error);
    } finally {
      setLookupLoading(false);
    }
  };

  // Add ISPDN system
  const addISPDN = () => {
    setIspdnSystems([
      ...ispdnSystems,
      {
        name: "",
        description: "",
        pdn_category: "ИНЫЕ",
        subject_count: "<1000",
        threat_type: "3",
        processing_purposes: [],
        subject_categories: [],
        pdn_types: [],
      },
    ]);
  };

  // Remove ISPDN system
  const removeISPDN = (index: number) => {
    if (ispdnSystems.length > 1) {
      setIspdnSystems(ispdnSystems.filter((_, i) => i !== index));
    }
  };

  // Update ISPDN system
  const updateISPDN = (index: number, field: string, value: string) => {
    const updated = [...ispdnSystems];
    updated[index] = { ...updated[index], [field]: value };
    setIspdnSystems(updated);
  };

  // Update responsible person
  const updateResponsiblePerson = (index: number, field: string, value: string) => {
    const updated = [...responsiblePersons];
    updated[index] = { ...updated[index], [field]: value };
    setResponsiblePersons(updated);
  };

  // Submit onboarding
  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch("/api/v1/compliance/russian/onboarding/complete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          inn,
          pdn_responsible: responsiblePersons.find((p) => p.role === "ОТВЕТСТВЕННЫЙ_ПДН" && p.full_name)
            ? {
                role: "ОТВЕТСТВЕННЫЙ_ПДН",
                full_name: responsiblePersons.find((p) => p.role === "ОТВЕТСТВЕННЫЙ_ПДН")?.full_name,
                email: responsiblePersons.find((p) => p.role === "ОТВЕТСТВЕННЫЙ_ПДН")?.email,
                position: responsiblePersons.find((p) => p.role === "ОТВЕТСТВЕННЫЙ_ПДН")?.position,
                phone: responsiblePersons.find((p) => p.role === "ОТВЕТСТВЕННЫЙ_ПДН")?.phone,
              }
            : null,
          security_admin: responsiblePersons.find((p) => p.role === "АДМИНИСТРАТОР_ИБ" && p.full_name)
            ? {
                role: "АДМИНИСТРАТОР_ИБ",
                full_name: responsiblePersons.find((p) => p.role === "АДМИНИСТРАТОР_ИБ")?.full_name,
                email: responsiblePersons.find((p) => p.role === "АДМИНИСТРАТОР_ИБ")?.email,
                position: responsiblePersons.find((p) => p.role === "АДМИНИСТРАТОР_ИБ")?.position,
                phone: responsiblePersons.find((p) => p.role === "АДМИНИСТРАТОР_ИБ")?.phone,
              }
            : null,
          ispdn_systems: ispdnSystems.filter((s) => s.name).map((s) => ({
            name: s.name,
            description: s.description,
            pdn_category: s.pdn_category,
            subject_count: s.subject_count,
            threat_type: s.threat_type,
            processing_purposes: s.processing_purposes,
            subject_categories: s.subject_categories,
            pdn_types: s.pdn_types,
          })),
          generate_fz152_package: generateAllDocs,
          assign_tasks: assignTasks,
          task_deadline_days: deadlineDays,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setOnboardingResult(result);
        setCurrentStep(6); // Success step
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || "Failed to complete onboarding"}`);
      }
    } catch (error) {
      console.error("Onboarding failed:", error);
      alert("Failed to complete onboarding. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate protection level preview
  const getProtectionLevelPreview = (ispdn: ISPDNSystem): string => {
    const isSpecial = ispdn.pdn_category === "СПЕЦИАЛЬНЫЕ";
    const isBiometric = ispdn.pdn_category === "БИОМЕТРИЧЕСКИЕ";
    const isLargeScale = ispdn.subject_count === ">100000";
    const threatType = ispdn.threat_type;

    if (isSpecial || isBiometric) {
      if (threatType === "1" || isLargeScale) return "УЗ-1";
      if (threatType === "2") return "УЗ-2";
      return "УЗ-3";
    }

    if (isLargeScale) {
      if (threatType === "1") return "УЗ-1";
      if (threatType === "2") return "УЗ-2";
      return "УЗ-3";
    }

    if (threatType === "1") return "УЗ-2";
    if (threatType === "2") return "УЗ-3";
    return "УЗ-4";
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return companyData !== null;
      case 2:
        return responsiblePersons.some((p) => p.full_name && p.email);
      case 3:
        return ispdnSystems.some((s) => s.name);
      case 4:
        return true;
      case 5:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Russian Compliance Setup
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Complete setup for 152-ФЗ compliance - from registration to full document package
        </p>
      </div>

      {/* Progress Steps */}
      {currentStep <= 5 && (
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {STEPS.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full ${
                    currentStep > step.id
                      ? "bg-green-500 text-white"
                      : currentStep === step.id
                      ? "bg-primary-600 text-white"
                      : "bg-gray-200 text-gray-500 dark:bg-dark-600"
                  }`}
                >
                  {currentStep > step.id ? (
                    <CheckCircleIcon className="w-6 h-6" />
                  ) : (
                    <step.icon className="w-5 h-5" />
                  )}
                </div>
                {index < STEPS.length - 1 && (
                  <div
                    className={`w-full h-1 mx-2 ${
                      currentStep > step.id ? "bg-green-500" : "bg-gray-200 dark:bg-dark-600"
                    }`}
                    style={{ width: "60px" }}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2">
            {STEPS.map((step) => (
              <span
                key={step.id}
                className={`text-xs ${
                  currentStep >= step.id ? "text-gray-900 dark:text-gray-100" : "text-gray-400"
                }`}
              >
                {step.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Step Content */}
      <div className="card">
        {/* Step 1: Company Registration */}
        {currentStep === 1 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <BuildingOfficeIcon className="w-6 h-6 mr-2 text-primary-600" />
              Step 1: Company Registration
            </h2>
            <p className="text-gray-500 mb-6">
              Enter your company INN to auto-fill organization details from EGRUL
            </p>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  INN (Tax ID)
                </label>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={inn}
                    onChange={(e) => setInn(e.target.value.replace(/\D/g, "").slice(0, 12))}
                    placeholder="Enter 10 or 12 digit INN"
                    className="flex-1 rounded-lg border-gray-300 dark:bg-dark-700 dark:border-dark-600 text-lg"
                  />
                  <button
                    onClick={handleLookupINN}
                    disabled={inn.length < 10 || lookupLoading}
                    className="btn-primary px-6 flex items-center"
                  >
                    {lookupLoading ? (
                      <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                    ) : (
                      <>
                        <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
                        Search
                      </>
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Example: 7707083893 (Sberbank), 7702070139 (Gazprom)
                </p>
              </div>

              {companyData && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 mr-2" />
                    <span className="font-medium text-green-800 dark:text-green-200">
                      Company Found
                    </span>
                  </div>
                  <dl className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <dt className="text-gray-500">Full Name</dt>
                      <dd className="font-medium">{companyData.full_name as string}</dd>
                    </div>
                    <div>
                      <dt className="text-gray-500">INN</dt>
                      <dd className="font-mono">{companyData.inn as string}</dd>
                    </div>
                    {Boolean(companyData.ogrn) && (
                      <div>
                        <dt className="text-gray-500">OGRN</dt>
                        <dd className="font-mono">{String(companyData.ogrn)}</dd>
                      </div>
                    )}
                    {Boolean(companyData.legal_address) && (
                      <div className="col-span-2">
                        <dt className="text-gray-500">Address</dt>
                        <dd>{String(companyData.legal_address)}</dd>
                      </div>
                    )}
                    {Boolean(companyData.director_name) && (
                      <div>
                        <dt className="text-gray-500">Director</dt>
                        <dd>{String(companyData.director_name)}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Responsible Persons */}
        {currentStep === 2 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <UserGroupIcon className="w-6 h-6 mr-2 text-primary-600" />
              Step 2: Responsible Persons
            </h2>
            <p className="text-gray-500 mb-6">
              Assign responsible persons as required by 152-ФЗ (Article 22.1)
            </p>

            <div className="space-y-6">
              {responsiblePersons.map((person, index) => (
                <div key={index} className="border rounded-lg p-4 dark:border-dark-600">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium">
                      {RESPONSIBLE_ROLES.find((r) => r.value === person.role)?.label || person.role}
                      {RESPONSIBLE_ROLES.find((r) => r.value === person.role)?.required && (
                        <span className="ml-2 text-xs text-red-500">Required</span>
                      )}
                    </h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">Full Name</label>
                      <input
                        type="text"
                        value={person.full_name}
                        onChange={(e) => updateResponsiblePerson(index, "full_name", e.target.value)}
                        placeholder="Иванов Иван Иванович"
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">Email</label>
                      <input
                        type="email"
                        value={person.email}
                        onChange={(e) => updateResponsiblePerson(index, "email", e.target.value)}
                        placeholder="email@company.ru"
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">Position</label>
                      <input
                        type="text"
                        value={person.position}
                        onChange={(e) => updateResponsiblePerson(index, "position", e.target.value)}
                        placeholder="IT Director"
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">Phone</label>
                      <input
                        type="tel"
                        value={person.phone}
                        onChange={(e) => updateResponsiblePerson(index, "phone", e.target.value)}
                        placeholder="+7 (999) 123-45-67"
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: ISPDN Systems */}
        {currentStep === 3 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <ServerStackIcon className="w-6 h-6 mr-2 text-primary-600" />
              Step 3: ISPDN Systems
            </h2>
            <p className="text-gray-500 mb-6">
              Register your Personal Data Information Systems (ISPDN) per PP 1119
            </p>

            <div className="space-y-6">
              {ispdnSystems.map((ispdn, index) => (
                <div key={index} className="border rounded-lg p-4 dark:border-dark-600">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium">ISPDN #{index + 1}</h3>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          getProtectionLevelPreview(ispdn) === "УЗ-1"
                            ? "bg-red-100 text-red-800"
                            : getProtectionLevelPreview(ispdn) === "УЗ-2"
                            ? "bg-orange-100 text-orange-800"
                            : getProtectionLevelPreview(ispdn) === "УЗ-3"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {getProtectionLevelPreview(ispdn)}
                      </span>
                      {ispdnSystems.length > 1 && (
                        <button
                          onClick={() => removeISPDN(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <label className="block text-sm text-gray-500 mb-1">System Name</label>
                      <input
                        type="text"
                        value={ispdn.name}
                        onChange={(e) => updateISPDN(index, "name", e.target.value)}
                        placeholder="e.g., 1C:Salary and HR, CRM System"
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm text-gray-500 mb-1">Description</label>
                      <textarea
                        value={ispdn.description}
                        onChange={(e) => updateISPDN(index, "description", e.target.value)}
                        placeholder="Brief description of the system"
                        rows={2}
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">PD Category</label>
                      <select
                        value={ispdn.pdn_category}
                        onChange={(e) => updateISPDN(index, "pdn_category", e.target.value)}
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      >
                        {PDN_CATEGORIES.map((cat) => (
                          <option key={cat.value} value={cat.value}>
                            {cat.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-500 mb-1">Number of Subjects</label>
                      <select
                        value={ispdn.subject_count}
                        onChange={(e) => updateISPDN(index, "subject_count", e.target.value)}
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      >
                        {SUBJECT_COUNTS.map((sc) => (
                          <option key={sc.value} value={sc.value}>
                            {sc.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm text-gray-500 mb-1">Threat Type</label>
                      <select
                        value={ispdn.threat_type}
                        onChange={(e) => updateISPDN(index, "threat_type", e.target.value)}
                        className="w-full rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                      >
                        {THREAT_TYPES.map((tt) => (
                          <option key={tt.value} value={tt.value}>
                            {tt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}

              <button
                onClick={addISPDN}
                className="btn-secondary w-full flex items-center justify-center"
              >
                <PlusIcon className="w-5 h-5 mr-2" />
                Add Another ISPDN System
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Document Package */}
        {currentStep === 4 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <DocumentTextIcon className="w-6 h-6 mr-2 text-primary-600" />
              Step 4: Document Package
            </h2>
            <p className="text-gray-500 mb-6">
              Generate pre-filled compliance documents for 152-ФЗ
            </p>

            <div className="space-y-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start">
                  <ShieldCheckIcon className="w-6 h-6 text-blue-600 mt-0.5 mr-3" />
                  <div>
                    <h3 className="font-medium text-blue-900 dark:text-blue-100">
                      152-ФЗ Document Package
                    </h3>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      The following documents will be generated with your company data pre-filled:
                    </p>
                  </div>
                </div>
              </div>

              <div className="border rounded-lg divide-y dark:border-dark-600 dark:divide-dark-600">
                {[
                  { title: "Personal Data Processing Policy", required: true },
                  { title: "Information Security Policy", required: true },
                  { title: "Order: PDN Responsible Appointment", required: true },
                  { title: "Order: Persons with PD Access", required: true },
                  { title: "Order: ISPDN Systems List", required: true },
                  { title: "Order: Classification Commission", required: true },
                  { title: "Regulation: Personal Data Processing", required: true },
                  { title: "Regulation: Employee PD Protection", required: true },
                  { title: "Instruction: Non-Automated Processing", required: true },
                  { title: "Instruction: ISPDN User", required: true },
                  { title: "Instruction: Security Administrator", required: true },
                  { title: "Consent Form: Personal Data Processing", required: true },
                  { title: "Consent Form: Employee PD", required: true },
                  { title: "Journal: Subject Requests", required: true },
                  { title: "Journal: Storage Media", required: true },
                  { title: "Journal: Security Incidents", required: true },
                  { title: "Act: ISPDN Classification", required: true },
                  { title: "Act: PD Destruction", required: true },
                  { title: "Threat Model", required: true },
                  { title: "Non-Disclosure Obligation", required: true },
                ].map((doc, index) => (
                  <div key={index} className="flex items-center justify-between p-3">
                    <div className="flex items-center">
                      <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                      <span>{doc.title}</span>
                    </div>
                    {doc.required && (
                      <span className="text-xs text-red-500">Mandatory</span>
                    )}
                  </div>
                ))}
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={generateAllDocs}
                  onChange={(e) => setGenerateAllDocs(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2">Generate all mandatory documents</span>
              </label>
            </div>
          </div>
        )}

        {/* Step 5: Tasks & Timeline */}
        {currentStep === 5 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <ClipboardDocumentCheckIcon className="w-6 h-6 mr-2 text-primary-600" />
              Step 5: Tasks & Timeline
            </h2>
            <p className="text-gray-500 mb-6">
              Set up compliance tasks and deadlines
            </p>

            <div className="space-y-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={assignTasks}
                  onChange={(e) => setAssignTasks(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2">Create compliance tasks automatically</span>
              </label>

              {assignTasks && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Task Deadline (days from now)
                  </label>
                  <input
                    type="number"
                    value={deadlineDays}
                    onChange={(e) => setDeadlineDays(parseInt(e.target.value) || 30)}
                    min={7}
                    max={365}
                    className="w-32 rounded-md border-gray-300 dark:bg-dark-700 dark:border-dark-600"
                  />
                </div>
              )}

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600 mt-0.5 mr-3" />
                  <div>
                    <h3 className="font-medium text-yellow-900 dark:text-yellow-100">
                      Tasks to be created
                    </h3>
                    <ul className="text-sm text-yellow-700 dark:text-yellow-300 mt-2 space-y-1">
                      <li>Complete 152-ФЗ document package preparation</li>
                      <li>Submit notification to Roskomnadzor</li>
                      <li>Conduct employee training</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Step */}
        {currentStep === 6 && onboardingResult && (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircleIcon className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Onboarding Complete!
            </h2>
            <p className="text-gray-500 mb-6">
              Your company is now set up for 152-ФЗ compliance
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-primary-600">
                  {onboardingResult.responsible_persons_created as number}
                </p>
                <p className="text-sm text-gray-500">Responsible Persons</p>
              </div>
              <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-primary-600">
                  {onboardingResult.ispdn_systems_created as number}
                </p>
                <p className="text-sm text-gray-500">ISPDN Systems</p>
              </div>
              <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-primary-600">
                  {onboardingResult.documents_generated as number}
                </p>
                <p className="text-sm text-gray-500">Documents Generated</p>
              </div>
              <div className="bg-gray-50 dark:bg-dark-700 rounded-lg p-4">
                <p className="text-2xl font-bold text-primary-600">
                  {onboardingResult.tasks_created as number}
                </p>
                <p className="text-sm text-gray-500">Tasks Created</p>
              </div>
            </div>

            {(onboardingResult.next_steps as string[])?.length > 0 && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 text-left mb-6">
                <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  Next Steps
                </h3>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  {(onboardingResult.next_steps as string[]).map((step, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">{index + 1}.</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <button
              onClick={() => navigate("/russian-compliance")}
              className="btn-primary px-8"
            >
              Go to Compliance Dashboard
            </button>
          </div>
        )}

        {/* Navigation Buttons */}
        {currentStep <= 5 && (
          <div className="flex justify-between mt-8 pt-6 border-t dark:border-dark-600">
            <button
              onClick={() => setCurrentStep(currentStep - 1)}
              disabled={currentStep === 1}
              className="btn-secondary flex items-center disabled:opacity-50"
            >
              <ArrowLeftIcon className="w-5 h-5 mr-2" />
              Previous
            </button>

            {currentStep < 5 ? (
              <button
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={!canProceed()}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                Next
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="btn-primary flex items-center"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    Complete Setup
                    <CheckCircleIcon className="w-5 h-5 ml-2" />
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
