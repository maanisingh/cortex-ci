import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useDueDateReminders } from "../hooks/useDueDateReminders";
import { TaskForReminder } from "../stores/notificationStore";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  FunnelIcon,
  ListBulletIcon,
  Squares2X2Icon,
} from "@heroicons/react/24/outline";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  isToday,
  addMonths,
  subMonths,
  parseISO,
  differenceInDays,
} from "date-fns";
import { ru } from "date-fns/locale";
import { russianComplianceApi } from "../services/api";

interface ApiTask {
  id: string;
  title: string;
  description: string | null;
  task_type: string;
  framework: string;
  status: string;
  priority: string;
  due_date: string | null;
  assigned_to: string | null;
  assigned_department: string | null;
  assigned_role: string | null;
  is_recurring: boolean;
  recurrence_days: number | null;
  completed_at: string | null;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "completed" | "overdue";
  priority: "low" | "medium" | "high" | "critical";
  dueDate: Date;
  framework: string;
  assignee: string;
  isRecurring: boolean;
  recurrenceDays?: number;
}

const statusMapping: Record<string, Task["status"]> = {
  NOT_STARTED: "pending",
  IN_PROGRESS: "in_progress",
  PENDING_REVIEW: "in_progress",
  COMPLETED: "completed",
  OVERDUE: "overdue",
  BLOCKED: "pending",
};

const priorityMapping: Record<string, Task["priority"]> = {
  CRITICAL: "critical",
  HIGH: "high",
  MEDIUM: "medium",
  LOW: "low",
};

const priorityColors = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-gray-400",
};

const statusColors = {
  pending: "border-l-gray-400",
  in_progress: "border-l-blue-500",
  completed: "border-l-green-500",
  overdue: "border-l-red-500",
};

const statusLabels = {
  pending: "Ожидает",
  in_progress: "В работе",
  completed: "Выполнено",
  overdue: "Просрочено",
};

