import { Fragment, useEffect } from "react";
import { Menu, Transition } from "@headlessui/react";
import {
  BellIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ClockIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { BellIcon as BellIconSolid } from "@heroicons/react/24/solid";
import { useNavigate } from "react-router-dom";
import { useNotificationStore, Notification } from "../../stores/notificationStore";
import { useLanguage } from "../../contexts/LanguageContext";
import { formatDistanceToNow } from "date-fns";
import { ru, enUS } from "date-fns/locale";

function getNotificationIcon(type: Notification["type"]) {
  switch (type) {
    case "warning":
      return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
    case "error":
      return <XMarkIcon className="h-5 w-5 text-red-500" />;
    case "success":
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    case "reminder":
      return <ClockIcon className="h-5 w-5 text-blue-500" />;
    case "info":
    default:
      return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
  }
}

function getPriorityColor(priority?: Notification["priority"]) {
  switch (priority) {
    case "critical":
      return "border-l-red-500";
    case "high":
      return "border-l-orange-500";
    case "medium":
      return "border-l-yellow-500";
    case "low":
    default:
      return "border-l-blue-500";
  }
}

export default function NotificationCenter() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    dismissReminder,
  } = useNotificationStore();

  const dateLocale = language === "ru" ? ru : enUS;

  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id);
    if (notification.actionUrl) {
      navigate(notification.actionUrl);
    }
  };

  const handleDismiss = (e: React.MouseEvent, notification: Notification) => {
    e.stopPropagation();
    removeNotification(notification.id);
    if (notification.taskId) {
      dismissReminder(notification.taskId);
    }
  };

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
        {unreadCount > 0 ? (
          <BellIconSolid className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        ) : (
          <BellIcon className="h-6 w-6" />
        )}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[20px] h-5 px-1 text-xs font-bold text-white bg-red-500 rounded-full">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 mt-2 w-96 max-h-[70vh] overflow-hidden bg-white dark:bg-gray-800 rounded-xl shadow-xl ring-1 ring-black/5 dark:ring-white/10 focus:outline-none z-50">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {language === "ru" ? "Уведомления" : "Notifications"}
            </h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    markAllAsRead();
                  }}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {language === "ru" ? "Прочитать все" : "Mark all read"}
                </button>
              )}
              {notifications.length > 0 && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    clearAllNotifications();
                  }}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:underline"
                >
                  {language === "ru" ? "Очистить" : "Clear"}
                </button>
              )}
            </div>
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto max-h-[calc(70vh-60px)]">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                <BellIcon className="h-12 w-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                <p>{language === "ru" ? "Нет уведомлений" : "No notifications"}</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {notifications.map((notification) => (
                  <Menu.Item key={notification.id}>
                    {({ active }) => (
                      <div
                        onClick={() => handleNotificationClick(notification)}
                        className={`
                          px-4 py-3 cursor-pointer border-l-4 transition-colors
                          ${getPriorityColor(notification.priority)}
                          ${!notification.read ? "bg-blue-50 dark:bg-blue-900/20" : ""}
                          ${active ? "bg-gray-100 dark:bg-gray-700" : ""}
                        `}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 mt-0.5">
                            {getNotificationIcon(notification.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                              <p
                                className={`text-sm font-medium ${
                                  !notification.read
                                    ? "text-gray-900 dark:text-white"
                                    : "text-gray-600 dark:text-gray-300"
                                }`}
                              >
                                {notification.title}
                              </p>
                              <button
                                onClick={(e) => handleDismiss(e, notification)}
                                className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
                              >
                                <XMarkIcon className="h-4 w-4" />
                              </button>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-2">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-gray-400 dark:text-gray-500">
                                {formatDistanceToNow(new Date(notification.timestamp), {
                                  addSuffix: true,
                                  locale: dateLocale,
                                })}
                              </span>
                              {notification.dueDate && (
                                <span
                                  className={`text-xs px-1.5 py-0.5 rounded ${
                                    new Date(notification.dueDate) < new Date()
                                      ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                      : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                  }`}
                                >
                                  {new Date(notification.dueDate).toLocaleDateString(
                                    language === "ru" ? "ru-RU" : "en-US",
                                    { month: "short", day: "numeric" }
                                  )}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </Menu.Item>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => navigate("/compliance-tasks")}
                className="w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:underline py-1"
              >
                {language === "ru" ? "Все задачи" : "View all tasks"}
              </button>
            </div>
          )}
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
