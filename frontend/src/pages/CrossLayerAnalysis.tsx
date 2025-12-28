import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ShieldExclamationIcon,
  ScaleIcon,
  CurrencyDollarIcon,
  CogIcon,
  UserGroupIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";
import { dependencyLayersApi, entitiesApi } from "../services/api";

// Layer colors following PHASE_2_1_SUMMARY.md specification
const LAYER_COLORS: Record<
  string,
  { bg: string; text: string; border: string; bar: string }
> = {
  legal: {
    bg: "bg-red-50",
    text: "text-red-700",
    border: "border-red-200",
    bar: "bg-red-500",
  },
  financial: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
    bar: "bg-amber-500",
  },
  operational: {
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    bar: "bg-blue-500",
  },
  human: {
    bg: "bg-purple-50",
    text: "text-purple-700",
    border: "border-purple-200",
    bar: "bg-purple-500",
  },
  academic: {
    bg: "bg-green-50",
    text: "text-green-700",
    border: "border-green-200",
    bar: "bg-green-500",
  },
};

const LAYER_ICONS: Record<
  string,
  React.ComponentType<{ className?: string }>
> = {
  legal: ScaleIcon,
  financial: CurrencyDollarIcon,
  operational: CogIcon,
  human: UserGroupIcon,
  academic: AcademicCapIcon,
};

interface Entity {
  id: string;
  name: string;
  type: string;
}

interface LayerImpact {
  outgoing: number;
  incoming: number;
  risk_score: number;
}

interface CrossLayerImpactResponse {
  entity_id: string;
  entity_name: string;
  layer_impact: Record<string, LayerImpact>;
  total_cross_layer_risk: number;
  primary_exposure_layer: string;
  total_outgoing: number;
  total_incoming: number;
  unique_entities_affected: number;
  recommendation: string;
}

