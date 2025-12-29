import { useMemo } from "react";

interface RiskItem {
  id: string;
  name: string;
  likelihood: 1 | 2 | 3 | 4 | 5; // 1 = Very Low, 5 = Very High
  impact: 1 | 2 | 3 | 4 | 5; // 1 = Very Low, 5 = Very High
  category: string;
}

interface RiskHeatMapProps {
  risks: RiskItem[];
  showLegend?: boolean;
}

const likelihoodLabels = ["Очень низкая", "Низкая", "Средняя", "Высокая", "Очень высокая"];
const impactLabels = ["Очень низкое", "Низкое", "Среднее", "Высокое", "Очень высокое"];

function getCellColor(likelihood: number, impact: number): string {
  const score = likelihood * impact;
  if (score <= 4) return "bg-green-100 dark:bg-green-900/30 hover:bg-green-200";
  if (score <= 9) return "bg-yellow-100 dark:bg-yellow-900/30 hover:bg-yellow-200";
  if (score <= 16) return "bg-orange-100 dark:bg-orange-900/30 hover:bg-orange-200";
  return "bg-red-100 dark:bg-red-900/30 hover:bg-red-200";
}

function getRiskLevel(likelihood: number, impact: number): string {
  const score = likelihood * impact;
  if (score <= 4) return "Низкий";
  if (score <= 9) return "Средний";
  if (score <= 16) return "Высокий";
  return "Критический";
}

export default function RiskHeatMap({ risks, showLegend = true }: RiskHeatMapProps) {
  // Group risks by cell position
  const risksByCell = useMemo(() => {
    const grouped: Record<string, RiskItem[]> = {};
    risks.forEach((risk) => {
      const key = `${risk.likelihood}-${risk.impact}`;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(risk);
    });
    return grouped;
  }, [risks]);

  // Calculate risk distribution
  const riskDistribution = useMemo(() => {
    let low = 0,
      medium = 0,
      high = 0,
      critical = 0;
    risks.forEach((risk) => {
      const score = risk.likelihood * risk.impact;
      if (score <= 4) low++;
      else if (score <= 9) medium++;
      else if (score <= 16) high++;
      else critical++;
    });
    return { low, medium, high, critical, total: risks.length };
  }, [risks]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Карта рисков</h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">{risks.length} рисков</span>
      </div>

      {/* Heat Map Grid */}
      <div className="flex gap-2">
        {/* Y-axis label */}
        <div className="flex flex-col justify-center items-center -rotate-180 text-xs text-gray-500 dark:text-gray-400 writing-mode-vertical">
          <span style={{ writingMode: "vertical-rl" }}>Воздействие →</span>
        </div>

        <div className="flex-1">
          {/* Grid */}
          <div className="grid grid-cols-5 gap-1">
            {[5, 4, 3, 2, 1].map((impact) =>
              [1, 2, 3, 4, 5].map((likelihood) => {
                const cellRisks = risksByCell[`${likelihood}-${impact}`] || [];
                const cellColor = getCellColor(likelihood, impact);

                return (
                  <div
                    key={`${likelihood}-${impact}`}
                    className={`
                      aspect-square rounded-lg ${cellColor}
                      flex items-center justify-center
                      transition-colors cursor-pointer
                      relative group
                    `}
                    title={`Вероятность: ${likelihoodLabels[likelihood - 1]}, Воздействие: ${impactLabels[impact - 1]}`}
                  >
                    {cellRisks.length > 0 && (
                      <span className="text-sm font-bold text-gray-700 dark:text-gray-300">
                        {cellRisks.length}
                      </span>
                    )}
                    {/* Tooltip */}
                    {cellRisks.length > 0 && (
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                        <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg p-2 whitespace-nowrap shadow-lg">
                          <p className="font-medium mb-1">
                            {getRiskLevel(likelihood, impact)} риск ({cellRisks.length})
                          </p>
                          {cellRisks.slice(0, 3).map((r) => (
                            <p key={r.id} className="text-gray-300">
                              • {r.name}
                            </p>
                          ))}
                          {cellRisks.length > 3 && (
                            <p className="text-gray-400">и ещё {cellRisks.length - 3}...</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* X-axis label */}
          <div className="text-center mt-2 text-xs text-gray-500 dark:text-gray-400">
            Вероятность →
          </div>
        </div>
      </div>

      {/* Legend and Distribution */}
      {showLegend && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-4 gap-2">
            <div className="flex items-center gap-2 p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <div className="text-xs">
                <p className="font-medium text-gray-700 dark:text-gray-300">Низкий</p>
                <p className="text-gray-500">{riskDistribution.low}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="text-xs">
                <p className="font-medium text-gray-700 dark:text-gray-300">Средний</p>
                <p className="text-gray-500">{riskDistribution.medium}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-orange-50 dark:bg-orange-900/20">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <div className="text-xs">
                <p className="font-medium text-gray-700 dark:text-gray-300">Высокий</p>
                <p className="text-gray-500">{riskDistribution.high}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 p-2 rounded-lg bg-red-50 dark:bg-red-900/20">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="text-xs">
                <p className="font-medium text-gray-700 dark:text-gray-300">Критический</p>
                <p className="text-gray-500">{riskDistribution.critical}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
