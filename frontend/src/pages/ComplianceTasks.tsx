import { useState, useEffect, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useDueDateReminders } from "../hooks/useDueDateReminders";
import { TaskForReminder } from "../stores/notificationStore";
import {
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  UserCircleIcon,
  CalendarIcon,
  DocumentTextIcon,
  ChevronRightIcon,
  XMarkIcon,
  SparklesIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon as CheckCircleSolidIcon } from "@heroicons/react/24/solid";
import { russianComplianceApi } from "../services/api";

// Status mapping from API to frontend
const statusMapping: Record<string, string> = {
  NOT_STARTED: "pending",
  IN_PROGRESS: "in_progress",
  PENDING_REVIEW: "in_progress",
  COMPLETED: "completed",
  OVERDUE: "overdue",
  BLOCKED: "pending",
};

// Priority mapping from API to frontend
const priorityMapping: Record<string, string> = {
  CRITICAL: "critical",
  HIGH: "high",
  MEDIUM: "medium",
  LOW: "low",
};

type TaskStatus = "pending" | "in_progress" | "completed" | "overdue";
type TaskPriority = "low" | "medium" | "high" | "critical";

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
  next_due_date: string | null;
  started_at: string | null;
  completed_at: string | null;
  completion_notes: string | null;
  created_at: string | null;
}

interface Task {
  id: string;
  title: string;
  description: string;
  category: string;
  status: TaskStatus;
  priority: TaskPriority;
  assigneeId: string;
  assigneeName: string;
  assigneeRole: string;
  companyId: string;
  framework: string;
  dueDate: string;
  createdAt: string;
  completedAt?: string;
  isRecurring: boolean;
  recurrenceDays?: number;
}

const statusConfig = {
  pending: { label: "Ожидает", color: "bg-gray-100 text-gray-800", icon: ClockIcon },
  in_progress: { label: "В работе", color: "bg-blue-100 text-blue-800", icon: ClockIcon },
  completed: { label: "Выполнено", color: "bg-green-100 text-green-800", icon: CheckCircleIcon },
  overdue: { label: "Просрочено", color: "bg-red-100 text-red-800", icon: ExclamationCircleIcon },
};

const priorityConfig = {
  low: { label: "Низкий", color: "text-gray-500" },
  medium: { label: "Средний", color: "text-yellow-600" },
  high: { label: "Высокий", color: "text-orange-600" },
  critical: { label: "Критический", color: "text-red-600" },
};

// Map API task to frontend format
const mapApiTask = (apiTask: ApiTask, companyId: string): Task => {
  let status = statusMapping[apiTask.status] as TaskStatus || "pending";

  // Check if overdue
  if (apiTask.due_date && status !== "completed") {
    const dueDate = new Date(apiTask.due_date);
    const now = new Date();
    if (dueDate < now) {
      status = "overdue";
    }
  }

  return {
    id: apiTask.id,
    title: apiTask.title,
    description: apiTask.description || "",
    category: apiTask.task_type || "compliance",
    status,
    priority: (priorityMapping[apiTask.priority] as TaskPriority) || "medium",
    assigneeId: apiTask.assigned_to || "",
    assigneeName: apiTask.assigned_department || "Не назначено",
    assigneeRole: apiTask.assigned_role || "",
    companyId,
    framework: apiTask.framework || "152-ФЗ",
    dueDate: apiTask.due_date || new Date().toISOString(),
    createdAt: apiTask.created_at || new Date().toISOString(),
    completedAt: apiTask.completed_at || undefined,
    isRecurring: apiTask.is_recurring,
    recurrenceDays: apiTask.recurrence_days || undefined,
  };
};

