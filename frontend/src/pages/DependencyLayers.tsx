import { useQuery } from "@tanstack/react-query";
import {
  Square3Stack3DIcon,
  ScaleIcon,
  BuildingLibraryIcon,
  CurrencyDollarIcon,
  CogIcon,
  UserGroupIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";
import { dependencyLayersApi } from "../services/api";

// Layer colors following PHASE_2_1_SUMMARY.md specification
const LAYER_COLORS: Record<string, { bg: string; text: string; border: string; icon: string }> = {
  legal: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", icon: "text-red-500" },
  financial: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", icon: "text-amber-500" },
  operational: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", icon: "text-blue-500" },
  human: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200", icon: "text-purple-500" },
  academic: { bg: "bg-green-50", text: "text-green-700", border: "border-green-200", icon: "text-green-500" },
};

const LAYER_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  legal: ScaleIcon,
  financial: CurrencyDollarIcon,
  operational: CogIcon,
  human: UserGroupIcon,
  academic: AcademicCapIcon,
};

interface LayerSummary {
  layers: Record<string, {
    count: number;
    avg_criticality: number;
    risk_weight: number;
  }>;
  total_dependencies: number;
  layer_descriptions: Record<string, string>;
}

export default function DependencyLayers() {
  const { data, isLoading, error } = useQuery<LayerSummary>({
    queryKey: ["dependency-layers-summary"],
    queryFn: async () => {
      const response = await dependencyLayersApi.summary();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Failed to load layer summary. Please try again.</p>
      </div>
    );
  }

  const layers = data?.layers || {};
  const descriptions = data?.layer_descriptions || {};

  // Calculate max count for bar chart scaling
  const maxCount = Math.max(...Object.values(layers).map(l => l.count), 1);

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Square3Stack3DIcon className="h-8 w-8 mr-3 text-primary-600" />
            Dependency Layers
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Multi-layer dependency modeling - understand how entities are connected across legal, financial, operational, human, and academic layers.
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-primary-100">
              <BuildingLibraryIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Dependencies</p>
              <p className="text-2xl font-bold text-gray-900">{data?.total_dependencies || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100">
              <Square3Stack3DIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Layers</p>
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(layers).filter(l => l.count > 0).length} / 5
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-amber-100">
              <ScaleIcon className="h-6 w-6 text-amber-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Highest Risk Layer</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">
                {Object.entries(layers).sort((a, b) =>
                  (b[1].count * b[1].risk_weight) - (a[1].count * a[1].risk_weight)
                )[0]?.[0] || "N/A"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Layer Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {Object.entries(layers).map(([layerName, stats]) => {
          const colors = LAYER_COLORS[layerName] || LAYER_COLORS.operational;
          const Icon = LAYER_ICONS[layerName] || CogIcon;
          const barWidth = maxCount > 0 ? (stats.count / maxCount) * 100 : 0;
          const weightedRisk = (stats.count * stats.avg_criticality * stats.risk_weight).toFixed(1);

          return (
            <div
              key={layerName}
              className={`card border ${colors.border} ${colors.bg}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg bg-white shadow-sm`}>
                    <Icon className={`h-6 w-6 ${colors.icon}`} />
                  </div>
                  <div className="ml-3">
                    <h3 className={`text-lg font-semibold capitalize ${colors.text}`}>
                      {layerName}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {descriptions[layerName] || "Dependencies in this layer"}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${colors.bg} ${colors.text} border ${colors.border}`}>
                  {stats.risk_weight}x risk
                </span>
              </div>

              <div className="space-y-3">
                {/* Count with bar */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Dependencies</span>
                    <span className="font-semibold">{stats.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        layerName === 'legal' ? 'bg-red-500' :
                        layerName === 'financial' ? 'bg-amber-500' :
                        layerName === 'operational' ? 'bg-blue-500' :
                        layerName === 'human' ? 'bg-purple-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${barWidth}%` }}
                    ></div>
                  </div>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-500">Avg Criticality</p>
                    <p className="text-lg font-bold text-gray-900">
                      {stats.avg_criticality.toFixed(1)}
                      <span className="text-xs text-gray-400 ml-1">/ 10</span>
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <p className="text-xs text-gray-500">Weighted Risk</p>
                    <p className="text-lg font-bold text-gray-900">{weightedRisk}</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Layer Risk Weight Legend */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Layer Risk Weights</h3>
        <p className="text-sm text-gray-600 mb-4">
          Different layers carry different risk multipliers based on their potential impact on operations.
          Higher weights indicate dependencies that pose greater risk if disrupted.
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Layer</th>
                <th className="table-header">Description</th>
                <th className="table-header text-center">Risk Weight</th>
                <th className="table-header text-center">Impact Level</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                { name: "legal", weight: 1.5, impact: "Critical" },
                { name: "financial", weight: 1.4, impact: "High" },
                { name: "human", weight: 1.2, impact: "Medium-High" },
                { name: "operational", weight: 1.0, impact: "Medium" },
                { name: "academic", weight: 0.8, impact: "Low-Medium" },
              ].map(({ name, weight, impact }) => {
                const colors = LAYER_COLORS[name];
                const Icon = LAYER_ICONS[name] || CogIcon;
                return (
                  <tr key={name} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div className="flex items-center">
                        <Icon className={`h-5 w-5 mr-2 ${colors.icon}`} />
                        <span className="font-medium capitalize">{name}</span>
                      </div>
                    </td>
                    <td className="table-cell text-sm text-gray-600">
                      {descriptions[name] || ""}
                    </td>
                    <td className="table-cell text-center">
                      <span className={`px-2 py-1 rounded text-sm font-medium ${colors.bg} ${colors.text}`}>
                        {weight}x
                      </span>
                    </td>
                    <td className="table-cell text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        impact === "Critical" ? "bg-red-100 text-red-800" :
                        impact === "High" ? "bg-orange-100 text-orange-800" :
                        impact === "Medium-High" ? "bg-yellow-100 text-yellow-800" :
                        impact === "Medium" ? "bg-blue-100 text-blue-800" :
                        "bg-green-100 text-green-800"
                      }`}>
                        {impact}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
