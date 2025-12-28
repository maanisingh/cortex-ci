// ============= Core Types =============

export interface Entity {
  id: string;
  tenant_id: string;
  name: string;
  type: EntityType;
  status: EntityStatus;
  metadata: Record<string, unknown>;
  risk_score?: number;
  last_checked?: string;
  created_at: string;
  updated_at: string;
}

export type EntityType =
  | "individual"
  | "organization"
  | "vessel"
  | "aircraft"
  | "ai_model"
  | "data_system"
  | "vendor"
  | "team"
  | "asset"
  | "other";

export type EntityStatus = "active" | "inactive" | "archived" | "pending";

export interface EntityCreate {
  name: string;
  type: EntityType;
  status?: EntityStatus;
  metadata?: Record<string, unknown>;
}

export interface EntityUpdate {
  name?: string;
  type?: EntityType;
  status?: EntityStatus;
  metadata?: Record<string, unknown>;
}

// ============= Constraint Types =============

export interface Constraint {
  id: string;
  tenant_id: string;
  name: string;
  type: ConstraintType;
  severity: ConstraintSeverity;
  description?: string;
  source: string;
  source_url?: string;
  effective_date?: string;
  expiration_date?: string;
  status: ConstraintStatus;
  conditions: ConstraintCondition[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type ConstraintType =
  // Core Regulatory Categories
  | "policy"
  | "regulation"
  | "compliance"
  | "contractual"
  | "operational"
  | "financial"
  | "security"
  // Trade & International
  | "sanctions"
  | "export_control"
  | "trade_restriction"
  | "import_regulation"
  // Data & Privacy
  | "data_privacy"
  | "data_protection"
  | "gdpr"
  | "ccpa"
  // Industry-Specific
  | "environmental"
  | "health_safety"
  | "labor"
  | "anti_corruption"
  | "aml"
  | "kyc"
  // Licensing & Certification
  | "license"
  | "certification"
  | "accreditation"
  // AI/ML Specific
  | "ai_governance"
  | "algorithmic_accountability"
  | "model_risk"
  // Other
  | "custom";

export type ConstraintSeverity = "critical" | "high" | "medium" | "low";

export type ConstraintStatus = "active" | "pending" | "expired" | "revoked";

export interface ConstraintCondition {
  field: string;
  operator:
    | "equals"
    | "contains"
    | "greater_than"
    | "less_than"
    | "in"
    | "not_in";
  value: string | number | string[];
}

export interface ConstraintCreate {
  name: string;
  type: ConstraintType;
  severity: ConstraintSeverity;
  description?: string;
  source: string;
  source_url?: string;
  effective_date?: string;
  expiration_date?: string;
  conditions?: ConstraintCondition[];
  metadata?: Record<string, unknown>;
}

export interface ConstraintUpdate {
  name?: string;
  type?: ConstraintType;
  severity?: ConstraintSeverity;
  description?: string;
  source?: string;
  source_url?: string;
  effective_date?: string;
  expiration_date?: string;
  status?: ConstraintStatus;
  conditions?: ConstraintCondition[];
  metadata?: Record<string, unknown>;
}

export interface ConstraintSummary {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  expiring_soon: number;
  recently_added: number;
}

// ============= Dependency Types =============

export interface Dependency {
  id: string;
  tenant_id: string;
  source_entity_id: string;
  target_entity_id: string;
  dependency_type: DependencyType;
  layer: DependencyLayer;
  strength: number;
  description?: string;
  metadata: Record<string, unknown>;
  is_critical: boolean;
  source_entity?: Entity;
  target_entity?: Entity;
  created_at: string;
  updated_at: string;
}

export type DependencyType =
  | "requires"
  | "provides"
  | "contracts_with"
  | "owns"
  | "employs"
  | "funds"
  | "regulates"
  | "partners_with"
  | "supplies"
  | "depends_on";

export type DependencyLayer =
  | "legal"
  | "financial"
  | "operational"
  | "human"
  | "academic"
  | "technical"
  | "supply_chain"
  | "regulatory";

export interface DependencyCreate {
  source_entity_id: string;
  target_entity_id: string;
  dependency_type: DependencyType;
  layer: DependencyLayer;
  strength?: number;
  description?: string;
  is_critical?: boolean;
  metadata?: Record<string, unknown>;
}

export interface DependencyUpdate {
  dependency_type?: DependencyType;
  layer?: DependencyLayer;
  strength?: number;
  description?: string;
  is_critical?: boolean;
  metadata?: Record<string, unknown>;
}

export interface DependencyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    total_nodes: number;
    total_edges: number;
    layers: Record<string, number>;
    critical_paths: number;
  };
}

export interface GraphNode {
  id: string;
  name: string;
  type: EntityType;
  risk_score?: number;
  layer?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: DependencyType;
  layer: DependencyLayer;
  strength: number;
  is_critical: boolean;
}

