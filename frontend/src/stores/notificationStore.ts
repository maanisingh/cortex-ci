import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Notification {
  id: string;
  type: "reminder" | "warning" | "success" | "error" | "info";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  taskId?: string;
  dueDate?: Date;
  priority?: "low" | "medium" | "high" | "critical";
}

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isOpen: boolean;

  // Actions
  addNotification: (notification: Omit<Notification, "id" | "timestamp" | "read">) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  toggleOpen: () => void;
  setOpen: (isOpen: boolean) => void;

  // Due date reminder specific
  checkDueDateReminders: (tasks: TaskForReminder[]) => void;
  dismissedReminders: string[]; // Task IDs that have been dismissed
  dismissReminder: (taskId: string) => void;
}

export interface TaskForReminder {
  id: string;
  title: string;
  dueDate: Date | string;
  status: string;
  priority?: string;
  url?: string;
}

function generateId(): string {
  return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function getDaysUntilDue(dueDate: Date | string): number {
  const due = new Date(dueDate);
  const now = new Date();
  const diffTime = due.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set, get) => ({
      notifications: [],
      unreadCount: 0,
      isOpen: false,
      dismissedReminders: [],

      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: generateId(),
          timestamp: new Date(),
          read: false,
        };

        set((state) => ({
          notifications: [newNotification, ...state.notifications].slice(0, 100), // Keep last 100
          unreadCount: state.unreadCount + 1,
        }));
      },

      markAsRead: (id) => {
        set((state) => {
          const notification = state.notifications.find((n) => n.id === id);
          if (!notification || notification.read) return state;

          return {
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, read: true } : n
            ),
            unreadCount: Math.max(0, state.unreadCount - 1),
          };
        });
      },

      markAllAsRead: () => {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0,
        }));
      },

      removeNotification: (id) => {
        set((state) => {
          const notification = state.notifications.find((n) => n.id === id);
          const wasUnread = notification && !notification.read;

          return {
            notifications: state.notifications.filter((n) => n.id !== id),
            unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
          };
        });
      },

      clearAllNotifications: () => {
        set({ notifications: [], unreadCount: 0 });
      },

      toggleOpen: () => {
        set((state) => ({ isOpen: !state.isOpen }));
      },

      setOpen: (isOpen) => {
        set({ isOpen });
      },

      dismissReminder: (taskId) => {
        set((state) => ({
          dismissedReminders: [...state.dismissedReminders, taskId],
        }));
      },

      checkDueDateReminders: (tasks) => {
        const { dismissedReminders, addNotification, notifications } = get();
        const now = new Date();

        // Get existing task IDs in notifications to avoid duplicates
        const existingTaskIds = new Set(
          notifications
            .filter((n) => n.taskId && n.type === "reminder")
            .map((n) => n.taskId)
        );

        tasks.forEach((task) => {
          // Skip if already dismissed, already has notification, or completed
          if (
            dismissedReminders.includes(task.id) ||
            existingTaskIds.has(task.id) ||
            task.status === "completed" ||
            task.status === "done"
          ) {
            return;
          }

          const daysUntilDue = getDaysUntilDue(task.dueDate);
          const dueDate = new Date(task.dueDate);

          // Determine notification type based on days until due
          let notificationType: Notification["type"] = "info";
          let priority: Notification["priority"] = "low";
          let title = "";
          let message = "";

          if (daysUntilDue < 0) {
            // Overdue
            notificationType = "warning";
            priority = "critical";
            title = "Overdue Task";
            message = `"${task.title}" was due ${Math.abs(daysUntilDue)} day(s) ago!`;
          } else if (daysUntilDue === 0) {
            // Due today
            notificationType = "warning";
            priority = "high";
            title = "Due Today";
            message = `"${task.title}" is due today!`;
          } else if (daysUntilDue === 1) {
            // Due tomorrow
            notificationType = "reminder";
            priority = "high";
            title = "Due Tomorrow";
            message = `"${task.title}" is due tomorrow.`;
          } else if (daysUntilDue <= 3) {
            // Due within 3 days
            notificationType = "reminder";
            priority = "medium";
            title = "Upcoming Deadline";
            message = `"${task.title}" is due in ${daysUntilDue} days.`;
          } else if (daysUntilDue <= 7) {
            // Due within a week
            notificationType = "info";
            priority = "low";
            title = "Upcoming Task";
            message = `"${task.title}" is due in ${daysUntilDue} days.`;
          } else {
            // More than a week away - don't create notification
            return;
          }

          addNotification({
            type: notificationType,
            title,
            message,
            taskId: task.id,
            dueDate,
            priority,
            actionUrl: task.url || `/compliance-tasks`,
          });
        });
      },
    }),
    {
      name: "cortex-notifications",
      partialize: (state) => ({
        notifications: state.notifications.slice(0, 50), // Only persist last 50
        dismissedReminders: state.dismissedReminders.slice(-100), // Keep last 100 dismissed
      }),
    }
  )
);
