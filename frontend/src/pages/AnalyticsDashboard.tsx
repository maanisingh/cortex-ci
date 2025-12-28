import { useQuery } from "@tanstack/react-query";
import { risksApi, entitiesApi, constraintsApi } from "../services/api";
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ShieldExclamationIcon,
  BuildingOfficeIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentMagnifyingGlassIcon,
  ChartPieIcon,
} from "@heroicons/react/24/outline";

interface RiskSummary {
  total_entities: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  average_score: number;
  critical_alerts: number;
}

interface TrendData {
  date: string;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  average_score: number;
}

const RISK_COLORS = {
  high: { bg: "bg-red-500", text: "text-red-600", light: "bg-red-50" },
  medium: { bg: "bg-amber-500", text: "text-amber-600", light: "bg-amber-50" },
  low: { bg: "bg-green-500", text: "text-green-600", light: "bg-green-50" },
};

export default function AnalyticsDashboard() {
  // Fetch risk summary
  const { data: riskSummary } = useQuery<RiskSummary>({
    queryKey: ["risk-summary-analytics"],
    queryFn: async () => {
      const response = await risksApi.summary();
      return response.data;
    },
  });

  // Fetch risk trends
  const { data: riskTrends } = useQuery<TrendData[]>({
    queryKey: ["risk-trends-analytics"],
    queryFn: async () => {
      const response = await risksApi.trends(30);
      return response.data?.trends || [];
    },
  });

  // Fetch entity stats
  const { data: entityStats } = useQuery({
    queryKey: ["entity-stats-analytics"],
    queryFn: async () => {
      const response = await entitiesApi.list({ page_size: 1 });
      return response.data;
    },
  });

  // Fetch constraint summary
  const { data: constraintSummary } = useQuery({
    queryKey: ["constraint-summary-analytics"],
    queryFn: async () => {
      const response = await constraintsApi.summary();
      return response.data;
    },
  });

  // Calculate percentages for risk distribution
  const totalRiskEntities =
    (riskSummary?.high_risk_count || 0) +
    (riskSummary?.medium_risk_count || 0) +
    (riskSummary?.low_risk_count || 0);

  const riskDistribution = [
    {
      label: "High Risk",
      count: riskSummary?.high_risk_count || 0,
      percentage:
        totalRiskEntities > 0
          ? ((riskSummary?.high_risk_count || 0) / totalRiskEntities) * 100
          : 0,
      color: RISK_COLORS.high,
    },
    {
      label: "Medium Risk",
      count: riskSummary?.medium_risk_count || 0,
      percentage:
        totalRiskEntities > 0
          ? ((riskSummary?.medium_risk_count || 0) / totalRiskEntities) * 100
          : 0,
      color: RISK_COLORS.medium,
    },
    {
      label: "Low Risk",
      count: riskSummary?.low_risk_count || 0,
      percentage:
        totalRiskEntities > 0
          ? ((riskSummary?.low_risk_count || 0) / totalRiskEntities) * 100
          : 0,
      color: RISK_COLORS.low,
    },
  ];

  // Calculate trend direction
  const latestScore = riskTrends?.[0]?.average_score || 0;
  const previousScore = riskTrends?.[riskTrends.length - 1]?.average_score || 0;
  const trendDirection =
    latestScore > previousScore
      ? "up"
      : latestScore < previousScore
        ? "down"
        : "stable";
  const trendChange = Math.abs(latestScore - previousScore).toFixed(1);

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ChartBarIcon className="h-7 w-7 text-indigo-600" />
          Analytics Dashboard
        </h1>
        <p className="mt-2 text-sm text-gray-700">
          Comprehensive overview of your constraint intelligence platform
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Entities */}
        <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600">
                Total Entities
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {entityStats?.total?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <BuildingOfficeIcon className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-blue-600">
            Organizations, individuals, and vessels monitored
          </p>
        </div>

        {/* Active Constraints */}
        <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600">
                Active Constraints
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {constraintSummary?.total_active?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <ShieldExclamationIcon className="h-8 w-8 text-purple-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-purple-600">
            Sanctions and regulatory constraints in effect
          </p>
        </div>

        {/* Average Risk Score */}
        <div className="card bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-amber-600">
                Average Risk Score
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {(riskSummary?.average_score || 0).toFixed(1)}
              </p>
            </div>
            <div className="p-3 bg-amber-100 rounded-lg">
              <ExclamationTriangleIcon className="h-8 w-8 text-amber-600" />
            </div>
          </div>
          <div className="mt-2 flex items-center gap-1">
            {trendDirection === "up" ? (
              <ArrowTrendingUpIcon className="h-4 w-4 text-red-500" />
            ) : trendDirection === "down" ? (
              <ArrowTrendingDownIcon className="h-4 w-4 text-green-500" />
            ) : (
              <span className="text-gray-400">-</span>
            )}
            <span
              className={`text-xs ${
                trendDirection === "up"
                  ? "text-red-600"
                  : trendDirection === "down"
                    ? "text-green-600"
                    : "text-gray-500"
              }`}
            >
              {trendChange} pts over 30 days
            </span>
          </div>
        </div>

        {/* High Risk Entities */}
        <div className="card bg-gradient-to-br from-red-50 to-rose-50 border-red-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-600">
                High Risk Entities
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {riskSummary?.high_risk_count?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            </div>
          </div>
          <p className="mt-2 text-xs text-red-600">
            Require immediate attention and review
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Risk Distribution */}
        <div className="card lg:col-span-2">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <ChartPieIcon className="h-5 w-5 text-indigo-600" />
            Risk Distribution
          </h2>
          <div className="space-y-4">
            {riskDistribution.map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-sm font-medium ${item.color.text}`}>
                    {item.label}
                  </span>
                  <span className="text-sm text-gray-500">
                    {item.count} ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${item.color.bg}`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Visual Breakdown */}
          <div className="mt-6 flex h-8 rounded-lg overflow-hidden">
            <div
              className="bg-red-500 transition-all"
              style={{ width: `${riskDistribution[0].percentage}%` }}
            />
            <div
              className="bg-amber-500 transition-all"
              style={{ width: `${riskDistribution[1].percentage}%` }}
            />
            <div
              className="bg-green-500 transition-all"
              style={{ width: `${riskDistribution[2].percentage}%` }}
            />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <DocumentMagnifyingGlassIcon className="h-5 w-5 text-indigo-600" />
            Quick Stats
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-700">
                  Compliant Entities
                </span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {(riskSummary?.low_risk_count || 0).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <ExclamationTriangleIcon className="h-5 w-5 text-amber-500" />
                <span className="text-sm text-gray-700">Under Review</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {(riskSummary?.medium_risk_count || 0).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <ClockIcon className="h-5 w-5 text-blue-500" />
                <span className="text-sm text-gray-700">
                  Pending Verification
                </span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {constraintSummary?.pending_review || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <ShieldExclamationIcon className="h-5 w-5 text-red-500" />
                <span className="text-sm text-gray-700">Critical Alerts</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {riskSummary?.critical_alerts || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Trend Chart (Simplified visualization) */}
      <div className="card mb-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
          <ArrowTrendingUpIcon className="h-5 w-5 text-indigo-600" />
          Risk Score Trend (30 Days)
        </h2>
        {riskTrends && riskTrends.length > 0 ? (
          <div className="h-64 flex items-end gap-1">
            {riskTrends.slice(-30).map((trend, index) => {
              const height = (trend.average_score / 100) * 100;
              const getBarColor = (score: number) => {
                if (score >= 75) return "bg-red-500";
                if (score >= 50) return "bg-amber-500";
                if (score >= 25) return "bg-yellow-400";
                return "bg-green-500";
              };

              return (
                <div
                  key={index}
                  className="flex-1 flex flex-col items-center group relative"
                >
                  <div
                    className={`w-full rounded-t transition-all hover:opacity-80 ${getBarColor(
                      trend.average_score,
                    )}`}
                    style={{ height: `${Math.max(height, 5)}%` }}
                  />
                  <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                    {new Date(trend.date).toLocaleDateString()}:{" "}
                    {trend.average_score.toFixed(1)}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No trend data available
          </div>
        )}
        <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
          <span>30 days ago</span>
          <span>Today</span>
        </div>
      </div>

      {/* Constraint Types */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <ShieldExclamationIcon className="h-5 w-5 text-indigo-600" />
            Constraints by Type
          </h2>
          {constraintSummary?.by_type ? (
            <div className="space-y-3">
              {Object.entries(constraintSummary.by_type).map(
                ([type, count]) => (
                  <div
                    key={type}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {type.replace("_", " ")}
                    </span>
                    <span className="text-lg font-semibold text-indigo-600">
                      {(count as number).toLocaleString()}
                    </span>
                  </div>
                ),
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No constraint data available
            </p>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <BuildingOfficeIcon className="h-5 w-5 text-indigo-600" />
            Entities by Type
          </h2>
          {entityStats?.by_type ? (
            <div className="space-y-3">
              {Object.entries(entityStats.by_type).map(([type, count]) => (
                <div
                  key={type}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {type.replace("_", " ")}
                  </span>
                  <span className="text-lg font-semibold text-indigo-600">
                    {(count as number).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No entity data available
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