export default function ComplianceTasks() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | "all">("all");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");

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

  // Fetch tasks for selected company
  const { data: apiTasks = [], isLoading, refetch } = useQuery({
    queryKey: ["compliance-tasks", selectedCompanyId],
    queryFn: async () => {
      if (!selectedCompanyId) return [];
      const response = await russianComplianceApi.tasks.list(selectedCompanyId);
      return response.data;
    },
    enabled: !!selectedCompanyId,
  });

  // Map API tasks to frontend format
  const tasks: Task[] = apiTasks.map((t: ApiTask) => mapApiTask(t, selectedCompanyId));

  // Convert tasks to reminder format for due date notifications
  const tasksForReminders = useMemo<TaskForReminder[]>(() => {
    return tasks.map((task) => ({
      id: task.id,
      title: task.title,
      dueDate: task.dueDate,
      status: task.status,
      priority: task.priority,
      url: `/compliance-tasks`,
    }));
  }, [tasks]);

  // Check for due date reminders
  useDueDateReminders(tasksForReminders, { enabled: tasks.length > 0 });

  // Complete task mutation
  const completeMutation = useMutation({
    mutationFn: async (taskId: string) => {
      return russianComplianceApi.tasks.complete(selectedCompanyId, taskId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-tasks"] });
    },
  });

  // Update task mutation
  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, data }: { taskId: string; data: { status?: string } }) => {
      return russianComplianceApi.tasks.update(selectedCompanyId, taskId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-tasks"] });
    },
  });

  // Generate tasks from template mutation
  const generateTasksMutation = useMutation({
    mutationFn: async () => {
      return russianComplianceApi.tasks.generateFromTemplate(selectedCompanyId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-tasks"] });
    },
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: async (data: {
      title: string;
      description?: string;
      priority?: string;
      due_date?: string;
    }) => {
      return russianComplianceApi.tasks.create(selectedCompanyId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance-tasks"] });
      setShowCreateModal(false);
    },
  });

  // Filter tasks
  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      searchQuery === "" ||
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || task.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  // Group by status for kanban-style view
  const tasksByStatus = {
    overdue: filteredTasks.filter((t) => t.status === "overdue"),
    pending: filteredTasks.filter((t) => t.status === "pending"),
    in_progress: filteredTasks.filter((t) => t.status === "in_progress"),
    completed: filteredTasks.filter((t) => t.status === "completed"),
  };

  // Stats
  const stats = {
    total: tasks.length,
    pending: tasks.filter((t) => t.status === "pending").length,
    inProgress: tasks.filter((t) => t.status === "in_progress").length,
    completed: tasks.filter((t) => t.status === "completed").length,
    overdue: tasks.filter((t) => t.status === "overdue").length,
  };

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diff = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  // Create task form state
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "MEDIUM",
    due_date: "",
  });

  if (!selectedCompanyId && companies.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-lg font-medium text-gray-900">Нет зарегистрированных компаний</h2>
        <p className="mt-2 text-sm text-gray-500">
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Задачи по соответствию</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Управление задачами для достижения полного соответствия требованиям 152-ФЗ
          </p>
        </div>
        <div className="flex space-x-2">
          {tasks.length === 0 && (
            <button
              onClick={() => generateTasksMutation.mutate()}
              disabled={generateTasksMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
            >
              {generateTasksMutation.isPending ? (
                <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
              ) : (
                <SparklesIcon className="h-5 w-5 mr-2" />
              )}
              Сгенерировать задачи 152-ФЗ
            </button>
          )}
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Создать задачу
          </button>
        </div>
      </div>

      {/* Company selector */}
      {companies.length > 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Выберите компанию
          </label>
          <select
            value={selectedCompanyId}
            onChange={(e) => setSelectedCompanyId(e.target.value)}
            className="w-full md:w-auto border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
          >
            {companies.map((company: { id: string; legal_name: string }) => (
              <option key={company.id} value={company.id}>
                {company.legal_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Всего задач</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-600 dark:text-gray-300">{stats.pending}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Ожидают</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-600">{stats.inProgress}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">В работе</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Выполнено</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Просрочено</div>
        </div>
      </div>

      {/* Search and filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск задач..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Обновить
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center px-4 py-2 border rounded-md text-sm font-medium ${
              showFilters
                ? "border-blue-500 text-blue-700 bg-blue-50 dark:bg-blue-900 dark:text-blue-200"
                : "border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
            }`}
          >
            <FunnelIcon className="h-5 w-5 mr-2" />
            Фильтры
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 pt-4 border-t dark:border-gray-700 flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Статус</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as TaskStatus | "all")}
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
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Приоритет</label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value as TaskPriority | "all")}
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
        )}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && tasks.length === 0 && (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <CalendarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Нет задач</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Создайте новую задачу или сгенерируйте задачи для соответствия 152-ФЗ
          </p>
          <div className="mt-6">
            <button
              onClick={() => generateTasksMutation.mutate()}
              disabled={generateTasksMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              <SparklesIcon className="h-5 w-5 mr-2" />
              Сгенерировать 20 задач 152-ФЗ
            </button>
          </div>
        </div>
      )}

      {/* Kanban board */}
      {!isLoading && tasks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {(["overdue", "pending", "in_progress", "completed"] as TaskStatus[]).map((status) => (
            <div key={status} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${statusConfig[status].color}`}
                  >
                    {statusConfig[status].label}
                  </span>
                  <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                    {tasksByStatus[status].length}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                {tasksByStatus[status].map((task) => (
                  <div
                    key={task.id}
                    onClick={() => setSelectedTask(task)}
                    className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2">
                        {task.title}
                      </h3>
                      <span className={`text-xs ${priorityConfig[task.priority].color}`}>
                        {priorityConfig[task.priority].label}
                      </span>
                    </div>

                    {task.isRecurring && (
                      <div className="mt-2 flex items-center text-xs text-purple-600">
                        <ArrowPathIcon className="h-3 w-3 mr-1" />
                        Повторяется каждые {task.recurrenceDays} дн.
                      </div>
                    )}

                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center">
                        <UserCircleIcon className="h-5 w-5 text-gray-400" />
                        <span className="ml-1 text-xs text-gray-500 dark:text-gray-400 truncate">
                          {task.assigneeName}
                        </span>
                      </div>
                      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        {(() => {
                          const days = getDaysUntilDue(task.dueDate);
                          if (task.status === "completed") return "Выполнено";
                          if (days < 0) return `${Math.abs(days)} дн. назад`;
                          if (days === 0) return "Сегодня";
                          if (days === 1) return "Завтра";
                          return `${days} дн.`;
                        })()}
                      </div>
                    </div>

                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-gray-400">{task.framework}</span>
                    </div>
                  </div>
                ))}

                {tasksByStatus[status].length === 0 && (
                  <div className="text-center py-4 text-sm text-gray-400">
                    Нет задач
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Task detail modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        statusConfig[selectedTask.status].color
                      }`}
                    >
                      {statusConfig[selectedTask.status].label}
                    </span>
                    <span className={`text-sm ${priorityConfig[selectedTask.priority].color}`}>
                      {priorityConfig[selectedTask.priority].label} приоритет
                    </span>
                    {selectedTask.isRecurring && (
                      <span className="text-xs text-purple-600 flex items-center">
                        <ArrowPathIcon className="h-3 w-3 mr-1" />
                        Повторяется
                      </span>
                    )}
                  </div>
                  <h2 className="mt-2 text-xl font-bold text-gray-900 dark:text-white">{selectedTask.title}</h2>
                </div>
                <button
                  onClick={() => setSelectedTask(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="mt-6 space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Описание</h3>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {selectedTask.description || "Нет описания"}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Ответственный</h3>
                    <div className="mt-1 flex items-center">
                      <UserCircleIcon className="h-8 w-8 text-gray-400" />
                      <div className="ml-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {selectedTask.assigneeName}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{selectedTask.assigneeRole}</p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Срок выполнения</h3>
                    <p className="mt-1 text-sm text-gray-900 dark:text-white">
                      {new Date(selectedTask.dueDate).toLocaleDateString("ru-RU", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      })}
                    </p>
                    {selectedTask.status !== "completed" && (
                      <p
                        className={`text-xs ${
                          getDaysUntilDue(selectedTask.dueDate) < 0
                            ? "text-red-600"
                            : getDaysUntilDue(selectedTask.dueDate) <= 3
                            ? "text-orange-600"
                            : "text-gray-500"
                        }`}
                      >
                        {(() => {
                          const days = getDaysUntilDue(selectedTask.dueDate);
                          if (days < 0) return `Просрочено на ${Math.abs(days)} дн.`;
                          if (days === 0) return "Срок истекает сегодня";
                          if (days === 1) return "Осталось 1 день";
                          return `Осталось ${days} дн.`;
                        })()}
                      </p>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Нормативная база</h3>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedTask.framework}</p>
                </div>

                {selectedTask.completedAt && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Выполнено</h3>
                    <p className="mt-1 text-sm text-gray-900 dark:text-white">
                      {new Date(selectedTask.completedAt).toLocaleString("ru-RU")}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 pt-6 border-t dark:border-gray-700 flex justify-between">
                <button
                  onClick={() => setSelectedTask(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Закрыть
                </button>
                <div className="space-x-2">
                  {selectedTask.status !== "completed" && (
                    <>
                      {selectedTask.status === "pending" && (
                        <button
                          onClick={() => {
                            updateTaskMutation.mutate({
                              taskId: selectedTask.id,
                              data: { status: "IN_PROGRESS" },
                            });
                            setSelectedTask(null);
                          }}
                          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                        >
                          Начать работу
                        </button>
                      )}
                      <button
                        onClick={() => {
                          completeMutation.mutate(selectedTask.id);
                          setSelectedTask(null);
                        }}
                        className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                      >
                        <CheckCircleSolidIcon className="h-5 w-5 mr-1" />
                        Выполнено
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create task modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Создать задачу</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Название задачи *
                  </label>
                  <input
                    type="text"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
                    placeholder="Введите название задачи"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Описание
                  </label>
                  <textarea
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
                    rows={3}
                    placeholder="Описание задачи"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Приоритет
                    </label>
                    <select
                      value={newTask.priority}
                      onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="LOW">Низкий</option>
                      <option value="MEDIUM">Средний</option>
                      <option value="HIGH">Высокий</option>
                      <option value="CRITICAL">Критический</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Срок выполнения
                    </label>
                    <input
                      type="date"
                      value={newTask.due_date}
                      onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                      className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-2">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Отмена
                </button>
                <button
                  onClick={() => createTaskMutation.mutate(newTask)}
                  disabled={!newTask.title || createTaskMutation.isPending}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {createTaskMutation.isPending ? "Создание..." : "Создать"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
