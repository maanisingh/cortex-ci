import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../stores/authStore";

const API_BASE_URL = "/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken, tenantId } = useAuthStore.getState();

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    if (tenantId) {
      config.headers["X-Tenant-ID"] = tenantId;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const { refreshToken, setTokens, logout } = useAuthStore.getState();

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          setTokens(response.data);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api(originalRequest);
        } catch {
          logout();
          window.location.href = "/login";
        }
      } else {
        logout();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);

// Auth API
export const authApi = {
  login: (
    email: string,
    password: string,
    tenantSlug?: string,
    mfaCode?: string,
  ) =>
    api.post("/auth/login", {
      email,
      password,
      tenant_slug: tenantSlug,
      mfa_code: mfaCode,
    }),

  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),

  me: () => api.get("/auth/me"),

  logout: () => api.post("/auth/logout"),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post("/auth/change-password", data),

  // MFA endpoints (Phase 3)
  mfa: {
    status: () => api.get("/auth/mfa/status"),
    setup: () => api.post("/auth/mfa/setup"),
    enable: (code: string) => api.post("/auth/mfa/enable", { code }),
    disable: (password: string, code: string) =>
      api.post("/auth/mfa/disable", { password, code }),
    verifyLogin: (mfaToken: string, code: string) =>
      api.post("/auth/mfa/verify-login", { mfa_token: mfaToken, code }),
    useBackupCode: (mfaToken: string, backupCode: string) =>
      api.post("/auth/mfa/backup-code", {
        mfa_token: mfaToken,
        backup_code: backupCode,
      }),
    regenerateBackupCodes: (code: string) =>
      api.post("/auth/mfa/regenerate-backup-codes", { code }),
  },
};

// Entities API
export const entitiesApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    type?: string;
    search?: string;
  }) => api.get("/entities", { params }),

  get: (id: string) => api.get(`/entities/${id}`),

  create: (data: Record<string, unknown>) => api.post("/entities", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/entities/${id}`, data),

  delete: (id: string) => api.delete(`/entities/${id}`),

  bulkImport: (data: {
    entities: Record<string, unknown>[];
    skip_duplicates?: boolean;
  }) => api.post("/entities/bulk-import", data),
};

// Constraints API
export const constraintsApi = {
  list: (params?: {
    page?: number;
    type?: string;
    severity?: string;
    search?: string;
  }) => api.get("/constraints", { params }),

  get: (id: string) => api.get(`/constraints/${id}`),

  create: (data: Record<string, unknown>) => api.post("/constraints", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/constraints/${id}`, data),

  delete: (id: string) => api.delete(`/constraints/${id}`),

  summary: () => api.get("/constraints/summary"),
};

