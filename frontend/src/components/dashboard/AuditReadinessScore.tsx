import {
  ShieldCheckIcon,
  DocumentCheckIcon,
  UserGroupIcon,
  ServerStackIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";

interface AuditCategory {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  score: number;
  items: {
    completed: number;
    total: number;
  };
}

interface AuditReadinessScoreProps {
  overallScore: number;
  categories?: AuditCategory[];
  lastAuditDate?: string;
  nextAuditDate?: string;
}

const defaultCategories: AuditCategory[] = [
  {
    id: "documents",
    name: "Документация",
    icon: DocumentCheckIcon,
    score: 85,
    items: { completed: 17, total: 20 },
  },
  {
    id: "technical",
    name: "Технические меры",
    icon: ServerStackIcon,
    score: 72,
    items: { completed: 18, total: 25 },
  },
  {
    id: "organizational",
    name: "Организационные меры",
    icon: UserGroupIcon,
    score: 90,
    items: { completed: 9, total: 10 },
  },
  {
    id: "training",
    name: "Обучение персонала",
    icon: ShieldCheckIcon,
    score: 65,
    items: { completed: 13, total: 20 },
  },
];

export default function AuditReadinessScore({
  overallScore,
  categories = defaultCategories,
  lastAuditDate,
  nextAuditDate,
}: AuditReadinessScoreProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return { text: "text-green-600", bg: "bg-green-500" };
    if (score >= 60) return { text: "text-yellow-600", bg: "bg-yellow-500" };
    if (score >= 40) return { text: "text-orange-600", bg: "bg-orange-500" };
    return { text: "text-red-600", bg: "bg-red-500" };
  };

  const scoreColors = getScoreColor(overallScore);
  const circumference = 2 * Math.PI * 52;
  const strokeDashoffset = circumference - (overallScore / 100) * circumference;

  const getReadinessLabel = (score: number) => {
    if (score >= 90) return "Полностью готов";
    if (score >= 80) return "Высокая готовность";
    if (score >= 60) return "Частичная готовность";
    if (score >= 40) return "Требует доработки";
    return "Не готов";
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Готовность к аудиту
        </h3>
        <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Main Score Circle */}
        <div className="relative flex-shrink-0">
          <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke="currentColor"
              strokeWidth="10"
              className="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke="currentColor"
              strokeWidth="10"
              strokeLinecap="round"
              className={scoreColors.text}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset,
                transition: "stroke-dashoffset 0.5s ease-in-out",
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${scoreColors.text}`}>{overallScore}%</span>
            <span className="text-xs text-gray-500 dark:text-gray-400 text-center mt-1">
              {getReadinessLabel(overallScore)}
            </span>
          </div>
        </div>

        {/* Categories */}
        <div className="flex-1 space-y-3 w-full">
          {categories.map((category) => {
            const Icon = category.icon;
            const catColors = getScoreColor(category.score);
            return (
              <div key={category.id} className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  <Icon className={`h-5 w-5 ${catColors.text}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                      {category.name}
                    </span>
                    <span className={`text-sm font-medium ${catColors.text}`}>
                      {category.score}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${catColors.bg} transition-all duration-500`}
                      style={{ width: `${category.score}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {category.items.completed}/{category.items.total} пунктов
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Audit Dates */}
      {(lastAuditDate || nextAuditDate) && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-4 text-sm">
            {lastAuditDate && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Последний аудит:</span>
                <p className="font-medium text-gray-900 dark:text-white">
                  {new Date(lastAuditDate).toLocaleDateString("ru-RU")}
                </p>
              </div>
            )}
            {nextAuditDate && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Следующий аудит:</span>
                <p className="font-medium text-blue-600 dark:text-blue-400">
                  {new Date(nextAuditDate).toLocaleDateString("ru-RU")}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Checklist Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <CheckCircleIcon className="h-4 w-4 text-green-500" />
            <span className="text-gray-600 dark:text-gray-400">Выполнено требований</span>
          </div>
          <span className="font-medium text-gray-900 dark:text-white">
            {categories.reduce((sum, cat) => sum + cat.items.completed, 0)} из{" "}
            {categories.reduce((sum, cat) => sum + cat.items.total, 0)}
          </span>
        </div>
      </div>
    </div>
  );
}
