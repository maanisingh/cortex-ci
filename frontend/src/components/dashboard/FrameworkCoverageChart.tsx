interface Framework {
  id: string;
  name: string;
  shortName: string;
  score: number;
  totalControls: number;
  implementedControls: number;
}

interface FrameworkCoverageChartProps {
  frameworks: Framework[];
}

export default function FrameworkCoverageChart({ frameworks }: FrameworkCoverageChartProps) {
  const getBarColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  const getBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100 dark:bg-green-900/20";
    if (score >= 60) return "bg-yellow-100 dark:bg-yellow-900/20";
    if (score >= 40) return "bg-orange-100 dark:bg-orange-900/20";
    return "bg-red-100 dark:bg-red-900/20";
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Покрытие по нормативным рамкам
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {frameworks.length} фреймворков
        </span>
      </div>

      <div className="space-y-4">
        {frameworks.map((framework) => (
          <div key={framework.id} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {framework.shortName}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {framework.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {framework.implementedControls}/{framework.totalControls}
                </span>
                <span
                  className={`text-sm font-bold ${
                    framework.score >= 80
                      ? "text-green-600"
                      : framework.score >= 60
                      ? "text-yellow-600"
                      : framework.score >= 40
                      ? "text-orange-600"
                      : "text-red-600"
                  }`}
                >
                  {framework.score}%
                </span>
              </div>
            </div>
            <div className={`h-3 rounded-full ${getBgColor(framework.score)}`}>
              <div
                className={`h-full rounded-full transition-all duration-500 ${getBarColor(
                  framework.score
                )}`}
                style={{ width: `${framework.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-600 dark:text-gray-400">80%+ Отлично</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-600 dark:text-gray-400">60-79% Хорошо</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-gray-600 dark:text-gray-400">40-59% Требует внимания</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-600 dark:text-gray-400">&lt;40% Критично</span>
          </div>
        </div>
      </div>
    </div>
  );
}
