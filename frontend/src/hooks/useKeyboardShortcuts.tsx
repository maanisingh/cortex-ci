import { useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

interface ShortcutConfig {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: () => void;
  description: string;
}

export const KEYBOARD_SHORTCUTS: Omit<ShortcutConfig, "action">[] = [
  { key: "d", altKey: true, description: "Go to Dashboard" },
  { key: "e", altKey: true, description: "Go to Entities" },
  { key: "c", altKey: true, description: "Go to Constraints" },
  { key: "r", altKey: true, description: "Go to Risks" },
  { key: "s", altKey: true, description: "Go to Scenarios" },
  { key: "a", altKey: true, description: "Go to Audit Log" },
  { key: "/", description: "Open search (when available)" },
  { key: "?", shiftKey: true, description: "Show keyboard shortcuts" },
  { key: "Escape", description: "Close modals" },
];

export function useKeyboardShortcuts(onShowShortcuts?: () => void) {
  const navigate = useNavigate();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const target = event.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.contentEditable === "true"
      ) {
        return;
      }

      const { key, ctrlKey, metaKey, shiftKey, altKey } = event;

      // Navigation shortcuts (Alt + key)
      if (altKey && !ctrlKey && !metaKey) {
        switch (key.toLowerCase()) {
          case "d":
            event.preventDefault();
            navigate("/");
            break;
          case "e":
            event.preventDefault();
            navigate("/entities");
            break;
          case "c":
            event.preventDefault();
            navigate("/constraints");
            break;
          case "r":
            event.preventDefault();
            navigate("/risks");
            break;
          case "s":
            event.preventDefault();
            navigate("/scenarios");
            break;
          case "a":
            event.preventDefault();
            navigate("/audit");
            break;
          case "l":
            event.preventDefault();
            navigate("/dependency-layers");
            break;
          case "h":
            event.preventDefault();
            navigate("/history");
            break;
        }
      }

      // Show shortcuts help (Shift + ?)
      if (shiftKey && key === "?") {
        event.preventDefault();
        onShowShortcuts?.();
      }
    },
    [navigate, onShowShortcuts],
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
}

// Component to display keyboard shortcuts
export function KeyboardShortcutsHelp({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Keyboard Shortcuts
          </h2>
          <div className="space-y-3">
            <div className="border-b pb-2 mb-2">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                Navigation
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Dashboard
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+D
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Entities
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+E
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Constraints
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+C
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Risks
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+R
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Scenarios
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+S
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Audit Log
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+A
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Layers
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+L
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    History
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Alt+H
                  </kbd>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                General
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Show shortcuts
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Shift+?
                  </kbd>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Close modal
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    Esc
                  </kbd>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="mt-4 w-full py-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
