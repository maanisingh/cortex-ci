import { useMemo } from "react";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";

interface ComplianceScoreCardProps {
  title: string;
  score: number;
  total: number;
  completed: number;
  inProgress: number;
  pending: number;
  overdue: number;
  showBreakdown?: boolean;
}

export default function ComplianceScoreCard({
  title,
  score,
  total,
  completed,
  inProgress,
  pending,
  overdue,
  showBreakdown = true,
}: ComplianceScoreCardProps) {
  const scoreColor = useMemo(() => {
    if (score >= 80) return { text: "text-green-600", bg: "bg-green-500", ring: "ring-green-500" };
    if (score >= 60) return { text: "text-yellow-600", bg: "bg-yellow-500", ring: "ring-yellow-500" };
    if (score >= 40) return { text: "text-orange-600", bg: "bg-orange-500", ring: "ring-orange-500" };
    return { text: "text-red-600", bg: "bg-red-500", ring: "ring-red-500" };
  }, [score]);

  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">{title}</h3>

      <div className="flex items-center justify-between">
        {/* Circular Progress */}
        <div className="relative">
          <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeLinecap="round"
              className={scoreColor.text}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset,
                transition: "stroke-dashoffset 0.5s ease-in-out",
              }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-2xl font-bold ${scoreColor.text}`}>{score}%</span>
          </div>
        </div>

        {/* Breakdown */}
        {showBreakdown && (
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-4 w-4 text-green-500" />
              <span className="text-gray-600 dark:text-gray-400">
                {completed} / {total}
              </span>
              <span className="text-xs text-gray-400">Выполнено</span>
            </div>
            <div className="flex items-center gap-2">
              <ClockIcon className="h-4 w-4 text-blue-500" />
              <span className="text-gray-600 dark:text-gray-400">{inProgress}</span>
              <span className="text-xs text-gray-400">В работе</span>
            </div>
            <div className="flex items-center gap-2">
              <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />
              <span className="text-gray-600 dark:text-gray-400">{pending}</span>
              <span className="text-xs text-gray-400">Ожидает</span>
            </div>
            {overdue > 0 && (
              <div className="flex items-center gap-2">
                <XCircleIcon className="h-4 w-4 text-red-500" />
                <span className="text-red-600 dark:text-red-400 font-medium">{overdue}</span>
                <span className="text-xs text-red-500">Просрочено</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