// Dependencies API
export const dependenciesApi = {
  list: (params?: { page?: number; layer?: string; entity_id?: string }) =>
    api.get("/dependencies", { params }),

  get: (id: string) => api.get(`/dependencies/${id}`),

  create: (data: Record<string, unknown>) => api.post("/dependencies", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/dependencies/${id}`, data),

  delete: (id: string) => api.delete(`/dependencies/${id}`),

  graph: (params?: { entity_id?: string; layer?: string; depth?: number }) =>
    api.get("/dependencies/graph", { params }),
};

// Risks API
export const risksApi = {
  summary: () => api.get("/risks/summary"),

  trends: (days?: number) => api.get("/risks/trends", { params: { days } }),

  entityRisk: (entityId: string) => api.get(`/risks/entity/${entityId}`),

  entityHistory: (entityId: string, limit?: number) =>
    api.get(`/risks/entity/${entityId}/history`, { params: { limit } }),

  justification: (entityId: string) =>
    api.get(`/risks/entity/${entityId}/justification`),

  calculate: (data: { entity_ids?: string[]; force_recalculate?: boolean }) =>
    api.post("/risks/calculate", data),

  // Risk Register API (GRC)
  register: {
    list: (params?: {
      page?: number;
      page_size?: number;
      category?: string;
      status?: string;
      level?: string;
      search?: string;
    }) => api.get("/risks/register", { params }),

    summary: () => api.get("/risks/register/summary"),

    get: (id: string) => api.get(`/risks/register/${id}`),

    create: (data: {
      title: string;
      description?: string;
      category: string;
      status?: string;
      likelihood?: number;
      impact?: number;
      residual_likelihood?: number;
      residual_impact?: number;
      treatment?: string;
      treatment_plan?: string;
      risk_owner_id?: string;
      risk_owner_name?: string;
      entity_id?: string;
      risk_appetite_threshold?: number;
      review_date?: string;
      target_closure_date?: string;
      source?: string;
      reference_id?: string;
      control_ids?: string[];
      tags?: string[];
    }) => api.post("/risks/register", data),

    update: (id: string, data: Record<string, unknown>) =>
      api.put(`/risks/register/${id}`, data),

    delete: (id: string) => api.delete(`/risks/register/${id}`),
  },
};

// Scenarios API
export const scenariosApi = {
  list: (params?: { page?: number; status?: string; type?: string }) =>
    api.get("/scenarios", { params }),

  get: (id: string) => api.get(`/scenarios/${id}`),

  results: (id: string) => api.get(`/scenarios/${id}/results`),

  create: (data: Record<string, unknown>) => api.post("/scenarios", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/scenarios/${id}`, data),

  run: (id: string) => api.post(`/scenarios/${id}/run`),

  archive: (
    id: string,
    data: { outcome_notes?: string; lessons_learned?: string },
  ) => api.post(`/scenarios/${id}/archive`, data),

  delete: (id: string) => api.delete(`/scenarios/${id}`),
};

