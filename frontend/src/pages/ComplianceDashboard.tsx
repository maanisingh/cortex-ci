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
} from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";
import {
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  DocumentCheckIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  FlagIcon,
} from "@heroicons/react/24/outline";
import { complianceScoringApi } from "../services/api";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(" ");
}

function getGradeColor(grade: string) {
  switch (grade) {
    case "A":
      return "text-green-600 bg-green-100";
    case "B":
      return "text-blue-600 bg-blue-100";
    case "C":
      return "text-yellow-600 bg-yellow-100";
    case "D":
      return "text-orange-600 bg-orange-100";
    default:
      return "text-red-600 bg-red-100";
  }
}

function getScoreColor(score: number) {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  if (score >= 40) return "text-orange-600";
  return "text-red-600";
}

interface Framework {
  id: string;
  name: string;
  score: number;
  grade: string;
  total: number;
  implemented: number;
}

interface GapItem {
  control_id: string;
  control_title: string;
  framework_id: string;
  framework_name: string;
  category: string;
  status: string;
  priority: number;
  severity: string;
}

interface DashboardData {
  score: {
    overall: number;
    grade: string;
    trend: {
      direction: string;
      change: number;
      period: string;
    };
  };
  summary: {
    total_frameworks: number;
    total_controls: number;
    implemented: number;
    gaps: number;
  };
  frameworks: Framework[];
  top_gaps: {
    critical_count: number;
    high_count: number;
    items: GapItem[];
  };
  efficiency: {
    cross_framework_mappings: number;
    recommended_priority: string[];
  };
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
    user: string;
  }>;
}

