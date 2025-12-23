import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken, tenantId } = useAuthStore.getState()

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }

    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const { refreshToken, setTokens, logout } = useAuthStore.getState()

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          setTokens(response.data)
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
          return api(originalRequest)
        } catch {
          logout()
          window.location.href = '/login'
        }
      } else {
        logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string, tenantSlug?: string) =>
    api.post('/auth/login', { email, password, tenant_slug: tenantSlug }),

  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),

  me: () => api.get('/auth/me'),

  logout: () => api.post('/auth/logout'),
}

// Entities API
export const entitiesApi = {
  list: (params?: { page?: number; page_size?: number; type?: string; search?: string }) =>
    api.get('/entities', { params }),

  get: (id: string) => api.get(`/entities/${id}`),

  create: (data: any) => api.post('/entities', data),

  update: (id: string, data: any) => api.put(`/entities/${id}`, data),

  delete: (id: string) => api.delete(`/entities/${id}`),

  bulkImport: (data: { entities: any[]; skip_duplicates?: boolean }) =>
    api.post('/entities/bulk-import', data),
}

// Constraints API
export const constraintsApi = {
  list: (params?: { page?: number; type?: string; severity?: string; search?: string }) =>
    api.get('/constraints', { params }),

  get: (id: string) => api.get(`/constraints/${id}`),

  create: (data: any) => api.post('/constraints', data),

  update: (id: string, data: any) => api.put(`/constraints/${id}`, data),

  delete: (id: string) => api.delete(`/constraints/${id}`),

  summary: () => api.get('/constraints/summary'),
}

// Dependencies API
export const dependenciesApi = {
  list: (params?: { page?: number; layer?: string; entity_id?: string }) =>
    api.get('/dependencies', { params }),

  get: (id: string) => api.get(`/dependencies/${id}`),

  create: (data: any) => api.post('/dependencies', data),

  update: (id: string, data: any) => api.put(`/dependencies/${id}`, data),

  delete: (id: string) => api.delete(`/dependencies/${id}`),

  graph: (params?: { entity_id?: string; layer?: string; depth?: number }) =>
    api.get('/dependencies/graph', { params }),
}

// Risks API
export const risksApi = {
  summary: () => api.get('/risks/summary'),

  trends: (days?: number) => api.get('/risks/trends', { params: { days } }),

  entityRisk: (entityId: string) => api.get(`/risks/entity/${entityId}`),

  entityHistory: (entityId: string, limit?: number) =>
    api.get(`/risks/entity/${entityId}/history`, { params: { limit } }),

  justification: (entityId: string) => api.get(`/risks/entity/${entityId}/justification`),

  calculate: (data: { entity_ids?: string[]; force_recalculate?: boolean }) =>
    api.post('/risks/calculate', data),
}

// Scenarios API
export const scenariosApi = {
  list: (params?: { page?: number; status?: string; type?: string }) =>
    api.get('/scenarios', { params }),

  get: (id: string) => api.get(`/scenarios/${id}`),

  results: (id: string) => api.get(`/scenarios/${id}/results`),

  create: (data: any) => api.post('/scenarios', data),

  update: (id: string, data: any) => api.put(`/scenarios/${id}`, data),

  run: (id: string) => api.post(`/scenarios/${id}/run`),

  archive: (id: string, data: { outcome_notes?: string; lessons_learned?: string }) =>
    api.post(`/scenarios/${id}/archive`, data),

  delete: (id: string) => api.delete(`/scenarios/${id}`),
}

// Audit API
export const auditApi = {
  list: (params?: {
    page?: number
    user_id?: string
    action?: string
    resource_type?: string
    start_date?: string
    end_date?: string
  }) => api.get('/audit', { params }),

  get: (id: string) => api.get(`/audit/${id}`),

  resourceHistory: (resourceType: string, resourceId: string) =>
    api.get(`/audit/resource/${resourceType}/${resourceId}`),
}

// Admin API
export const adminApi = {
  users: {
    list: (params?: { page?: number; role?: string }) => api.get('/admin/users', { params }),
    get: (id: string) => api.get(`/admin/users/${id}`),
    create: (data: any) => api.post('/admin/users', data),
    update: (id: string, data: any) => api.put(`/admin/users/${id}`, data),
    delete: (id: string) => api.delete(`/admin/users/${id}`),
  },
  settings: {
    get: () => api.get('/admin/settings'),
    update: (data: any) => api.put('/admin/settings', data),
    updateRiskWeights: (weights: Record<string, number>) =>
      api.put('/admin/settings/risk-weights', weights),
  },
}