// Audit API
export const auditApi = {
  list: (params?: {
    page?: number;
    user_id?: string;
    action?: string;
    resource_type?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get("/audit", { params }),

  get: (id: string) => api.get(`/audit/${id}`),

  resourceHistory: (resourceType: string, resourceId: string) =>
    api.get(`/audit/resource/${resourceType}/${resourceId}`),
};

// Admin API
export const adminApi = {
  users: {
    list: (params?: { page?: number; role?: string }) =>
      api.get("/admin/users", { params }),
    get: (id: string) => api.get(`/admin/users/${id}`),
    create: (data: Record<string, unknown>) => api.post("/admin/users", data),
    update: (id: string, data: Record<string, unknown>) =>
      api.put(`/admin/users/${id}`, data),
    delete: (id: string) => api.delete(`/admin/users/${id}`),
  },
  settings: {
    get: () => api.get("/admin/settings"),
    update: (data: Record<string, unknown>) => api.put("/admin/settings", data),
    updateRiskWeights: (weights: Record<string, number>) =>
      api.put("/admin/settings/risk-weights", weights),
  },
};

// ============= PHASE 2 APIs =============

// Scenario Chains API (Phase 2.2)
export const scenarioChainsApi = {
  list: (params?: { page?: number; page_size?: number }) =>
    api.get("/scenarios/chains", { params }),

  get: (id: string) => api.get(`/scenarios/chains/${id}`),

  create: (data: {
    name: string;
    description?: string;
    trigger_event: string;
    trigger_entity_id?: string;
  }) => api.post("/scenarios/chains", data),

  getEffects: (chainId: string) =>
    api.get(`/scenarios/chains/${chainId}/effects`),

  addEffect: (chainId: string, data: Record<string, unknown>) =>
    api.post(`/scenarios/chains/${chainId}/effects`, data),

  simulate: (chainId: string, maxDepth?: number) =>
    api.post(`/scenarios/chains/${chainId}/simulate`, null, {
      params: { max_depth: maxDepth },
    }),

  delete: (id: string) => api.delete(`/scenarios/chains/${id}`),
};

// Risk Justification API (Phase 2.3)
export const riskJustificationApi = {
  get: (entityId: string) => api.get(`/risks/justification/${entityId}`),

  export: (entityId: string, format?: string) =>
    api.get(`/risks/justification/${entityId}/export`, { params: { format } }),

  override: (entityId: string, data: { new_score: number; reason: string }) =>
    api.post(`/risks/justification/${entityId}/override`, data),

  history: (entityId: string) =>
    api.get(`/risks/justification/${entityId}/history`),
};

// Dependencies Layer API (Phase 2.1)
export const dependencyLayersApi = {
  summary: () => api.get("/dependencies/layers/summary"),

  crossLayerImpact: (entityId: string) =>
    api.get(`/dependencies/cross-layer-impact/${entityId}`),
};

// History API (Phase 2.4)
export const historyApi = {
  entityTimeline: (entityId: string, days?: number) =>
    api.get(`/history/entity/${entityId}/timeline`, { params: { days } }),

  createSnapshot: () => api.post("/history/snapshot"),

  constraintChanges: (days?: number) =>
    api.get("/history/constraints/changes", { params: { days } }),

  decisions: {
    list: (params?: {
      include_resolved?: boolean;
      page?: number;
      page_size?: number;
    }) => api.get("/history/decisions", { params }),

    create: (data: {
      decision_date: string;
      decision_summary: string;
      decision_type: string;
      entities_involved?: string[];
    }) => api.post("/history/decisions", data),

    recordOutcome: (
      decisionId: string,
      params: {
        outcome_summary: string;
        outcome_success: boolean;
        lessons_learned?: string;
      },
    ) => api.put(`/history/decisions/${decisionId}/outcome`, null, { params }),
  },

  transitionReport: (data: {
    title: string;
    period_start: string;
    period_end: string;
    executive_summary: string;
  }) => api.post("/history/transition-report", data),
};

// Monitoring API
export const monitoringApi = {
  health: () => api.get("/monitoring/health"),
  metrics: () => api.get("/monitoring/metrics"),
  alerts: (params?: { severity?: string; acknowledged?: boolean }) =>
    api.get("/monitoring/alerts", { params }),
  dashboard: () => api.get("/monitoring/dashboard"),
};

// AI Analysis API (Phase 2.5)
export const aiApi = {
  list: (params?: {
    status_filter?: string;
    page?: number;
    page_size?: number;
  }) => api.get("/ai", { params }),

  get: (id: string) => api.get(`/ai/${id}`),

  request: (data: {
    analysis_type:
      | "anomaly"
      | "pattern"
      | "summary"
      | "scenario"
      | "clustering";
    description: string;
    entity_ids?: string[];
    parameters?: Record<string, unknown>;
  }) => api.post("/ai", data),

  approve: (id: string, notes?: string) =>
    api.post(`/ai/${id}/approve`, null, { params: { notes } }),

  reject: (id: string, reason: string) =>
    api.post(`/ai/${id}/reject`, null, { params: { reason } }),

  anomalies: {
    pending: (params?: { page?: number; page_size?: number }) =>
      api.get("/ai/anomalies/pending", { params }),

    review: (
      anomalyId: string,
      params: { is_confirmed: boolean; notes?: string },
    ) => api.post(`/ai/anomalies/${anomalyId}/review`, null, { params }),
  },

  modelCard: (analysisType: string) =>
    api.get(`/ai/model-card/${analysisType}`),
};

// ============= COMPLIANCE PLATFORM APIs =============

// Compliance Scoring API
export const complianceScoringApi = {
  score: (frameworkId?: string) =>
    api.get("/compliance/scoring/score", {
      params: { framework_id: frameworkId },
    }),

  gaps: (params?: {
    framework_id?: string;
    severity?: string;
    limit?: number;
  }) => api.get("/compliance/scoring/gaps", { params }),

  frameworkGaps: (frameworkId: string) =>
    api.get(`/compliance/scoring/gaps/${frameworkId}`),

  mapping: () => api.get("/compliance/scoring/mapping"),

  dashboard: () => api.get("/compliance/scoring/dashboard"),
};

// Compliance Frameworks API
export const complianceFrameworksApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    type?: string;
    is_active?: boolean;
  }) => api.get("/compliance/frameworks", { params }),

  get: (id: string) => api.get(`/compliance/frameworks/${id}`),

  create: (data: Record<string, unknown>) =>
    api.post("/compliance/frameworks", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/compliance/frameworks/${id}`, data),

  delete: (id: string) => api.delete(`/compliance/frameworks/${id}`),
};

// Compliance Controls API
export const complianceControlsApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    framework_id?: string;
    category?: string;
    implementation_status?: string;
  }) => api.get("/compliance/controls", { params }),

  get: (id: string) => api.get(`/compliance/controls/${id}`),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/compliance/controls/${id}`, data),

  stats: (frameworkId?: string) =>
    api.get("/compliance/controls/stats/summary", {
      params: { framework_id: frameworkId },
    }),
};

