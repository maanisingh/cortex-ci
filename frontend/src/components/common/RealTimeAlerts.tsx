import { useState, useEffect, useCallback, useRef } from "react";
import { useAuthStore } from "../../stores/authStore";
import {
  BellIcon,
  BellAlertIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ShieldExclamationIcon,
} from "@heroicons/react/24/outline";

interface Alert {
  type: string;
  priority: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  data?: Record<string, unknown>;
  entity_id?: string;
  created_at: string;
}

interface WebSocketMessage {
  type: string;
  alert?: Alert;
  alerts?: Alert[];
  message?: string;
}

const PRIORITY_STYLES = {
  low: {
    bg: "bg-gray-50",
    border: "border-gray-200",
    icon: InformationCircleIcon,
    iconColor: "text-gray-500",
  },
  medium: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    icon: InformationCircleIcon,
    iconColor: "text-blue-500",
  },
  high: {
    bg: "bg-amber-50",
    border: "border-amber-200",
    icon: ExclamationTriangleIcon,
    iconColor: "text-amber-500",
  },
  critical: {
    bg: "bg-red-50",
    border: "border-red-200",
    icon: ShieldExclamationIcon,
    iconColor: "text-red-500",
  },
};

export default function RealTimeAlerts() {
  const { accessToken, isAuthenticated } = useAuthStore();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [connected, setConnected] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connectWebSocket = useCallback(() => {
    if (!accessToken || !isAuthenticated) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws?token=${accessToken}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);

          if (data.type === "alert" && data.alert) {
            setAlerts((prev) => [data.alert!, ...prev].slice(0, 50));
            setUnreadCount((prev) => prev + 1);

            // Show browser notification for high/critical alerts
            if (
              data.alert.priority === "high" ||
              data.alert.priority === "critical"
            ) {
              showBrowserNotification(data.alert);
            }
          } else if (data.type === "recent_alerts" && data.alerts) {
            setAlerts(data.alerts);
          } else if (data.type === "connected") {
            console.log("WebSocket connection confirmed");
          }
        } catch (e) {
          console.error("Failed to parse WebSocket message", e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        console.log("WebSocket disconnected");
        // Attempt reconnection after 5 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error", error);
        ws.close();
      };
    } catch (e) {
      console.error("Failed to create WebSocket", e);
    }
  }, [accessToken, isAuthenticated]);

  const showBrowserNotification = (alert: Alert) => {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(alert.title, {
        body: alert.message,
        icon: "/favicon.ico",
      });
    }
  };

  useEffect(() => {
    // Request notification permission
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket]);

  const clearAlerts = () => {
    setAlerts([]);
    setUnreadCount(0);
  };

  const dismissAlert = (index: number) => {
    setAlerts((prev) => prev.filter((_, i) => i !== index));
  };

  const handleOpenPanel = () => {
    setShowPanel(true);
    setUnreadCount(0);
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={handleOpenPanel}
        className="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none"
      >
        {unreadCount > 0 ? (
          <BellAlertIcon className="h-6 w-6 text-indigo-600 animate-pulse" />
        ) : (
          <BellIcon className="h-6 w-6" />
        )}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
        {/* Connection indicator */}
        <span
          className={`absolute bottom-1 right-1 w-2 h-2 rounded-full ${
            connected ? "bg-green-500" : "bg-red-500"
          }`}
        />
      </button>

      {/* Alerts Panel */}
      {showPanel && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowPanel(false)}
          />

          {/* Panel */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border z-50 max-h-[80vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b">
              <div className="flex items-center gap-2">
                <BellIcon className="h-5 w-5 text-gray-500" />
                <h3 className="font-medium text-gray-900">Notifications</h3>
                {!connected && (
                  <span className="text-xs text-red-500">(Disconnected)</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {alerts.length > 0 && (
                  <button
                    onClick={clearAlerts}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Clear all
                  </button>
                )}
                <button
                  onClick={() => setShowPanel(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Alerts List */}
            <div className="overflow-y-auto flex-1">
              {alerts.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500">
                  <CheckCircleIcon className="h-12 w-12 mx-auto text-gray-300 mb-2" />
                  <p>No notifications</p>
                  <p className="text-xs mt-1">You're all caught up!</p>
                </div>
              ) : (
                <div className="divide-y">
                  {alerts.map((alert, index) => {
                    const style = PRIORITY_STYLES[alert.priority];
                    const Icon = style.icon;

                    return (
                      <div
                        key={index}
                        className={`px-4 py-3 hover:bg-gray-50 relative ${style.bg}`}
                      >
                        <button
                          onClick={() => dismissAlert(index)}
                          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                        <div className="flex gap-3">
                          <Icon className={`h-5 w-5 flex-shrink-0 ${style.iconColor}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900">
                              {alert.title}
                            </p>
                            <p className="text-sm text-gray-600 mt-0.5">
                              {alert.message}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {formatTime(alert.created_at)}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-50 border-t text-center">
              <span className="text-xs text-gray-500">
                Real-time alerts powered by WebSocket
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
