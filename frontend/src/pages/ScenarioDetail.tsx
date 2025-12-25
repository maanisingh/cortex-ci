import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { scenariosApi, entitiesApi } from "../services/api";

interface Scenario {
  id: string;
  name: string;
  description: string;
  type: string;
  status: string;
  trigger_entity_id: string;
  affected_countries: string[];
  affected_entity_types: string[];
  parameters: Record<string, any>;
  results: ScenarioResults | null;
  outcome_notes: string;
  lessons_learned: string;
  created_at: string;
  updated_at: string;
  completed_at: string;
}

interface ScenarioResults {
  total_affected_entities: number;
  cascade_depth: number;
  affected_entities: AffectedEntity[];
  risk_delta: Record<string, number>;
  recommendations: string[];
  execution_time_ms: number;
}

interface AffectedEntity {
  entity_id: string;
  entity_name: string;
  entity_type: string;
  impact_level: string;
  cascade_level: number;
  risk_before: number;
  risk_after: number;
  impact_reason: string;
}

interface Entity {
  id: string;
  name: string;
  type: string;
}

export default function ScenarioDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [triggerEntity, setTriggerEntity] = useState<Entity | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (id) {
      loadScenarioData();
    }
  }, [id]);

  const loadScenarioData = async () => {
    try {
      setLoading(true);
      const scenarioRes = await scenariosApi.get(id!);
      setScenario(scenarioRes.data);

      // Load trigger entity if exists
      if (scenarioRes.data.trigger_entity_id) {
        try {
          const entityRes = await entitiesApi.get(
            scenarioRes.data.trigger_entity_id,
          );
          setTriggerEntity(entityRes.data);
        } catch {
          // Entity might not exist
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load scenario");
    } finally {
      setLoading(false);
    }
  };

  const handleRunScenario = async () => {
    if (!id) return;
    try {
      setRunning(true);
      await scenariosApi.run(id);
      // Reload to get results
      await loadScenarioData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to run scenario");
    } finally {
      setRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      running: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      archived: "bg-purple-100 text-purple-800",
    };
    return colors[status?.toLowerCase()] || "bg-gray-100 text-gray-800";
  };

  const getImpactColor = (impact: string) => {
    switch (impact?.toLowerCase()) {
      case "critical":
        return "bg-red-100 text-red-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const typeLabels: Record<string, string> = {
    entity_sanctioned: "Entity Sanctioned",
    country_embargo: "Country Embargo",
    supplier_unavailable: "Supplier Unavailable",
    financial_restriction: "Financial Restriction",
    regulatory_change: "Regulatory Change",
    custom: "Custom",
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !scenario) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error || "Scenario not found"}</p>
        <button
          onClick={() => navigate("/scenarios")}
          className="mt-2 text-red-600 underline"
        >
          Back to Scenarios
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate("/scenarios")}
            className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
          >
            ← Back to Scenarios
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{scenario.name}</h1>
          <p className="text-gray-500">
            {typeLabels[scenario.type] || scenario.type}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(scenario.status)}`}
          >
            {scenario.status}
          </span>
          {scenario.status === "draft" && (
            <button
              onClick={handleRunScenario}
              disabled={running}
              className="btn-primary"
            >
              {running ? "Running..." : "Run Scenario"}
            </button>
          )}
        </div>
      </div>

      {/* Main Info Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scenario Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Scenario Configuration</h2>

          {scenario.description && (
            <div className="mb-4">
              <h3 className="text-sm text-gray-500 mb-1">Description</h3>
              <p className="text-gray-900">{scenario.description}</p>
            </div>
          )}

          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Type</dt>
              <dd className="font-medium">
                {typeLabels[scenario.type] || scenario.type}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Status</dt>
              <dd className="font-medium capitalize">{scenario.status}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Created</dt>
              <dd className="font-medium">
                {new Date(scenario.created_at).toLocaleString()}
              </dd>
            </div>
            {scenario.completed_at && (
              <div>
                <dt className="text-sm text-gray-500">Completed</dt>
                <dd className="font-medium">
                  {new Date(scenario.completed_at).toLocaleString()}
                </dd>
              </div>
            )}
            {triggerEntity && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Trigger Entity</dt>
                <dd>
                  <Link
                    to={`/entities/${triggerEntity.id}`}
                    className="text-primary-600 hover:underline font-medium"
                  >
                    {triggerEntity.name}
                  </Link>
                  <span className="text-gray-500 ml-2">
                    ({triggerEntity.type})
                  </span>
                </dd>
              </div>
            )}
            {scenario.affected_countries?.length > 0 && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Affected Countries</dt>
                <dd className="flex flex-wrap gap-1 mt-1">
                  {scenario.affected_countries.map((country) => (
                    <span
                      key={country}
                      className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-sm"
                    >
                      {country}
                    </span>
                  ))}
                </dd>
              </div>
            )}
            {scenario.affected_entity_types?.length > 0 && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Affected Entity Types</dt>
                <dd className="flex flex-wrap gap-1 mt-1">
                  {scenario.affected_entity_types.map((type) => (
                    <span
                      key={type}
                      className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-sm capitalize"
                    >
                      {type.toLowerCase()}
                    </span>
                  ))}
                </dd>
              </div>
            )}
          </dl>
        </div>

        {/* Results Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Results Summary</h2>
          {scenario.results ? (
            <div className="space-y-4">
              <div className="text-center p-4 rounded-lg bg-gray-50">
                <div className="text-3xl font-bold text-gray-900">
                  {scenario.results.total_affected_entities}
                </div>
                <div className="text-sm text-gray-500">Affected Entities</div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Cascade Depth</span>
                  <span className="font-medium">
                    {scenario.results.cascade_depth} levels
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Execution Time</span>
                  <span className="font-medium">
                    {scenario.results.execution_time_ms}ms
                  </span>
                </div>
              </div>
              {scenario.results.risk_delta &&
                Object.keys(scenario.results.risk_delta).length > 0 && (
                  <div className="border-t pt-3">
                    <h3 className="text-sm text-gray-500 mb-2">Risk Changes</h3>
                    {Object.entries(scenario.results.risk_delta).map(
                      ([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600 capitalize">
                            {key.replace(/_/g, " ")}
                          </span>
                          <span
                            className={`font-medium ${value > 0 ? "text-red-600" : "text-green-600"}`}
                          >
                            {value > 0 ? "+" : ""}
                            {value.toFixed(1)}
                          </span>
                        </div>
                      ),
                    )}
                  </div>
                )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <p>No results yet</p>
              {scenario.status === "draft" && (
                <button
                  onClick={handleRunScenario}
                  disabled={running}
                  className="mt-2 text-primary-600 hover:underline text-sm"
                >
                  Run scenario to see results
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Affected Entities */}
      {scenario.results?.affected_entities &&
        scenario.results.affected_entities.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">
              Affected Entities ({scenario.results.affected_entities.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Entity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Impact
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Cascade Level
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Risk Change
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Reason
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {scenario.results.affected_entities.map((entity, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <Link
                          to={`/entities/${entity.entity_id}`}
                          className="text-primary-600 hover:underline font-medium"
                        >
                          {entity.entity_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                        {entity.entity_type?.toLowerCase()}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${getImpactColor(entity.impact_level)}`}
                        >
                          {entity.impact_level}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        Level {entity.cascade_level}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={
                            entity.risk_after > entity.risk_before
                              ? "text-red-600"
                              : "text-green-600"
                          }
                        >
                          {entity.risk_before?.toFixed(1)} →{" "}
                          {entity.risk_after?.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">
                        {entity.impact_reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      {/* Recommendations */}
      {scenario.results?.recommendations &&
        scenario.results.recommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Recommendations</h2>
            <ul className="space-y-2">
              {scenario.results.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

      {/* Outcome & Lessons Learned (for archived scenarios) */}
      {scenario.status === "archived" &&
        (scenario.outcome_notes || scenario.lessons_learned) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {scenario.outcome_notes && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Outcome Notes</h2>
                <p className="text-gray-700">{scenario.outcome_notes}</p>
              </div>
            )}
            {scenario.lessons_learned && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Lessons Learned</h2>
                <p className="text-gray-700">{scenario.lessons_learned}</p>
              </div>
            )}
          </div>
        )}

      {/* Parameters (if any) */}
      {scenario.parameters && Object.keys(scenario.parameters).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Scenario Parameters</h2>
          <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
            {JSON.stringify(scenario.parameters, null, 2)}
          </pre>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <Link
          to={`/audit?resource_type=scenario&resource_id=${id}`}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          View Audit History
        </Link>
      </div>
    </div>
  );
}