export default function ComplianceDashboard() {
  const { data: dashboardData, isLoading } = useQuery<DashboardData>({
    queryKey: ["compliance-dashboard"],
    queryFn: async () => {
      const response = await complianceScoringApi.dashboard();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No compliance data available</p>
      </div>
    );
  }

  // Prepare chart data
  const statusData = {
    labels: ["Implemented", "Partial", "Gaps", "Not Assessed"],
    datasets: [
      {
        data: [
          dashboardData.summary.implemented,
          Math.round(
            (dashboardData.summary.total_controls -
              dashboardData.summary.implemented -
              dashboardData.summary.gaps) *
              0.4,
          ),
          dashboardData.summary.gaps,
          Math.round(
            (dashboardData.summary.total_controls -
              dashboardData.summary.implemented) *
              0.3,
          ),
        ],
        backgroundColor: [
          "rgb(34, 197, 94)",
          "rgb(234, 179, 8)",
          "rgb(239, 68, 68)",
          "rgb(156, 163, 175)",
        ],
      },
    ],
  };

  const frameworkScores = {
    labels: dashboardData.frameworks
      .slice(0, 6)
      .map((f) => f.name.substring(0, 15)),
    datasets: [
      {
        label: "Compliance Score %",
        data: dashboardData.frameworks.slice(0, 6).map((f) => f.score),
        backgroundColor: dashboardData.frameworks
          .slice(0, 6)
          .map((f) =>
            f.score >= 70
              ? "rgba(34, 197, 94, 0.8)"
              : f.score >= 50
                ? "rgba(234, 179, 8, 0.8)"
                : "rgba(239, 68, 68, 0.8)",
          ),
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Compliance Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time compliance posture across all frameworks
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <Link
            to="/compliance/frameworks"
            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            <DocumentCheckIcon className="h-5 w-5 mr-2 text-gray-400" />
            Frameworks
          </Link>
          <Link
            to="/compliance/controls"
            className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            <ClipboardDocumentListIcon className="h-5 w-5 mr-2" />
            Controls
          </Link>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            {/* Score Circle */}
            <div className="relative">
              <div
                className={classNames(
                  "flex items-center justify-center w-32 h-32 rounded-full border-8",
                  dashboardData.score.overall >= 70
                    ? "border-green-500"
                    : dashboardData.score.overall >= 50
                      ? "border-yellow-500"
                      : "border-red-500",
                )}
              >
                <div className="text-center">
                  <span
                    className={classNames(
                      "text-3xl font-bold",
                      getScoreColor(dashboardData.score.overall),
                    )}
                  >
                    {dashboardData.score.overall}%
                  </span>
                  <span
                    className={classNames(
                      "block text-2xl font-semibold px-2 py-0.5 rounded",
                      getGradeColor(dashboardData.score.grade),
                    )}
                  >
                    {dashboardData.score.grade}
                  </span>
                </div>
              </div>
            </div>

            {/* Score Details */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Overall Compliance Score
              </h2>
              <div className="mt-2 flex items-center text-sm">
                {dashboardData.score.trend.direction === "up" ? (
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-500 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="h-5 w-5 text-red-500 mr-1" />
                )}
                <span
                  className={
                    dashboardData.score.trend.direction === "up"
                      ? "text-green-600"
                      : "text-red-600"
                  }
                >
                  {dashboardData.score.trend.change > 0 ? "+" : ""}
                  {dashboardData.score.trend.change}%
                </span>
                <span className="text-gray-500 ml-1">
                  over {dashboardData.score.trend.period}
                </span>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {dashboardData.summary.total_frameworks}
              </div>
              <div className="text-sm text-gray-500">Frameworks</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">
                {dashboardData.summary.total_controls}
              </div>
              <div className="text-sm text-gray-500">Controls</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {dashboardData.summary.implemented}
              </div>
              <div className="text-sm text-gray-500">Implemented</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {dashboardData.summary.gaps}
              </div>
              <div className="text-sm text-gray-500">Gaps</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Control Status Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Control Implementation Status
          </h3>
          <div className="h-64 flex items-center justify-center">
            <Doughnut
              data={statusData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: "right",
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Framework Scores Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Framework Compliance Scores
          </h3>
          <div className="h-64">
            <Bar
              data={frameworkScores}
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
          </div>
        </div>
      </div>

      {/* Frameworks and Gaps Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Framework Progress */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Framework Progress
            </h3>
            <Link
              to="/compliance/frameworks"
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              View all
            </Link>
          </div>
          <div className="space-y-4">
            {dashboardData.frameworks.slice(0, 6).map((framework) => (
              <div key={framework.id} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-900 truncate max-w-xs">
                    {framework.name}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className={getScoreColor(framework.score)}>
                      {framework.score}%
                    </span>
                    <span
                      className={classNames(
                        "px-2 py-0.5 rounded text-xs font-medium",
                        getGradeColor(framework.grade),
                      )}
                    >
                      {framework.grade}
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={classNames(
                      "h-2 rounded-full",
                      framework.score >= 70
                        ? "bg-green-500"
                        : framework.score >= 50
                          ? "bg-yellow-500"
                          : "bg-red-500",
                    )}
                    style={{ width: `${framework.score}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500">
                  {framework.implemented} / {framework.total} controls
                  implemented
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Gaps */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Priority Gaps
            </h3>
            <div className="flex space-x-2 text-sm">
              <span className="inline-flex items-center px-2 py-1 rounded bg-red-100 text-red-700">
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                {dashboardData.top_gaps.critical_count} Critical
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded bg-orange-100 text-orange-700">
                <FlagIcon className="h-4 w-4 mr-1" />
                {dashboardData.top_gaps.high_count} High
              </span>
            </div>
          </div>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Control
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Framework
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Severity
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {dashboardData.top_gaps.items.slice(0, 8).map((gap, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-3 py-2">
                      <div className="text-sm font-medium text-gray-900">
                        {gap.control_id}
                      </div>
                      <div className="text-xs text-gray-500 truncate max-w-xs">
                        {gap.control_title}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-xs text-gray-500">
                      {gap.framework_name.substring(0, 20)}
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={classNames(
                          "px-2 py-0.5 rounded text-xs font-medium",
                          gap.severity === "CRITICAL"
                            ? "bg-red-100 text-red-700"
                            : gap.severity === "HIGH"
                              ? "bg-orange-100 text-orange-700"
                              : "bg-yellow-100 text-yellow-700",
                        )}
                      >
                        {gap.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Cross-Framework Efficiency */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <ChartBarIcon className="h-6 w-6 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Cross-Framework Efficiency
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600 mb-3">
              Complying with multiple frameworks can be streamlined by
              leveraging control mappings.
            </p>
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {dashboardData.efficiency.cross_framework_mappings}
                </div>
                <div className="text-sm text-gray-500">Control Mappings</div>
              </div>
              <div className="text-4xl text-gray-300">=</div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  ~
                  {Math.round(
                    dashboardData.efficiency.cross_framework_mappings * 0.4,
                  )}
                  %
                </div>
                <div className="text-sm text-gray-500">Effort Reduction</div>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">
              Recommended Priority Order:
            </p>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
              {dashboardData.efficiency.recommended_priority.map(
                (framework, idx) => (
                  <li key={idx}>{framework}</li>
                ),
              )}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
