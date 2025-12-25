import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import {
  BeakerIcon,
  ChartBarIcon,
  ArrowPathIcon,
  PlayIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowsRightLeftIcon,
  ShieldExclamationIcon,
} from "@heroicons/react/24/outline";

interface SimulationResult {
  simulation_id: string;
  simulation_type: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  iterations: number;
  total_iterations: number;
  progress: number;
  results: Record<string, unknown>;
  metrics: Record<string, number>;
  duration_seconds: number | null;
  errors: string[];
}

const SIMULATION_TYPES = [
  {
    id: "monte_carlo",
    name: "Monte Carlo",
    description: "Probabilistic risk distribution analysis",
    icon: ChartBarIcon,
    color: "indigo",
  },
  {
    id: "cascade",
    name: "Cascade Analysis",
    description: "Impact propagation through dependencies",
    icon: ArrowsRightLeftIcon,
    color: "purple",
  },
  {
    id: "what_if",
    name: "What-If Analysis",
    description: "Scenario-based risk projections",
    icon: BeakerIcon,
    color: "blue",
  },
  {
    id: "stress_test",
    name: "Stress Test",
    description: "Resilience under extreme conditions",
    icon: ShieldExclamationIcon,
    color: "red",
  },
];

export default function Simulations() {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [monteCarloIterations, setMonteCarloIterations] = useState(1000);
  const [confidenceLevel, setConfidenceLevel] = useState(0.95);
  const [cascadeTrigger, setCascadeTrigger] = useState("");
  const [cascadeDepth, setCascadeDepth] = useState(5);
  const [whatIfName, setWhatIfName] = useState("");
  const [whatIfRiskMultiplier, setWhatIfRiskMultiplier] = useState(1.0);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [activeResult, setActiveResult] = useState<SimulationResult | null>(null);

  // Fetch simulation history
  const { data: simulations, refetch } = useQuery<{ simulations: SimulationResult[] }>({
    queryKey: ["simulations"],
    queryFn: async () => {
      const response = await api.get("/v1/simulations/");
      return response.data;
    },
    refetchInterval: 5000,
  });

  // Monte Carlo mutation
  const monteCarloMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post("/v1/simulations/monte-carlo", {
        iterations: monteCarloIterations,
        confidence_level: confidenceLevel,
        risk_volatility: 0.15,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setActiveResult(data);
      refetch();
    },
  });

  // Cascade mutation
  const cascadeMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post("/v1/simulations/cascade", {
        trigger_entity_id: cascadeTrigger,
        max_depth: cascadeDepth,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setActiveResult(data);
      refetch();
    },
  });

  // What-if mutation
  const whatIfMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post("/v1/simulations/what-if", {
        name: whatIfName || "Custom Scenario",
        description: "User-defined what-if analysis",
        global_modifiers: {
          risk_multiplier: whatIfRiskMultiplier,
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setActiveResult(data);
      refetch();
    },
  });

  // Stress test mutation
  const stressTestMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post("/v1/simulations/stress-test", {
        scenarios: selectedScenarios.length > 0 ? selectedScenarios : undefined,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setActiveResult(data);
      refetch();
    },
  });

  const runSimulation = () => {
    switch (selectedType) {
      case "monte_carlo":
        monteCarloMutation.mutate();
        break;
      case "cascade":
        if (cascadeTrigger) cascadeMutation.mutate();
        break;
      case "what_if":
        whatIfMutation.mutate();
        break;
      case "stress_test":
        stressTestMutation.mutate();
        break;
    }
  };

  const isLoading =
    monteCarloMutation.isPending ||
    cascadeMutation.isPending ||
    whatIfMutation.isPending ||
    stressTestMutation.isPending;

  const renderConfigPanel = () => {
    switch (selectedType) {
      case "monte_carlo":
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Iterations
              </label>
              <input
                type="range"
                min={100}
                max={10000}
                step={100}
                value={monteCarloIterations}
                onChange={(e) => setMonteCarloIterations(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-500">
                {monteCarloIterations.toLocaleString()} iterations
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Confidence Level
              </label>
              <select
                value={confidenceLevel}
                onChange={(e) => setConfidenceLevel(Number(e.target.value))}
                className="input"
              >
                <option value={0.9}>90%</option>
                <option value={0.95}>95%</option>
                <option value={0.99}>99%</option>
              </select>
            </div>
          </div>
        );
      case "cascade":
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Trigger Entity ID
              </label>
              <input
                type="text"
                value={cascadeTrigger}
                onChange={(e) => setCascadeTrigger(e.target.value)}
                placeholder="Enter entity UUID"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max Cascade Depth
              </label>
              <input
                type="range"
                min={1}
                max={10}
                value={cascadeDepth}
                onChange={(e) => setCascadeDepth(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-500">{cascadeDepth} levels</span>
            </div>
          </div>
        );
      case "what_if":
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Scenario Name
              </label>
              <input
                type="text"
                value={whatIfName}
                onChange={(e) => setWhatIfName(e.target.value)}
                placeholder="My Scenario"
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Risk Multiplier
              </label>
              <input
                type="range"
                min={0.5}
                max={2.0}
                step={0.1}
                value={whatIfRiskMultiplier}
                onChange={(e) => setWhatIfRiskMultiplier(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-500">
                {whatIfRiskMultiplier.toFixed(1)}x risk modifier
              </span>
            </div>
          </div>
        );
      case "stress_test":
        return (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Stress Scenarios
            </label>
            {[
              "regulatory_crackdown",
              "market_crisis",
              "geopolitical_event",
              "supply_chain_disruption",
            ].map((scenario) => (
              <label key={scenario} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selectedScenarios.includes(scenario)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedScenarios([...selectedScenarios, scenario]);
                    } else {
                      setSelectedScenarios(
                        selectedScenarios.filter((s) => s !== scenario)
                      );
                    }
                  }}
                  className="rounded"
                />
                <span className="text-sm capitalize">
                  {scenario.replace(/_/g, " ")}
                </span>
              </label>
            ))}
          </div>
        );
      default:
        return (
          <p className="text-gray-500 text-center py-8">
            Select a simulation type to configure
          </p>
        );
    }
  };

  const renderResults = (result: SimulationResult) => {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 capitalize">
            {result.simulation_type.replace(/_/g, " ")} Results
          </h3>
          <span
            className={`px-2 py-1 text-xs rounded-full ${
              result.status === "completed"
                ? "bg-green-100 text-green-800"
                : result.status === "running"
                ? "bg-blue-100 text-blue-800"
                : "bg-red-100 text-red-800"
            }`}
          >
            {result.status}
          </span>
        </div>

        {result.progress < 100 && result.status === "running" && (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all"
                style={{ width: `${result.progress}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">
              {result.iterations} / {result.total_iterations} iterations
            </span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          {Object.entries(result.metrics).map(([key, value]) => (
            <div key={key} className="bg-gray-50 p-3 rounded-lg">
              <span className="text-xs text-gray-500 capitalize">
                {key.replace(/_/g, " ")}
              </span>
              <p className="text-lg font-semibold text-gray-900">
                {typeof value === "number" ? value.toLocaleString() : value}
              </p>
            </div>
          ))}
        </div>

        {result.duration_seconds && (
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <ClockIcon className="h-4 w-4" />
            Completed in {result.duration_seconds.toFixed(2)}s
          </p>
        )}

        {result.results && Object.keys(result.results).length > 0 && (
          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-indigo-600 hover:text-indigo-800">
              View detailed results
            </summary>
            <pre className="mt-2 text-xs bg-gray-50 p-4 rounded overflow-auto max-h-64">
              {JSON.stringify(result.results, null, 2)}
            </pre>
          </details>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BeakerIcon className="h-7 w-7 text-indigo-600" />
          Advanced Simulations
        </h1>
        <p className="mt-2 text-sm text-gray-700">
          Run sophisticated risk analysis simulations and stress tests
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulation Type Selection */}
        <div className="lg:col-span-2">
          <div className="card mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Select Simulation Type
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {SIMULATION_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedType === type.id
                      ? `border-${type.color}-500 bg-${type.color}-50`
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <type.icon
                    className={`h-6 w-6 ${
                      selectedType === type.id
                        ? `text-${type.color}-600`
                        : "text-gray-400"
                    }`}
                  />
                  <h3 className="mt-2 font-medium text-gray-900">{type.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Configuration Panel */}
          <div className="card mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Configuration
            </h2>
            {renderConfigPanel()}

            <div className="mt-6 flex gap-3">
              <button
                onClick={runSimulation}
                disabled={!selectedType || isLoading}
                className="btn-primary flex items-center gap-2"
              >
                {isLoading ? (
                  <ArrowPathIcon className="h-5 w-5 animate-spin" />
                ) : (
                  <PlayIcon className="h-5 w-5" />
                )}
                {isLoading ? "Running..." : "Run Simulation"}
              </button>
            </div>
          </div>

          {/* Active Result */}
          {activeResult && renderResults(activeResult)}
        </div>

        {/* Simulation History */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Recent Simulations
          </h2>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {simulations?.simulations?.map((sim) => (
              <button
                key={sim.simulation_id}
                onClick={() => setActiveResult(sim)}
                className={`w-full p-3 rounded-lg border text-left transition-all ${
                  activeResult?.simulation_id === sim.simulation_id
                    ? "border-indigo-500 bg-indigo-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">
                    {sim.simulation_type.replace(/_/g, " ")}
                  </span>
                  {sim.status === "completed" ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : sim.status === "running" ? (
                    <ArrowPathIcon className="h-4 w-4 text-blue-500 animate-spin" />
                  ) : (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(sim.started_at).toLocaleString()}
                </p>
              </button>
            )) || (
              <p className="text-gray-500 text-center py-4">No simulations yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