// ============= Risk Types =============

export interface RiskScore {
  id: string;
  entity_id: string;
  score: number;
  level: RiskLevel;
  factors: RiskFactor[];
  calculated_at: string;
  valid_until?: string;
}

export type RiskLevel = "critical" | "high" | "medium" | "low" | "minimal";

export interface RiskFactor {
  category: string;
  name: string;
  impact: number;
  weight: number;
  source: string;
  description?: string;
}

export interface RiskSummary {
  total_entities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  minimal_count: number;
  average_score: number;
  recent_escalations: number;
  recent_improvements: number;
  [key: `${string}_count`]: number | undefined;
}

export interface RiskTrend {
  date: string;
  average_score: number;
  critical_count: number;
  high_count: number;
}

export interface RiskJustification {
  entity_id: string;
  entity_name: string;
  current_score: number;
  current_level: RiskLevel;
  factors: RiskFactor[];
  constraint_impacts: ConstraintImpact[];
  dependency_impacts: DependencyImpact[];
  historical_context: HistoricalContext;
  assumptions: string[];
  data_sources: DataSource[];
  confidence_level: number;
  last_updated: string;
  override_info?: {
    overridden: boolean;
    override_score?: number;
    override_reason?: string;
    overridden_by?: string;
    overridden_at?: string;
  };
  justification?: {
    primary_factors: string[];
    secondary_factors: string[];
    mitigating_factors: string[];
    uncertainty_notes: string[];
  };
}

export interface ConstraintImpact {
  constraint_id: string;
  constraint_name: string;
  type: ConstraintType;
  severity: ConstraintSeverity;
  impact_score: number;
  reason: string;
}

export interface DependencyImpact {
  dependency_id: string;
  related_entity_name: string;
  relationship_type: DependencyType;
  layer: DependencyLayer;
  impact_score: number;
  is_critical: boolean;
}

export interface HistoricalContext {
  previous_scores: { date: string; score: number }[];
  trend: "improving" | "stable" | "worsening";
  significant_events: string[];
}

export interface DataSource {
  name: string;
  type: string;
  last_updated: string;
  reliability: "high" | "medium" | "low";
}

// ============= Scenario Types =============

export interface Scenario {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  type: ScenarioType;
  status: ScenarioStatus;
  hypothesis: string;
  parameters: ScenarioParameter[];
  results?: ScenarioResults;
  created_by: string;
  created_at: string;
  updated_at: string;
  archived_at?: string;
  trigger_entity_id?: string;
  affected_countries?: string[];
  affected_entity_types?: string[];
  outcome_notes?: string;
  lessons_learned?: string;
  run_count?: number;
}

export type ScenarioType =
  | "constraint_change"
  | "entity_status_change"
  | "dependency_failure"
  | "cascading_effect"
  | "stress_test"
  | "what_if";

export type ScenarioStatus =
  | "draft"
  | "running"
  | "completed"
  | "archived"
  | "failed";

export interface ScenarioParameter {
  name: string;
  type: "entity" | "constraint" | "dependency" | "numeric" | "boolean";
  value: string | number | boolean;
  entity_id?: string;
  constraint_id?: string;
}

export interface ScenarioResults {
  execution_time: number;
  affected_entities: AffectedEntity[];
  risk_changes: RiskChange[];
  cascading_effects: CascadingEffect[];
  recommendations: string[];
}

export interface AffectedEntity {
  entity_id: string;
  entity_name: string;
  impact_type: "direct" | "indirect";
  severity: ConstraintSeverity;
  description: string;
}

export interface RiskChange {
  entity_id: string;
  entity_name: string;
  old_score: number;
  new_score: number;
  change: number;
  reason: string;
}

export interface CascadingEffect {
  depth: number;
  source_entity: string;
  affected_entity: string;
  effect_type: string;
  probability: number;
  impact: number;
}

export interface ScenarioCreate {
  name: string;
  description?: string;
  type: ScenarioType;
  hypothesis: string;
  parameters: ScenarioParameter[];
}

export interface ScenarioUpdate {
  name?: string;
  description?: string;
  hypothesis?: string;
  parameters?: ScenarioParameter[];
}

// ============= Scenario Chain Types =============

export interface ScenarioChain {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  trigger_event: string;
  trigger_entity_id?: string;
  status: "active" | "archived";
  effects: ChainEffect[];
  created_at: string;
  updated_at: string;
}

export interface ChainEffect {
  id: string;
  chain_id: string;
  sequence_order: number;
  effect_type: string;
  target_entity_id?: string;
  delay_days: number;
  probability: number;
  impact_score: number;
  conditions: Record<string, unknown>;
}

