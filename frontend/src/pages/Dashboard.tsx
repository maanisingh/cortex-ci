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
      name: "Monitored Entities",
      value: entitiesData?.total || 0,
      icon: BuildingOfficeIcon,
      color: "bg-blue-500",
      href: "/entities",
    },
    {
      name: "Active Constraints",
      value: constraintsSummary?.total || 0,
      icon: DocumentTextIcon,
      color: "bg-purple-500",
      href: "/constraints",
    },
    {
      name: "Dependencies",
      value: graphData?.stats?.total_edges || 0,
      icon: LinkIcon,
      color: "bg-green-500",
      href: "/dependencies",
    },
    {
      name: "Critical Risks",
      value: riskSummary?.critical_count || 0,
      icon: ExclamationTriangleIcon,
      color: "bg-red-500",
      href: "/risks",
    },
  ];

  // Risk distribution chart data
  const riskDistributionData = {
    labels: ["Critical", "High", "Medium", "Low"],
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
        label: "Average Risk Score",
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
          Executive Dashboard
          <InfoTooltip text="Your central command center for monitoring compliance status, risk levels, and key metrics across all monitored entities." />
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Constraint intelligence and risk monitoring overview
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
          Quick Actions
          <InfoTooltip text="Common actions for managing your compliance workflow. Click any button to get started." />
        </h3>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/entities?action=new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Entity
          </Link>
          <Link
            to="/scenarios?action=new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
          >
            <BeakerIcon className="h-4 w-4 mr-2" />
            New Scenario
          </Link>
          <Link
            to="/audit"
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <DocumentMagnifyingGlassIcon className="h-4 w-4 mr-2" />
            View Audit Log
          </Link>
          <Link
            to="/risks"
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Recalculate Risks
          </Link>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 mb-8">
        {/* Risk Distribution */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            Risk Distribution
            <InfoTooltip text="Shows how entities are distributed across risk levels. Critical and high-risk entities require immediate attention." />
          </h3>
          <div className="h-64 flex items-center justify-center">
            {loadingRisk ? (
              <div className="text-gray-500">Loading...</div>
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
              <div className="text-gray-500">No risk data available</div>
            )}
          </div>
        </div>

        {/* Risk Trend */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            Risk Trend (30 days)
            <InfoTooltip text="Track how your overall risk posture has changed over the past month. A downward trend indicates improving compliance." />
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
                No trend data available
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
              Recent Escalations
              <InfoTooltip text="Entities whose risk levels have increased in the past 30 days. These require review to understand what changed." />
            </h3>
            <span className="flex items-center text-red-600">
              <ArrowTrendingUpIcon className="h-5 w-5 mr-1" />
              {riskSummary?.recent_escalations || 0}
            </span>
          </div>
          <p className="text-sm text-gray-500">
            Entities with increased risk level in the last 30 days
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              Recent Improvements
              <InfoTooltip text="Entities whose risk levels have decreased. This indicates successful mitigation efforts or constraint resolution." />
            </h3>
            <span className="flex items-center text-green-600">
              <ArrowTrendingDownIcon className="h-5 w-5 mr-1" />
              {riskSummary?.recent_improvements || 0}
            </span>
          </div>
          <p className="text-sm text-gray-500">
            Entities with decreased risk level in the last 30 days
          </p>
        </div>
      </div>

      {/* Constraint & Dependency Overview */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Constraints by Type */}
        <div className="card" data-tour="constraints">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            Constraints by Type
            <InfoTooltip text="Breakdown of active constraints affecting your entities. Each constraint type represents a different regulatory or compliance category." />
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
                No constraints configured yet
              </p>
            )}
          </div>
          {constraintsSummary?.expiring_soon > 0 && (
            <div className="mt-4 p-3 bg-orange-50 rounded-md">
              <p className="text-sm text-orange-800">
                <strong>{constraintsSummary.expiring_soon}</strong> constraints
                expiring within 30 days
              </p>
            </div>
          )}
        </div>

        {/* Dependencies by Layer */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            Dependencies by Layer
            <InfoTooltip text="Multi-layer dependency mapping shows relationships across legal, financial, operational, and other layers. Critical for understanding cascading risks." />
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
                No dependencies mapped yet
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