// ============= PHASE 2 APIs =============

// Scenario Chains API (Phase 2.2)
export const scenarioChainsApi = {
  list: (params?: { page?: number; page_size?: number }) =>
    api.get('/scenarios/chains', { params }),

  get: (id: string) => api.get(`/scenarios/chains/${id}`),

  create: (data: { name: string; description?: string; trigger_event: string; trigger_entity_id?: string }) =>
    api.post('/scenarios/chains', data),

  getEffects: (chainId: string) => api.get(`/scenarios/chains/${chainId}/effects`),

  addEffect: (chainId: string, data: any) =>
    api.post(`/scenarios/chains/${chainId}/effects`, data),

  simulate: (chainId: string, maxDepth?: number) =>
    api.post(`/scenarios/chains/${chainId}/simulate`, null, { params: { max_depth: maxDepth } }),

  delete: (id: string) => api.delete(`/scenarios/chains/${id}`),
}

// Risk Justification API (Phase 2.3)
export const riskJustificationApi = {
  get: (entityId: string) => api.get(`/risks/justification/${entityId}`),

  export: (entityId: string, format?: string) =>
    api.get(`/risks/justification/${entityId}/export`, { params: { format } }),

  override: (entityId: string, data: { new_score: number; reason: string }) =>
    api.post(`/risks/justification/${entityId}/override`, data),

  history: (entityId: string) => api.get(`/risks/justification/${entityId}/history`),
}

// Dependencies Layer API (Phase 2.1)
export const dependencyLayersApi = {
  summary: () => api.get('/dependencies/layers/summary'),

  crossLayerImpact: (entityId: string) =>
    api.get(`/dependencies/cross-layer-impact/${entityId}`),
}

// History API (Phase 2.4)
export const historyApi = {
  entityTimeline: (entityId: string, days?: number) =>
    api.get(`/history/entity/${entityId}/timeline`, { params: { days } }),

  createSnapshot: () => api.post('/history/snapshot'),

  constraintChanges: (days?: number) =>
    api.get('/history/constraints/changes', { params: { days } }),

  decisions: {
    list: (params?: { include_resolved?: boolean; page?: number; page_size?: number }) =>
      api.get('/history/decisions', { params }),

    create: (data: {
      decision_date: string;
      decision_summary: string;
      decision_type: string;
      entities_involved?: string[];
    }) => api.post('/history/decisions', data),

    recordOutcome: (decisionId: string, params: {
      outcome_summary: string;
      outcome_success: boolean;
      lessons_learned?: string;
    }) => api.put(`/history/decisions/${decisionId}/outcome`, null, { params }),
  },

  transitionReport: (data: {
    title: string;
    period_start: string;
    period_end: string;
    executive_summary: string;
  }) => api.post('/history/transition-report', data),
}

// AI Analysis API (Phase 2.5)
export const aiApi = {
  list: (params?: { status_filter?: string; page?: number; page_size?: number }) =>
    api.get('/ai', { params }),

  get: (id: string) => api.get(`/ai/${id}`),

  request: (data: {
    analysis_type: 'anomaly' | 'pattern' | 'summary' | 'scenario' | 'clustering';
    description: string;
    entity_ids?: string[];
    parameters?: Record<string, any>;
  }) => api.post('/ai', data),

  approve: (id: string, notes?: string) =>
    api.post(`/ai/${id}/approve`, null, { params: { notes } }),

  reject: (id: string, reason: string) =>
    api.post(`/ai/${id}/reject`, null, { params: { reason } }),

  anomalies: {
    pending: (params?: { page?: number; page_size?: number }) =>
      api.get('/ai/anomalies/pending', { params }),

    review: (anomalyId: string, params: { is_confirmed: boolean; notes?: string }) =>
      api.post(`/ai/anomalies/${anomalyId}/review`, null, { params }),
  },

  modelCard: (analysisType: string) => api.get(`/ai/model-card/${analysisType}`),
}
