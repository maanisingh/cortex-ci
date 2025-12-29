import { Link } from "react-router-dom";
import {
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
  CalendarDaysIcon,
} from "@heroicons/react/24/outline";

interface TaskStats {
  total: number;
  completed: number;
  inProgress: number;
  pending: number;
  overdue: number;
}

interface UpcomingTask {
  id: string;
  title: string;
  dueDate: string;
  priority: "low" | "medium" | "high" | "critical";
  status: "pending" | "in_progress" | "completed" | "overdue";
}

interface TaskSummaryWidgetProps {
  stats: TaskStats;
  upcomingTasks?: UpcomingTask[];
  showUpcoming?: boolean;
}

export default function TaskSummaryWidget({
  stats,
  upcomingTasks = [],
  showUpcoming = true,
}: TaskSummaryWidgetProps) {
  const priorityColors = {
    low: "text-gray-500",
    medium: "text-yellow-600",
    high: "text-orange-600",
    critical: "text-red-600",
  };

  const getDaysUntilDue = (date: string) => {
    const due = new Date(date);
    const now = new Date();
    const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getDueLabel = (date: string) => {
    const days = getDaysUntilDue(date);
    if (days < 0) return { text: `${Math.abs(days)} дн. назад`, color: "text-red-600" };
    if (days === 0) return { text: "Сегодня", color: "text-orange-600" };
    if (days === 1) return { text: "Завтра", color: "text-yellow-600" };
    if (days <= 7) return { text: `Через ${days} дн.`, color: "text-blue-600" };
    return { text: new Date(date).toLocaleDateString("ru-RU"), color: "text-gray-500" };
  };

  const completionRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Сводка по задачам</h3>
        <Link
          to="/compliance-tasks"
          className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
        >
          Все задачи
          <ArrowRightIcon className="h-4 w-4" />
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Всего</p>
        </div>
        <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Выполнено</p>
        </div>
        <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-2xl font-bold text-blue-600">{stats.inProgress}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">В работе</p>
        </div>
        <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Просрочено</p>
        </div>
      </div>

      {/* Completion Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600 dark:text-gray-400">Прогресс выполнения</span>
          <span className="font-bold text-gray-900 dark:text-white">{completionRate}%</span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
            style={{ width: `${completionRate}%` }}
          />
        </div>
      </div>

      {/* Upcoming Tasks */}
      {showUpcoming && upcomingTasks.length > 0 && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <CalendarDaysIcon className="h-5 w-5 text-blue-600" />
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Ближайшие сроки
            </h4>
          </div>
          <div className="space-y-2">
            {upcomingTasks.slice(0, 4).map((task) => {
              const dueLabel = getDueLabel(task.dueDate);
              return (
                <div
                  key={task.id}
                  className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {task.status === "overdue" ? (
                      <ExclamationCircleIcon className="h-4 w-4 text-red-500 flex-shrink-0" />
                    ) : task.status === "completed" ? (
                      <CheckCircleIcon className="h-4 w-4 text-green-500 flex-shrink-0" />
                    ) : (
                      <ClockIcon className="h-4 w-4 text-blue-500 flex-shrink-0" />
                    )}
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                      {task.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`text-xs ${priorityColors[task.priority]}`}>
                      {task.priority === "critical" && "!!! "}
                      {task.priority === "high" && "!! "}
                      {task.priority === "medium" && "! "}
                    </span>
                    <span className={`text-xs font-medium ${dueLabel.color}`}>{dueLabel.text}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
