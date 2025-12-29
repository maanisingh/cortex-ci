import {
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PencilSquareIcon,
} from "@heroicons/react/24/outline";

interface DocumentStats {
  total: number;
  approved: number;
  draft: number;
  pendingReview: number;
  expired: number;
}

interface DocumentStatusTrackerProps {
  stats: DocumentStats;
  recentDocuments?: {
    id: string;
    title: string;
    status: "approved" | "draft" | "pending_review" | "expired";
    updatedAt: string;
  }[];
}

export default function DocumentStatusTracker({
  stats,
  recentDocuments = [],
}: DocumentStatusTrackerProps) {
  const statusConfig = {
    approved: {
      label: "Утверждено",
      color: "text-green-600",
      bgColor: "bg-green-100 dark:bg-green-900/20",
      icon: CheckCircleIcon,
    },
    draft: {
      label: "Черновик",
      color: "text-gray-600",
      bgColor: "bg-gray-100 dark:bg-gray-700",
      icon: PencilSquareIcon,
    },
    pending_review: {
      label: "На проверке",
      color: "text-blue-600",
      bgColor: "bg-blue-100 dark:bg-blue-900/20",
      icon: ClockIcon,
    },
    expired: {
      label: "Истёк срок",
      color: "text-red-600",
      bgColor: "bg-red-100 dark:bg-red-900/20",
      icon: ExclamationTriangleIcon,
    },
  };

  const approvedPercentage = stats.total > 0 ? Math.round((stats.approved / stats.total) * 100) : 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Статус документов
        </h3>
        <div className="flex items-center gap-2">
          <DocumentTextIcon className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-500 dark:text-gray-400">{stats.total} документов</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`p-4 rounded-lg ${statusConfig.approved.bgColor}`}>
          <div className="flex items-center gap-2">
            <CheckCircleIcon className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Утверждено</span>
          </div>
          <p className="text-2xl font-bold text-green-600 mt-1">{stats.approved}</p>
        </div>

        <div className={`p-4 rounded-lg ${statusConfig.draft.bgColor}`}>
          <div className="flex items-center gap-2">
            <PencilSquareIcon className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Черновики</span>
          </div>
          <p className="text-2xl font-bold text-gray-600 mt-1">{stats.draft}</p>
        </div>

        <div className={`p-4 rounded-lg ${statusConfig.pending_review.bgColor}`}>
          <div className="flex items-center gap-2">
            <ClockIcon className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">На проверке</span>
          </div>
          <p className="text-2xl font-bold text-blue-600 mt-1">{stats.pendingReview}</p>
        </div>

        <div className={`p-4 rounded-lg ${statusConfig.expired.bgColor}`}>
          <div className="flex items-center gap-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Истёк срок</span>
          </div>
          <p className="text-2xl font-bold text-red-600 mt-1">{stats.expired}</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600 dark:text-gray-400">Готовность документации</span>
          <span className="font-bold text-gray-900 dark:text-white">{approvedPercentage}%</span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 transition-all duration-500"
            style={{ width: `${approvedPercentage}%` }}
          />
        </div>
      </div>

      {/* Recent Documents */}
      {recentDocuments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Последние обновления
          </h4>
          <div className="space-y-2">
            {recentDocuments.slice(0, 3).map((doc) => {
              const config = statusConfig[doc.status];
              const Icon = config.icon;
              return (
                <div
                  key={doc.id}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Icon className={`h-4 w-4 flex-shrink-0 ${config.color}`} />
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                      {doc.title}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0 ml-2">
                    {new Date(doc.updatedAt).toLocaleDateString("ru-RU")}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