export interface ChainSimulationResult {
  chain_id: string;
  scenario_chain_id: string;
  trigger_event: string;
  execution_time: number;
  depth_reached: number;
  effects: SimulatedEffect[];
  total_entities_affected: number;
  total_risk_change: number;
  immediate_effects: SimulatedEffect[];
  delayed_effects: SimulatedEffect[];
  timeline: { day: number; effects: SimulatedEffect[] }[];
  risk_trajectory: { day: number; risk_score: number }[];
  recommendations: string[];
}

export interface SimulatedEffect {
  depth: number;
  effect: ChainEffect;
  affected_entities: string[];
  risk_impact: number;
  propagation_probability: number;
}

// ============= Audit Types =============

export interface AuditLog {
  id: string;
  tenant_id: string;
  user_id: string;
  user_email: string;
  action: AuditAction;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export type AuditAction =
  | "create"
  | "read"
  | "update"
  | "delete"
  | "login"
  | "logout"
  | "export"
  | "import"
  | "run_scenario"
  | "calculate_risk"
  | "override";

// ============= User Types =============

export interface User {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  mfa_enabled: boolean;
  last_login?: string | null;
  created_at: string;
  updated_at: string;
  mfa_verified_at?: string | null;
  backup_codes_remaining?: number;
}

export type UserRole = "admin" | "analyst" | "viewer" | "auditor";

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface UserUpdate {
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

// ============= Monitoring Types =============

export interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  services: ServiceStatus[];
  last_check: string;
}

export interface ServiceStatus {
  name: string;
  status: "up" | "down" | "degraded";
  latency_ms?: number;
  last_check: string;
}

export interface SystemMetrics {
  entities_count: number;
  constraints_count: number;
  dependencies_count: number;
  users_count: number;
  scenarios_run_today: number;
  api_requests_24h: number;
  avg_response_time_ms: number;
}

export interface Alert {
  id: string;
  type: string;
  priority: AlertPriority;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  entity_id?: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
}

export type AlertPriority = "low" | "medium" | "high" | "critical";

// ============= AI Analysis Types =============

export interface AIAnalysis {
  id: string;
  tenant_id: string;
  analysis_type: AIAnalysisType;
  description: string;
  entity_ids?: string[];
  parameters: Record<string, unknown>;
  status: AIAnalysisStatus;
  results?: AIAnalysisResults;
  requested_by: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  completed_at?: string;
}

export type AIAnalysisType =
  | "anomaly"
  | "pattern"
  | "summary"
  | "scenario"
  | "clustering"
  | "prediction";

export type AIAnalysisStatus =
  | "pending"
  | "approved"
  | "running"
  | "completed"
  | "rejected"
  | "failed";

export interface AIAnalysisResults {
  summary: string;
  findings: AIFinding[];
  confidence: number;
  model_version: string;
  processing_time_ms: number;
}

export interface AIFinding {
  type: string;
  severity: ConstraintSeverity;
  description: string;
  affected_entities: string[];
  recommendation?: string;
  confidence: number;
}

export interface ModelCard {
  model_name: string;
  model_version: string;
  description: string;
  capabilities: string[];
  limitations: string[];
  training_data_summary: string;
  bias_considerations: string[];
  intended_use: string;
  out_of_scope_use: string[];
}

// ============= History Types =============

export interface TimelineEvent {
  id: string;
  timestamp: string;
  event_type: string;
  description: string;
  entity_id?: string;
  user_id?: string;
  details: Record<string, unknown>;
}

export interface Decision {
  id: string;
  tenant_id: string;
  decision_date: string;
  decision_summary: string;
  decision_type: string;
  entities_involved: string[];
  outcome_summary?: string;
  outcome_success?: boolean;
  lessons_learned?: string;
  resolved_at?: string;
  created_by: string;
  created_at: string;
}

export interface TransitionReport {
  id: string;
  title: string;
  period_start: string;
  period_end: string;
  executive_summary: string;
  risk_summary: RiskSummary;
  key_decisions: Decision[];
  entity_changes: EntityChange[];
  constraint_changes: ConstraintChange[];
  recommendations: string[];
  created_at: string;
}

export interface EntityChange {
  entity_id: string;
  entity_name: string;
  change_type: "created" | "updated" | "archived" | "risk_change";
  old_value?: string;
  new_value?: string;
  changed_at: string;
}

export interface ConstraintChange {
  constraint_id: string;
  constraint_name: string;
  change_type: "added" | "modified" | "expired" | "revoked";
  description: string;
  changed_at: string;
}

// ============= Pagination Types =============

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// ============= API Response Types =============

export interface ApiError {
  detail: string;
  status_code: number;
  error_code?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ============= MFA Types =============

export interface MFAStatus {
  enabled: boolean;
  mfa_enabled: boolean;
  backup_codes_remaining: number;
  mfa_verified_at?: string | null;
}

export interface MFASetupData {
  secret: string;
  qr_code: string;
  provisioning_uri: string;
  backup_codes: string[];
}