export default function CrossLayerAnalysis() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  // Search entities
  const { data: searchResults, isLoading: searchLoading } = useQuery({
    queryKey: ["entities-search", searchQuery],
    queryFn: async () => {
      if (!searchQuery || searchQuery.length < 2) return { items: [] };
      const response = await entitiesApi.list({
        search: searchQuery,
        page_size: 10,
      });
      return response.data;
    },
    enabled: searchQuery.length >= 2,
  });

  // Cross-layer impact analysis
  const {
    data: impactData,
    isLoading: impactLoading,
    error: impactError,
  } = useQuery<CrossLayerImpactResponse>({
    queryKey: ["cross-layer-impact", selectedEntityId],
    queryFn: async () => {
      const response = await dependencyLayersApi.crossLayerImpact(
        selectedEntityId!,
      );
      return response.data;
    },
    enabled: !!selectedEntityId,
  });

  const handleEntitySelect = (entity: Entity) => {
    setSelectedEntityId(entity.id);
    setSearchQuery(entity.name);
  };

  const getRiskLevel = (risk: number): { label: string; color: string } => {
    if (risk > 50) return { label: "HIGH", color: "text-red-600 bg-red-100" };
    if (risk > 25)
      return { label: "MEDIUM", color: "text-amber-600 bg-amber-100" };
    if (risk > 10) return { label: "LOW", color: "text-blue-600 bg-blue-100" };
    return { label: "MINIMAL", color: "text-green-600 bg-green-100" };
  };

  const maxRiskScore = impactData
    ? Math.max(
        ...Object.values(impactData.layer_impact).map((l) => l.risk_score),
        1,
      )
    : 1;

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <ShieldExclamationIcon className="h-8 w-8 mr-3 text-primary-600" />
            Cross-Layer Impact Analysis
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Analyze how disruption to an entity would cascade across different
            dependency layers.
          </p>
        </div>
      </div>

      {/* Search Box */}
      <div className="card mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Entity to Analyze
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            placeholder="Search entities by name..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              if (e.target.value.length < 2) {
                setSelectedEntityId(null);
              }
            }}
          />
        </div>

        {/* Search Results Dropdown */}
        {searchQuery.length >= 2 &&
          searchResults?.items?.length > 0 &&
          !selectedEntityId && (
            <div className="absolute z-10 mt-1 w-full max-w-md bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto">
              {searchResults.items.map((entity: Entity) => (
                <button
                  key={entity.id}
                  onClick={() => handleEntitySelect(entity)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center justify-between"
                >
                  <span className="font-medium">{entity.name}</span>
                  <span className="text-xs text-gray-500 uppercase">
                    {entity.type}
                  </span>
                </button>
              ))}
            </div>
          )}

        {searchLoading && searchQuery.length >= 2 && (
          <p className="mt-2 text-sm text-gray-500">Searching...</p>
        )}
      </div>

      {/* Impact Analysis Results */}
      {impactLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}

      {impactError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">
            Failed to load impact analysis. Please try again.
          </p>
        </div>
      )}

      {impactData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Total Risk Score
                  </p>
                  <p className="text-3xl font-bold text-gray-900">
                    {impactData.total_cross_layer_risk?.toFixed(1) ?? "0.0"}
                  </p>
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskLevel(impactData.total_cross_layer_risk).color}`}
                >
                  {getRiskLevel(impactData.total_cross_layer_risk).label}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <ArrowTrendingUpIcon className="h-8 w-8 text-blue-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Outgoing Dependencies
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {impactData.total_outgoing}
                  </p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <ArrowTrendingDownIcon className="h-8 w-8 text-purple-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Incoming Dependencies
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {impactData.total_incoming}
                  </p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-8 w-8 text-amber-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Entities Affected
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {impactData.unique_entities_affected}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Primary Exposure & Recommendation */}
          <div className="card mb-6">
            <div className="flex items-start">
              <div
                className={`p-3 rounded-lg ${LAYER_COLORS[impactData.primary_exposure_layer]?.bg || "bg-gray-100"}`}
              >
                {(() => {
                  const Icon =
                    LAYER_ICONS[impactData.primary_exposure_layer] || CogIcon;
                  return (
                    <Icon
                      className={`h-6 w-6 ${LAYER_COLORS[impactData.primary_exposure_layer]?.text || "text-gray-600"}`}
                    />
                  );
                })()}
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  Primary Exposure:{" "}
                  <span className="capitalize">
                    {impactData.primary_exposure_layer}
                  </span>{" "}
                  Layer
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {impactData.recommendation}
                </p>
              </div>
            </div>
          </div>

          {/* Layer-by-Layer Impact */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Impact by Layer
            </h3>
            <div className="space-y-4">
              {Object.entries(impactData.layer_impact)
                .sort((a, b) => b[1].risk_score - a[1].risk_score)
                .map(([layerName, impact]) => {
                  const colors =
                    LAYER_COLORS[layerName] || LAYER_COLORS.operational;
                  const Icon = LAYER_ICONS[layerName] || CogIcon;
                  const barWidth =
                    maxRiskScore > 0
                      ? (impact.risk_score / maxRiskScore) * 100
                      : 0;
                  const totalDeps = impact.outgoing + impact.incoming;

                  return (
                    <div
                      key={layerName}
                      className={`p-4 rounded-lg border ${colors.border} ${colors.bg}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Icon className={`h-5 w-5 mr-2 ${colors.text}`} />
                          <span
                            className={`font-semibold capitalize ${colors.text}`}
                          >
                            {layerName}
                          </span>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-sm font-medium ${colors.bg} ${colors.text}`}
                        >
                          Risk: {impact.risk_score?.toFixed(1) ?? "0.0"}
                        </span>
                      </div>

                      {/* Risk bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${colors.bar}`}
                          style={{ width: `${barWidth}%` }}
                        ></div>
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="bg-white rounded p-2 text-center">
                          <p className="text-gray-500">Outgoing</p>
                          <p className="font-bold text-gray-900">
                            {impact.outgoing}
                          </p>
                        </div>
                        <div className="bg-white rounded p-2 text-center">
                          <p className="text-gray-500">Incoming</p>
                          <p className="font-bold text-gray-900">
                            {impact.incoming}
                          </p>
                        </div>
                        <div className="bg-white rounded p-2 text-center">
                          <p className="text-gray-500">Total</p>
                          <p className="font-bold text-gray-900">{totalDeps}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!selectedEntityId && !impactLoading && (
        <div className="card text-center py-12">
          <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Select an Entity
          </h3>
          <p className="text-gray-500">
            Search for and select an entity above to view its cross-layer impact
            analysis.
          </p>
        </div>
      )}
    </div>
  );
}
