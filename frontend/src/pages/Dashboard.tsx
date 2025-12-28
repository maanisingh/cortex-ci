import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from "chart.js";
import { Pie, Line } from "react-chartjs-2";
import {
  BuildingOfficeIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  LinkIcon,
  InformationCircleIcon,
  PlusIcon,
  BeakerIcon,
  DocumentMagnifyingGlassIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";

import {
  risksApi,
  entitiesApi,
  constraintsApi,
  dependenciesApi,
} from "../services/api";
import { useLanguage } from "../contexts/LanguageContext";

// Tooltip component for contextual help
function InfoTooltip({ text }: { text: string }) {
  return (
    <div className="group relative inline-block ml-1">
      <InformationCircleIcon className="h-4 w-4 text-gray-400 hover:text-indigo-500 cursor-help" />
      <div className="invisible group-hover:visible absolute z-50 w-64 p-2 mt-1 text-xs text-white bg-gray-900 rounded-lg shadow-lg -left-28 top-full">
        {text}
        <div className="absolute w-2 h-2 bg-gray-900 rotate-45 -top-1 left-1/2 transform -translate-x-1/2"></div>
      </div>
    </div>
  );
}

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
);

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(" ");
}

export default function Dashboard() {
  const { t } = useLanguage();

  // Fetch risk summary
  const { data: riskSummary, isLoading: loadingRisk } = useQuery({
    queryKey: ["risk-summary"],
    queryFn: async () => {
      const response = await risksApi.summary();
      return response.data;
    },
  });

  // Fetch risk trends
  const { data: riskTrends } = useQuery({
    queryKey: ["risk-trends"],
    queryFn: async () => {
      const response = await risksApi.trends(30);
      return response.data;
    },
  });

  // Fetch entities count
  const { data: entitiesData } = useQuery({
    queryKey: ["entities-count"],
    queryFn: async () => {
      const response = await entitiesApi.list({ page_size: 1 });
      return response.data;
    },
  });

  // Fetch constraints summary
  const { data: constraintsSummary } = useQuery({
    queryKey: ["constraints-summary"],
    queryFn: async () => {
      const response = await constraintsApi.summary();
      return response.data;
    },
  });

  // Fetch dependency graph stats
  const { data: graphData } = useQuery({
    queryKey: ["dependency-graph"],
    queryFn: async () => {
      const response = await dependenciesApi.graph();
      return response.data;
    },
  });

  const stats = [
    {
      name: t("riskObjects"),
      value: entitiesData?.total || 0,
      icon: BuildingOfficeIcon,
      color: "bg-blue-500",
      href: "/entities",
    },
    {
      name: t("activeControls"),
      value: constraintsSummary?.total || 0,
      icon: DocumentTextIcon,
      color: "bg-purple-500",
      href: "/constraints",
    },
    {
      name: t("riskRelationships"),
      value: graphData?.stats?.total_edges || 0,
      icon: LinkIcon,
      color: "bg-green-500",
      href: "/dependencies",
    },
    {
      name: t("criticalRisks"),
      value: riskSummary?.critical_count || 0,
      icon: ExclamationTriangleIcon,
      color: "bg-red-500",
      href: "/risks",
    },
  ];

  // Risk distribution chart data
  const riskDistributionData = {
    labels: [t("critical"), t("high"), t("medium"), t("low")],
    datasets: [
      {
        data: [
          riskSummary?.critical_count || 0,
          riskSummary?.high_count || 0,
          riskSummary?.medium_count || 0,
          riskSummary?.low_count || 0,
        ],
        backgroundColor: ["#ef4444", "#f97316", "#eab308", "#22c55e"],
        borderWidth: 0,
      },
    ],
  };

  // Risk trend chart data
  const trendLabels =
    riskTrends?.map((t: { date: string }) =>
      new Date(t.date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
    ) || [];

  const riskTrendData = {
    labels: trendLabels,
    datasets: [
      {
        label: t("averageRiskScore"),
        data:
          riskTrends?.map((t: { average_score: number }) => t.average_score) ||
          [],
        borderColor: "#0ea5e9",
        backgroundColor: "rgba(14, 165, 233, 0.1)",
        fill: true,
        tension: 0.4,
      },
    ],
  };

  return (
    <div data-tour="dashboard">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          {t("grcDashboard")}
          <InfoTooltip text={t("grcDashboardTooltip")} />
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {t("grcDashboardSubtitle")}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            to={stat.href}
            className="card hover:shadow-lg transition-shadow cursor-pointer"
          >
            <div className="flex items-center">
              <div
                className={classNames(
                  "flex-shrink-0 rounded-md p-3",
                  stat.color,
                )}
              >
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 flex items-center">
          {t("quickActions")}
          <InfoTooltip text={t("quickActionsTooltip")} />
        </h3>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/entities?action=new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            {t("addRiskObject")}
          </Link>
          <Link
            to="/constraints?action=new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            {t("addControl")}
          </Link>
          <Link
            to="/scenarios?action=new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
          >
            <BeakerIcon className="h-4 w-4 mr-2" />
            {t("newRiskScenario")}
          </Link>
          <Link
            to="/risks"
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            {t("riskRegister")}
          </Link>
          <Link
            to="/compliance"
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <DocumentMagnifyingGlassIcon className="h-4 w-4 mr-2" />
            {t("complianceStatus")}
          </Link>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 mb-8">
        {/* Risk Distribution */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            {t("riskDistribution")}
            <InfoTooltip text={t("riskDistributionTooltip")} />
          </h3>
          <div className="h-64 flex items-center justify-center">
            {loadingRisk ? (
              <div className="text-gray-500">{t("loading")}</div>
            ) : riskSummary?.total_entities > 0 ? (
              <Pie
                data={riskDistributionData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: "bottom",
                    },
                  },
                }}
              />
            ) : (
              <div className="text-gray-500">{t("noRiskData")}</div>
            )}
          </div>
        </div>

        {/* Risk Trend */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            {t("riskTrend")}
            <InfoTooltip text={t("riskTrendTooltip")} />
          </h3>
          <div className="h-64">
            {riskTrends?.length > 0 ? (
              <Line
                data={riskTrendData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                    },
                  },
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                {t("noTrendData")}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Escalations & Improvements */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              {t("recentEscalations")}
              <InfoTooltip text={t("recentEscalationsTooltip")} />
            </h3>
            <span className="flex items-center text-red-600">
              <ArrowTrendingUpIcon className="h-5 w-5 mr-1" />
              {riskSummary?.recent_escalations || 0}
            </span>
          </div>
          <p className="text-sm text-gray-500">
            {t("escalationsDescription")}
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              {t("recentImprovements")}
              <InfoTooltip text={t("recentImprovementsTooltip")} />
            </h3>
            <span className="flex items-center text-green-600">
              <ArrowTrendingDownIcon className="h-5 w-5 mr-1" />
              {riskSummary?.recent_improvements || 0}
            </span>
          </div>
          <p className="text-sm text-gray-500">
            {t("improvementsDescription")}
          </p>
        </div>
      </div>

      {/* Constraint & Dependency Overview */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Controls by Type */}
        <div className="card" data-tour="constraints">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            {t("controlsByType")}
            <InfoTooltip text={t("controlsByTypeTooltip")} />
          </h3>
          <div className="space-y-3">
            {constraintsSummary?.by_type &&
              Object.entries(constraintsSummary.by_type).map(
                ([type, count]: [string, unknown]) =>
                  (count as number) > 0 && (
                    <div
                      key={type}
                      className="flex items-center justify-between"
                    >
                      <span className="text-sm font-medium text-gray-600 capitalize">
                        {type}
                      </span>
                      <span className="text-sm font-semibold text-gray-900">
                        {count as number}
                      </span>
                    </div>
                  ),
              )}
            {!constraintsSummary?.by_type && (
              <p className="text-sm text-gray-500">
                {t("noControlsConfigured")}
              </p>
            )}
          </div>
          {constraintsSummary?.expiring_soon > 0 && (
            <div className="mt-4 p-3 bg-orange-50 rounded-md">
              <p className="text-sm text-orange-800">
                <strong>{constraintsSummary.expiring_soon}</strong> {t("controlsRequireReview")}
              </p>
            </div>
          )}
        </div>

        {/* Risk Relationships by Layer */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            {t("riskRelationshipsByLayer")}
            <InfoTooltip text={t("riskRelationshipsByLayerTooltip")} />
          </h3>
          <div className="space-y-3">
            {graphData?.stats?.layers &&
              Object.entries(graphData.stats.layers).map(
                ([layer, count]: [string, unknown]) =>
                  (count as number) > 0 && (
                    <div
                      key={layer}
                      className="flex items-center justify-between"
                    >
                      <span className="text-sm font-medium text-gray-600 capitalize">
                        {layer}
                      </span>
                      <span className="text-sm font-semibold text-gray-900">
                        {count as number}
                      </span>
                    </div>
                  ),
              )}
            {(!graphData?.stats?.layers ||
              Object.values(graphData?.stats?.layers || {}).every(
                (v) => v === 0,
              )) && (
              <p className="text-sm text-gray-500">
                {t("noDependenciesMapped")}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