export default function ComplianceCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [viewMode, setViewMode] = useState<"calendar" | "timeline">("calendar");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [showFilters, setShowFilters] = useState(false);

  // Fetch companies
  const { data: companies = [] } = useQuery({
    queryKey: ["russian-companies"],
    queryFn: async () => {
      const response = await russianComplianceApi.companies.list();
      return response.data;
    },
  });

  // Set first company as default
  useEffect(() => {
    if (companies.length > 0 && !selectedCompanyId) {
      setSelectedCompanyId(companies[0].id);
    }
  }, [companies, selectedCompanyId]);

  // Fetch tasks
  const { data: apiTasks = [], isLoading, refetch } = useQuery({
    queryKey: ["compliance-tasks-calendar", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return [];
      const response = await russianComplianceApi.tasks.list(selectedCompanyId);
      return response.data;
    },
    enabled: !!selectedCompanyId,
  });

  // Map API tasks to frontend format
  const tasks: Task[] = useMemo(() => {
    return apiTasks
      .filter((t: ApiTask) => t.due_date)
      .map((t: ApiTask) => {
        const dueDate = parseISO(t.due_date!);
        let status = statusMapping[t.status] || "pending";

        // Check if overdue
        if (status !== "completed" && differenceInDays(dueDate, new Date()) < 0) {
          status = "overdue";
        }

        return {
          id: t.id,
          title: t.title,
          description: t.description || "",
          status,
          priority: priorityMapping[t.priority] || "medium",
          dueDate,
          framework: t.framework || "152-ФЗ",
          assignee: t.assigned_department || "Не назначено",
          isRecurring: t.is_recurring,
          recurrenceDays: t.recurrence_days || undefined,
        };
      });
  }, [apiTasks]);

  // Convert tasks to reminder format for due date notifications
  const tasksForReminders = useMemo<TaskForReminder[]>(() => {
    return tasks.map((task) => ({
      id: task.id,
      title: task.title,
      dueDate: task.dueDate,
      status: task.status,
      priority: task.priority,
      url: `/compliance-calendar`,
    }));
  }, [tasks]);

  // Check for due date reminders
  useDueDateReminders(tasksForReminders, { enabled: tasks.length > 0 });

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (filterStatus !== "all" && task.status !== filterStatus) return false;
      if (filterPriority !== "all" && task.priority !== filterPriority) return false;
      return true;
    });
  }, [tasks, filterStatus, filterPriority]);

  // Calendar days calculation
  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(currentDate);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
    return eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  }, [currentDate]);

  // Tasks grouped by date for calendar
  const tasksByDate = useMemo(() => {
    const grouped: Record<string, Task[]> = {};
    filteredTasks.forEach((task) => {
      const key = format(task.dueDate, "yyyy-MM-dd");
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(task);
    });
    return grouped;
  }, [filteredTasks]);

  // Tasks for selected date
  const selectedDateTasks = useMemo(() => {
    if (!selectedDate) return [];
    const key = format(selectedDate, "yyyy-MM-dd");
    return tasksByDate[key] || [];
  }, [selectedDate, tasksByDate]);

  // Upcoming tasks (next 30 days)
  const upcomingTasks = useMemo(() => {
    const now = new Date();
    return filteredTasks
      .filter((t) => t.status !== "completed" && differenceInDays(t.dueDate, now) >= 0)
      .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
      .slice(0, 10);
  }, [filteredTasks]);

  // Overdue tasks
  const overdueTasks = useMemo(() => {
    return filteredTasks
      .filter((t) => t.status === "overdue")
      .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());
  }, [filteredTasks]);

  // Stats
  const stats = useMemo(() => {
    const now = new Date();
    const thisMonth = tasks.filter(
      (t) => isSameMonth(t.dueDate, currentDate)
    );
    return {
      thisMonth: thisMonth.length,
      completed: thisMonth.filter((t) => t.status === "completed").length,
      pending: thisMonth.filter((t) => t.status === "pending" || t.status === "in_progress").length,
      overdue: tasks.filter((t) => t.status === "overdue").length,
      upcoming7Days: tasks.filter(
        (t) => t.status !== "completed" && differenceInDays(t.dueDate, now) >= 0 && differenceInDays(t.dueDate, now) <= 7
      ).length,
    };
  }, [tasks, currentDate]);

  const navigateMonth = (direction: "prev" | "next") => {
    setCurrentDate(direction === "prev" ? subMonths(currentDate, 1) : addMonths(currentDate, 1));
    setSelectedDate(null);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  if (!selectedCompanyId && companies.length === 0) {
    return (
      <div className="text-center py-12">
        <CalendarIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h2 className="mt-2 text-lg font-medium text-gray-900 dark:text-white">
          Нет зарегистрированных компаний
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Сначала добавьте компанию в разделе{" "}
          <Link to="/russian-compliance" className="text-blue-600 hover:underline">
            Российское соответствие
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Календарь соответствия
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Планирование и отслеживание сроков выполнения задач
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden">
            <button
              onClick={() => setViewMode("calendar")}
              className={`px-3 py-2 text-sm ${
                viewMode === "calendar"
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600"
              }`}
            >
              <Squares2X2Icon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode("timeline")}
              className={`px-3 py-2 text-sm ${
                viewMode === "timeline"
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600"
              }`}
            >
              <ListBulletIcon className="h-5 w-5" />
            </button>
          </div>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            <ArrowPathIcon className={`h-5 w-5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center px-3 py-2 border rounded-lg text-sm font-medium ${
              showFilters
                ? "border-blue-500 text-blue-700 bg-blue-50 dark:bg-blue-900 dark:text-blue-200"
                : "border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
            }`}
          >
            <FunnelIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Company selector */}
      {companies.length > 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Компания
          </label>
          <select
            value={selectedCompanyId}
            onChange={(e) => setSelectedCompanyId(e.target.value)}
            className="w-full sm:w-auto border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
          >
            {companies.map((company: { id: string; legal_name: string }) => (
              <option key={company.id} value={company.id}>
                {company.legal_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Статус
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-sm dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Все</option>
                <option value="pending">Ожидает</option>
                <option value="in_progress">В работе</option>
                <option value="completed">Выполнено</option>
                <option value="overdue">Просрочено</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Приоритет
              </label>
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 text-sm dark:bg-gray-700 dark:text-white"
              >
                <option value="all">Все</option>
                <option value="critical">Критический</option>
                <option value="high">Высокий</option>
                <option value="medium">Средний</option>
                <option value="low">Низкий</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center">
            <CalendarIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.thisMonth}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">В этом месяце</div>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Выполнено</div>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">В ожидании</div>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-8 w-8 text-red-500" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Просрочено</div>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-3">
              <div className="text-2xl font-bold text-orange-600">{stats.upcoming7Days}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Следующие 7 дней</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar / Timeline View */}
        <div className="lg:col-span-2">
          {viewMode === "calendar" ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              {/* Calendar Header */}
              <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
                <button
                  onClick={() => navigateMonth("prev")}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronLeftIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </button>
                <div className="flex items-center space-x-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                    {format(currentDate, "LLLL yyyy", { locale: ru })}
                  </h2>
                  <button
                    onClick={goToToday}
                    className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 rounded-lg"
                  >
                    Сегодня
                  </button>
                </div>
                <button
                  onClick={() => navigateMonth("next")}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ChevronRightIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </button>
              </div>

              {/* Weekday Headers */}
              <div className="grid grid-cols-7 border-b dark:border-gray-700">
                {["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map((day) => (
                  <div
                    key={day}
                    className="py-2 text-center text-sm font-medium text-gray-500 dark:text-gray-400"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7">
                {calendarDays.map((day, idx) => {
                  const dateKey = format(day, "yyyy-MM-dd");
                  const dayTasks = tasksByDate[dateKey] || [];
                  const isCurrentMonth = isSameMonth(day, currentDate);
                  const isSelected = selectedDate && isSameDay(day, selectedDate);
                  const hasOverdue = dayTasks.some((t) => t.status === "overdue");
                  const hasCritical = dayTasks.some((t) => t.priority === "critical");

                  return (
                    <div
                      key={idx}
                      onClick={() => setSelectedDate(day)}
                      className={`min-h-[100px] p-2 border-b border-r dark:border-gray-700 cursor-pointer transition-colors ${
                        isCurrentMonth
                          ? "bg-white dark:bg-gray-800"
                          : "bg-gray-50 dark:bg-gray-900"
                      } ${isSelected ? "ring-2 ring-blue-500 ring-inset" : ""} ${
                        isToday(day) ? "bg-blue-50 dark:bg-blue-900/20" : ""
                      } hover:bg-gray-50 dark:hover:bg-gray-700`}
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className={`text-sm font-medium ${
                            isToday(day)
                              ? "bg-blue-600 text-white w-7 h-7 rounded-full flex items-center justify-center"
                              : isCurrentMonth
                              ? "text-gray-900 dark:text-white"
                              : "text-gray-400 dark:text-gray-500"
                          }`}
                        >
                          {format(day, "d")}
                        </span>
                        {dayTasks.length > 0 && (
                          <span className="flex space-x-1">
                            {hasOverdue && (
                              <span className="w-2 h-2 rounded-full bg-red-500"></span>
                            )}
                            {hasCritical && !hasOverdue && (
                              <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                            )}
                          </span>
                        )}
                      </div>
                      {/* Task indicators */}
                      <div className="mt-1 space-y-1">
                        {dayTasks.slice(0, 3).map((task) => (
                          <div
                            key={task.id}
                            className={`text-xs truncate px-1 py-0.5 rounded ${
                              task.status === "completed"
                                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                : task.status === "overdue"
                                ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                                : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                            }`}
                          >
                            {task.title}
                          </div>
                        ))}
                        {dayTasks.length > 3 && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 px-1">
                            +{dayTasks.length - 3} ещё
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Timeline View */
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Хронология задач
              </h2>
              <div className="space-y-4">
                {filteredTasks
                  .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
                  .map((task) => (
                    <div
                      key={task.id}
                      className={`p-4 rounded-lg border-l-4 bg-gray-50 dark:bg-gray-700 ${statusColors[task.status]}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span
                              className={`w-2 h-2 rounded-full ${priorityColors[task.priority]}`}
                            ></span>
                            <h3 className="font-medium text-gray-900 dark:text-white">
                              {task.title}
                            </h3>
                            {task.isRecurring && (
                              <ArrowPathIcon className="h-4 w-4 text-purple-500" />
                            )}
                          </div>
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            {task.description || "Нет описания"}
                          </p>
                          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                            <span>{task.framework}</span>
                            <span>{task.assignee}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {format(task.dueDate, "d MMM yyyy", { locale: ru })}
                          </div>
                          <div
                            className={`text-xs ${
                              task.status === "overdue"
                                ? "text-red-600"
                                : task.status === "completed"
                                ? "text-green-600"
                                : "text-gray-500"
                            }`}
                          >
                            {statusLabels[task.status]}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                {filteredTasks.length === 0 && (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    Нет задач для отображения
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Selected Date Tasks */}
          {selectedDate && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                {format(selectedDate, "d MMMM yyyy", { locale: ru })}
              </h3>
              {selectedDateTasks.length > 0 ? (
                <div className="space-y-3">
                  {selectedDateTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-3 rounded-lg border-l-4 bg-gray-50 dark:bg-gray-700 ${statusColors[task.status]}`}
                    >
                      <div className="flex items-center space-x-2">
                        <span
                          className={`w-2 h-2 rounded-full ${priorityColors[task.priority]}`}
                        ></span>
                        <h4 className="font-medium text-sm text-gray-900 dark:text-white">
                          {task.title}
                        </h4>
                      </div>
                      <div className="mt-1 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>{task.framework}</span>
                        <span>{statusLabels[task.status]}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Нет задач на эту дату
                </p>
              )}
            </div>
          )}

          {/* Overdue Tasks */}
          {overdueTasks.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center space-x-2 mb-3">
                <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Просроченные
                </h3>
                <span className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 text-xs px-2 py-0.5 rounded-full">
                  {overdueTasks.length}
                </span>
              </div>
              <div className="space-y-2">
                {overdueTasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="p-2 rounded bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
                  >
                    <div className="flex items-center space-x-2">
                      <span
                        className={`w-2 h-2 rounded-full ${priorityColors[task.priority]}`}
                      ></span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {task.title}
                      </span>
                    </div>
                    <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                      Просрочено на {Math.abs(differenceInDays(task.dueDate, new Date()))} дн.
                    </div>
                  </div>
                ))}
                {overdueTasks.length > 5 && (
                  <Link
                    to="/compliance-tasks"
                    className="block text-center text-sm text-red-600 hover:text-red-700"
                  >
                    Смотреть все ({overdueTasks.length})
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* Upcoming Tasks */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center space-x-2 mb-3">
              <ClockIcon className="h-5 w-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Предстоящие
              </h3>
            </div>
            {upcomingTasks.length > 0 ? (
              <div className="space-y-2">
                {upcomingTasks.map((task) => {
                  const daysUntil = differenceInDays(task.dueDate, new Date());
                  return (
                    <div
                      key={task.id}
                      className="p-2 rounded bg-gray-50 dark:bg-gray-700"
                    >
                      <div className="flex items-center space-x-2">
                        <span
                          className={`w-2 h-2 rounded-full ${priorityColors[task.priority]}`}
                        ></span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white truncate flex-1">
                          {task.title}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                        <span>{format(task.dueDate, "d MMM", { locale: ru })}</span>
                        <span
                          className={
                            daysUntil === 0
                              ? "text-orange-600"
                              : daysUntil <= 3
                              ? "text-yellow-600"
                              : ""
                          }
                        >
                          {daysUntil === 0
                            ? "Сегодня"
                            : daysUntil === 1
                            ? "Завтра"
                            : `${daysUntil} дн.`}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Нет предстоящих задач
              </p>
            )}
          </div>

          {/* Quick Link to Kanban */}
          <Link
            to="/compliance-tasks"
            className="block bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow p-4 text-center font-medium"
          >
            Открыть доску задач
          </Link>
        </div>
      </div>
    </div>
  );
}
