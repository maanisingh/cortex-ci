import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  PlusIcon,
  PlayIcon,
  LinkIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { scenarioChainsApi } from "../services/api";

interface ScenarioChain {
  id: string;
  name: string;
  description?: string;
  trigger_event: string;
  total_entities_affected: number;
  max_cascade_depth: number;
  estimated_timeline_days: number;
  overall_severity: string;
  total_risk_increase: number;
  is_active: boolean;
  last_simulated_at?: string;
  created_at: string;
}

interface SimulationResult {
  scenario_chain_id: string;
  trigger_event: string;
  immediate_effects: any[];
  delayed_effects: any[];
  total_entities_affected: number;
  max_cascade_depth: number;
  estimated_timeline_days: number;
  overall_severity: string;
  risk_impact_summary: Record<string, any>;
}

export default function ScenarioChains() {
  const [showForm, setShowForm] = useState(false);
  const [simulationResult, setSimulationResult] =
    useState<SimulationResult | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    trigger_event: "",
  });

  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["scenario-chains"],
    queryFn: async () => {
      const response = await scenarioChainsApi.list();
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: {
      name: string;
      description?: string;
      trigger_event: string;
    }) => scenarioChainsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenario-chains"] });
      setShowForm(false);
      setFormData({ name: "", description: "", trigger_event: "" });
    },
  });

  const simulateMutation = useMutation({
    mutationFn: (chainId: string) => scenarioChainsApi.simulate(chainId, 3),
    onSuccess: (response) => {
      setSimulationResult(response.data);
      queryClient.invalidateQueries({ queryKey: ["scenario-chains"] });
    },
  });

  const severityColors: Record<string, string> = {
    negligible: "bg-gray-100 text-gray-800",
    minor: "bg-blue-100 text-blue-800",
    moderate: "bg-yellow-100 text-yellow-800",
    significant: "bg-orange-100 text-orange-800",
    severe: "bg-red-100 text-red-800",
    catastrophic: "bg-red-200 text-red-900",
  };

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Scenario Chains</h1>
          <p className="mt-2 text-sm text-gray-700">
            Cascading effect prediction and multi-step scenario simulation
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="btn-primary"
            onClick={() => setShowForm(true)}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Chain
          </button>
        </div>
      </div>

      {/* Create Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Create Scenario Chain</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createMutation.mutate(formData);
              }}
            >
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Trigger Event
                  </label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={3}
                    placeholder="e.g., Major bank sanctioned by OFAC"
                    value={formData.trigger_event}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        trigger_event: e.target.value,
                      })
                    }
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description (Optional)
                  </label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={2}
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? "Creating..." : "Create Chain"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Simulation Result Modal */}
      {simulationResult && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl my-8 mx-4">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">Cascade Simulation Results</h2>
              <button
                onClick={() => setSimulationResult(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <span className="text-2xl">&times;</span>
              </button>
            </div>

            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {simulationResult.total_entities_affected}
                </div>
                <div className="text-sm text-gray-600">Entities Affected</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {simulationResult.max_cascade_depth}
                </div>
                <div className="text-sm text-gray-600">Cascade Depth</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {simulationResult.estimated_timeline_days}
                </div>
                <div className="text-sm text-gray-600">Days Timeline</div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <span
                  className={`inline-flex px-2 py-1 rounded text-sm font-medium ${severityColors[simulationResult.overall_severity]}`}
                >
                  {simulationResult.overall_severity.toUpperCase()}
                </span>
                <div className="text-sm text-gray-600 mt-1">Severity</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-2 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
                  Immediate Effects ({simulationResult.immediate_effects.length}
                  )
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {simulationResult.immediate_effects.map(
                    (effect: any, i: number) => (
                      <div
                        key={i}
                        className="bg-red-50 p-3 rounded border border-red-100"
                      >
                        <div className="font-medium">{effect.entity_name}</div>
                        <div className="text-sm text-gray-600">
                          {effect.effect_description}
                        </div>
                        <div className="text-xs mt-1">
                          <span
                            className={`px-1.5 py-0.5 rounded ${severityColors[effect.severity]}`}
                          >
                            {effect.severity}
                          </span>
                          <span className="ml-2">
                            Risk +{effect.risk_score_delta}
                          </span>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-2 flex items-center">
                  <LinkIcon className="h-5 w-5 text-orange-500 mr-2" />
                  Delayed Effects ({simulationResult.delayed_effects.length})
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {simulationResult.delayed_effects.map(
                    (effect: any, i: number) => (
                      <div
                        key={i}
                        className="bg-orange-50 p-3 rounded border border-orange-100"
                      >
                        <div className="font-medium">{effect.entity_name}</div>
                        <div className="text-sm text-gray-600">
                          {effect.effect_description}
                        </div>
                        <div className="text-xs mt-1">
                          <span
                            className={`px-1.5 py-0.5 rounded ${severityColors[effect.severity]}`}
                          >
                            {effect.severity}
                          </span>
                          <span className="ml-2">
                            +{effect.time_delay_days} days
                          </span>
                          <span className="ml-2">
                            Depth: {effect.cascade_depth}
                          </span>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t">
              <h3 className="font-semibold mb-2">Risk Impact Summary</h3>
              <div className="text-sm text-gray-600">
                Total Risk Increase:{" "}
                <span className="font-bold text-red-600">
                  +{simulationResult.risk_impact_summary.total_risk_increase}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chains List */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Name</th>
                <th className="table-header">Trigger Event</th>
                <th className="table-header">Affected</th>
                <th className="table-header">Depth</th>
                <th className="table-header">Severity</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    Loading...
                  </td>
                </tr>
              ) : !data?.length ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No scenario chains found. Create one to start cascade
                    analysis.
                  </td>
                </tr>
              ) : (
                data.map((chain: ScenarioChain) => (
                  <tr key={chain.id} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div className="font-medium text-gray-900">
                        {chain.name}
                      </div>
                      {chain.description && (
                        <div className="text-xs text-gray-500 truncate max-w-xs">
                          {chain.description}
                        </div>
                      )}
                    </td>
                    <td className="table-cell">
                      <div className="text-sm text-gray-600 truncate max-w-xs">
                        {chain.trigger_event}
                      </div>
                    </td>
                    <td className="table-cell text-center font-medium">
                      {chain.total_entities_affected}
                    </td>
                    <td className="table-cell text-center">
                      {chain.max_cascade_depth}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${severityColors[chain.overall_severity] || "bg-gray-100"}`}
                      >
                        {chain.overall_severity}
                      </span>
                    </td>
                    <td className="table-cell">
                      <button
                        onClick={() => simulateMutation.mutate(chain.id)}
                        disabled={simulateMutation.isPending}
                        className="text-primary-600 hover:text-primary-900 text-sm flex items-center"
                      >
                        <PlayIcon className="h-4 w-4 mr-1" />
                        {simulateMutation.isPending
                          ? "Simulating..."
                          : "Simulate"}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
