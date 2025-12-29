import { useEffect, useCallback } from "react";
import { useNotificationStore, TaskForReminder } from "../stores/notificationStore";

interface UseRemindersOptions {
  enabled?: boolean;
  checkIntervalMs?: number; // How often to re-check (default: 5 minutes)
}

export function useDueDateReminders(
  tasks: TaskForReminder[] | undefined,
  options: UseRemindersOptions = {}
) {
  const { enabled = true, checkIntervalMs = 5 * 60 * 1000 } = options;
  const { checkDueDateReminders } = useNotificationStore();

  const checkReminders = useCallback(() => {
    if (!tasks || tasks.length === 0) return;
    checkDueDateReminders(tasks);
  }, [tasks, checkDueDateReminders]);

  // Check on initial load and when tasks change
  useEffect(() => {
    if (!enabled) return;
    checkReminders();
  }, [enabled, checkReminders]);

  // Set up periodic checking
  useEffect(() => {
    if (!enabled || checkIntervalMs <= 0) return;

    const intervalId = setInterval(checkReminders, checkIntervalMs);
    return () => clearInterval(intervalId);
  }, [enabled, checkIntervalMs, checkReminders]);

  return { checkReminders };
}

// Hook to manually trigger a reminder check from anywhere in the app
export function useManualReminderCheck() {
  const { checkDueDateReminders } = useNotificationStore();

  return useCallback(
    (tasks: TaskForReminder[]) => {
      checkDueDateReminders(tasks);
    },
    [checkDueDateReminders]
  );
}