// ============= GRC MODULE APIs =============

// Policy Management API
export const policiesApi = {
  list: (params?: {
    category?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get("/compliance/policies", { params }),

  summary: () => api.get("/compliance/policies/summary"),

  get: (id: string) => api.get(`/compliance/policies/${id}`),

  create: (data: {
    policy_number: string;
    title: string;
    category: string;
    content: string;
    summary?: string;
    purpose?: string;
    scope?: string;
    owner_department?: string;
    requires_acknowledgement?: boolean;
    review_frequency_months?: number;
    tags?: string[];
  }) => api.post("/compliance/policies", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/compliance/policies/${id}`, data),

  delete: (id: string) => api.delete(`/compliance/policies/${id}`),

  acknowledge: (id: string) =>
    api.post(`/compliance/policies/${id}/acknowledge`),

  publish: (id: string) => api.patch(`/compliance/policies/${id}/publish`),

  updateStatus: (id: string, newStatus: string) =>
    api.patch(`/compliance/policies/${id}/status`, null, {
      params: { new_status: newStatus },
    }),

  // Version Control
  versions: {
    list: (policyId: string) =>
      api.get(`/compliance/policies/${policyId}/versions`),

    get: (policyId: string, versionId: string) =>
      api.get(`/compliance/policies/${policyId}/versions/${versionId}`),

    create: (
      policyId: string,
      data: { change_summary: string; version_type?: string; content?: string },
    ) => api.post(`/compliance/policies/${policyId}/versions`, data),
  },

  // Acknowledgements
  acknowledgements: {
    list: (policyId: string) =>
      api.get(`/compliance/policies/${policyId}/acknowledgements`),

    stats: (policyId: string) =>
      api.get(`/compliance/policies/${policyId}/acknowledgements/stats`),

    myStatus: (policyId: string) =>
      api.get(`/compliance/policies/${policyId}/acknowledgements/my-status`),
  },

  // Exceptions
  exceptions: {
    list: (policyId: string, status?: string) =>
      api.get(`/compliance/policies/${policyId}/exceptions`, {
        params: { status },
      }),

    get: (policyId: string, exceptionId: string) =>
      api.get(`/compliance/policies/${policyId}/exceptions/${exceptionId}`),

    create: (
      policyId: string,
      data: {
        title: string;
        justification: string;
        scope: string;
        risk_description?: string;
        compensating_controls?: string;
        department?: string;
        effective_from?: string;
        effective_to?: string;
        is_permanent?: boolean;
      },
    ) => api.post(`/compliance/policies/${policyId}/exceptions`, data),

    update: (
      policyId: string,
      exceptionId: string,
      data: Record<string, unknown>,
    ) =>
      api.put(
        `/compliance/policies/${policyId}/exceptions/${exceptionId}`,
        data,
      ),

    review: (
      policyId: string,
      exceptionId: string,
      action: "approve" | "deny",
      notes?: string,
    ) =>
      api.patch(
        `/compliance/policies/${policyId}/exceptions/${exceptionId}/review`,
        null,
        { params: { action, notes } },
      ),
  },
};

// Evidence Management API
export const evidenceApi = {
  list: (params?: {
    evidence_type?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get("/compliance/evidence", { params }),

  summary: () => api.get("/compliance/evidence/summary"),

  get: (id: string) => api.get(`/compliance/evidence/${id}`),

  create: (data: {
    title: string;
    description?: string;
    evidence_type: string;
    control_id?: string;
    external_url?: string;
    category?: string;
    tags?: string[];
    valid_from?: string;
    valid_to?: string;
    is_perpetual?: boolean;
  }) => api.post("/compliance/evidence", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/compliance/evidence/${id}`, data),

  delete: (id: string) => api.delete(`/compliance/evidence/${id}`),

  review: (
    id: string,
    data: {
      decision: string;
      comments?: string;
      completeness_score?: number;
      relevance_score?: number;
      quality_score?: number;
    },
  ) => api.post(`/compliance/evidence/${id}/review`, data),

  submitForReview: (id: string) =>
    api.post(`/compliance/evidence/${id}/submit-for-review`),

  expiring: (days?: number) =>
    api.get("/compliance/evidence/expiring", { params: { days: days || 30 } }),

  byControl: (controlId: string) =>
    api.get(`/compliance/evidence/by-control/${controlId}`),

  linkControl: (evidenceId: string, controlId: string, linkType?: string) =>
    api.post(`/compliance/evidence/${evidenceId}/link-control`, null, {
      params: { control_id: controlId, link_type: linkType || "PRIMARY" },
    }),
};

// Audit Management API
export const auditsApi = {
  list: (params?: {
    audit_type?: string;
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get("/compliance/audits", { params }),

  summary: () => api.get("/compliance/audits/summary"),

  get: (id: string) => api.get(`/compliance/audits/${id}`),

  create: (data: {
    title: string;
    audit_type: string;
    description?: string;
    scope_description?: string;
    planned_start?: string;
    planned_end?: string;
    in_scope_systems?: string[];
    in_scope_frameworks?: string[];
  }) => api.post("/compliance/audits", data),

  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/compliance/audits/${id}`, data),

  delete: (id: string) => api.delete(`/compliance/audits/${id}`),

  start: (id: string) => api.post(`/compliance/audits/${id}/start`),

  complete: (id: string, overallRating?: string, opinion?: string) =>
    api.post(`/compliance/audits/${id}/complete`, null, {
      params: { overall_rating: overallRating, opinion },
    }),

  // Findings
  findings: {
    list: (auditId: string, params?: { severity?: string; status?: string }) =>
      api.get(`/compliance/audits/${auditId}/findings`, { params }),

    listAll: (params?: {
      severity?: string;
      status?: string;
      search?: string;
      page?: number;
      page_size?: number;
    }) => api.get("/compliance/audits/findings/all", { params }),

    summary: () => api.get("/compliance/audits/findings/summary"),

    create: (
      auditId: string,
      data: {
        title: string;
        severity: string;
        description: string;
        recommendation?: string;
        root_cause?: string;
        impact?: string;
        target_remediation_date?: string;
        owner_department?: string;
      },
    ) => api.post(`/compliance/audits/${auditId}/findings`, data),

    get: (findingId: string) =>
      api.get(`/compliance/audits/findings/${findingId}`),

    update: (findingId: string, data: Record<string, unknown>) =>
      api.put(`/compliance/audits/findings/${findingId}`, data),

    open: (severity?: string) =>
      api.get("/compliance/audits/findings/open", { params: { severity } }),

    overdue: () => api.get("/compliance/audits/findings/overdue"),

    respond: (findingId: string, response: string, targetDate?: string) =>
      api.post(`/compliance/audits/findings/${findingId}/respond`, {
        response,
        target_date: targetDate,
      }),

    close: (findingId: string, verificationNotes?: string) =>
      api.post(`/compliance/audits/findings/${findingId}/close`, null, {
        params: { verification_notes: verificationNotes },
      }),

    updateStatus: (findingId: string, newStatus: string) =>
      api.patch(`/compliance/audits/findings/${findingId}/status`, null, {
        params: { new_status: newStatus },
      }),
  },
};

// Incident Management API
export const incidentsApi = {
  list: (params?: {
    category?: string;
    severity?: string;
    status?: string;
    is_breach?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get("/compliance/incidents", { params }),

  get: (id: string) => api.get(`/compliance/incidents/${id}`),

  create: (data: {
    title: string;
    description: string;
    category: string;
    severity: string;
    detection_method?: string;
    affected_systems?: string[];
  }) => api.post("/compliance/incidents", data),

  updateStatus: (id: string, newStatus: string) =>
    api.patch(`/compliance/incidents/${id}/status`, null, {
      params: { new_status: newStatus },
    }),

  markAsBreach: (id: string, isBreach: boolean, notes?: string) =>
    api.patch(`/compliance/incidents/${id}/breach`, null, {
      params: { is_breach: isBreach, notes },
    }),
};

// Vendor Risk Management API
export const vendorsApi = {
  list: (params?: { tier?: string; status?: string; category?: string }) =>
    api.get("/compliance/vendors", { params }),

  get: (id: string) => api.get(`/compliance/vendors/${id}`),

  create: (data: {
    legal_name: string;
    tier: string;
    category: string;
    country?: string;
    services_provided?: string[];
    has_data_access?: boolean;
  }) => api.post("/compliance/vendors", data),

  startAssessment: (vendorId: string, assessmentType?: string) =>
    api.post(`/compliance/vendors/${vendorId}/assess`, null, {
      params: { assessment_type: assessmentType || "INITIAL" },
    }),
};

// ============= RUSSIAN COMPLIANCE APIs =============

// Russian Compliance API (152-ФЗ, 187-ФЗ, ГОСТ 57580, ФСТЭК)
export const russianComplianceApi = {
  // Company Profile
  companies: {
    lookup: (inn: string) =>
      api.post("/compliance/russian/companies/lookup", null, {
        params: { inn },
      }),

    list: () => api.get("/compliance/russian/companies"),

    get: (id: string) => api.get(`/compliance/russian/companies/${id}`),

    create: (inn: string) =>
      api.post("/compliance/russian/companies", { inn }),

    update: (id: string, data: Record<string, unknown>) =>
      api.patch(`/compliance/russian/companies/${id}`, data),
  },

  // Responsible Persons
  responsiblePersons: {
    list: (companyId: string) =>
      api.get(`/compliance/russian/companies/${companyId}/responsible`),

    create: (
      companyId: string,
      data: {
        role: string;
        full_name: string;
        email: string;
        position?: string;
        department?: string;
        phone?: string;
      },
    ) => api.post(`/compliance/russian/companies/${companyId}/responsible`, data),
  },

  // ISPDN Systems
  ispdn: {
    list: (companyId: string) =>
      api.get(`/compliance/russian/companies/${companyId}/ispdn`),

    create: (
      companyId: string,
      data: {
        name: string;
        description?: string;
        pdn_category: string;
        subject_count: string;
        threat_type: string;
        processing_purposes?: string[];
        subject_categories?: string[];
        pdn_types?: string[];
      },
    ) => api.post(`/compliance/russian/companies/${companyId}/ispdn`, data),
  },

  // Protection Level Calculator
  calculateProtectionLevel: (data: {
    pdn_category: string;
    subject_count: number;
    threat_type: string;
    is_employee_only?: boolean;
  }) => api.post("/compliance/russian/calculate-protection-level", data),

  // Document Templates
  templates: {
    list: (params?: { framework?: string; protection_level?: string }) =>
      api.get("/compliance/russian/templates", { params }),

    get: (id: string) => api.get(`/compliance/russian/templates/${id}`),

    preview: (templateId: string, companyId: string) =>
      api.get(`/compliance/russian/templates/${templateId}/preview`, {
        params: { company_id: companyId },
      }),
  },

  // Lifecycle Templates (company stage recommendations)
  lifecycleTemplates: {
    listAll: () => api.get("/compliance/russian/lifecycle-templates"),

    getStage: (stage: string) =>
      api.get(`/compliance/russian/lifecycle-templates/${stage}`),
  },

  // SME Templates (285+ business document templates)
  smeTemplates: {
    list: (params?: { category?: string; search?: string }) =>
      api.get("/compliance/russian/sme-templates", { params }),

    getCategories: () => api.get("/compliance/russian/sme-templates/categories"),

    getStatistics: () => api.get("/compliance/russian/sme-templates/statistics"),

    generate: (templateId: string, companyData: Record<string, unknown> = {}) =>
      api.post("/compliance/russian/sme-templates/generate", {
        template_id: templateId,
        company_data: companyData,
      }),
  },

  // Compliance Documents
  documents: {
    list: (companyId: string, params?: { framework?: string; status?: string }) =>
      api.get(`/compliance/russian/companies/${companyId}/documents`, { params }),

    get: (companyId: string, documentId: string) =>
      api.get(`/compliance/russian/companies/${companyId}/documents/${documentId}`),

    create: (
      companyId: string,
      data: { template_id: string; ispdn_id?: string },
    ) => api.post(`/compliance/russian/companies/${companyId}/documents`, data),

    update: (
      companyId: string,
      documentId: string,
      data: { content?: string; status?: string },
    ) =>
      api.patch(
        `/compliance/russian/companies/${companyId}/documents/${documentId}`,
        data,
      ),
  },

  // Compliance Tasks
  tasks: {
    list: (companyId: string, params?: { status?: string; framework?: string }) =>
      api.get(`/compliance/russian/companies/${companyId}/tasks`, { params }),

    get: (companyId: string, taskId: string) =>
      api.get(`/compliance/russian/companies/${companyId}/tasks/${taskId}`),

    create: (
      companyId: string,
      data: {
        title: string;
        description?: string;
        task_type?: string;
        framework?: string;
        priority?: string;
        due_date?: string;
        assigned_to?: string;
        assigned_department?: string;
        is_recurring?: boolean;
        recurrence_days?: number;
      },
    ) => api.post(`/compliance/russian/companies/${companyId}/tasks`, data),

    update: (
      companyId: string,
      taskId: string,
      data: {
        title?: string;
        description?: string;
        status?: string;
        priority?: string;
        due_date?: string;
        assigned_to?: string;
        completion_notes?: string;
      },
    ) =>
      api.patch(
        `/compliance/russian/companies/${companyId}/tasks/${taskId}`,
        data,
      ),

    delete: (companyId: string, taskId: string) =>
      api.delete(`/compliance/russian/companies/${companyId}/tasks/${taskId}`),

    complete: (companyId: string, taskId: string, completionNotes?: string) =>
      api.post(
        `/compliance/russian/companies/${companyId}/tasks/${taskId}/complete`,
        null,
        { params: { completion_notes: completionNotes } },
      ),

    bulkCreate: (
      companyId: string,
      tasks: Array<{
        title: string;
        description?: string;
        task_type?: string;
        priority?: string;
        due_date?: string;
        is_recurring?: boolean;
        recurrence_days?: number;
      }>,
    ) =>
      api.post(`/compliance/russian/companies/${companyId}/tasks/bulk-create`, tasks),

    generateFromTemplate: (companyId: string, startDate?: string) =>
      api.post(
        `/compliance/russian/companies/${companyId}/tasks/generate-from-template`,
        null,
        { params: { start_date: startDate } },
      ),

    myTasks: (status?: string) =>
      api.get("/compliance/russian/my-tasks", { params: { status } }),

    getTemplates: () => api.get("/compliance/russian/task-templates"),
  },

  // Dashboard
  dashboard: (companyId: string) =>
    api.get(`/compliance/russian/companies/${companyId}/dashboard`),

  // Frameworks
  frameworks: () => api.get("/compliance/russian/frameworks"),
};
