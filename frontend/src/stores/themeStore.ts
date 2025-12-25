import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ThemeState {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  setDarkMode: (isDark: boolean) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      isDarkMode: false,

      toggleDarkMode: () => {
        const newMode = !get().isDarkMode;
        set({ isDarkMode: newMode });
        applyTheme(newMode);
      },

      setDarkMode: (isDark: boolean) => {
        set({ isDarkMode: isDark });
        applyTheme(isDark);
      },
    }),
    {
      name: "cortex-theme",
      onRehydrateStorage: () => (state) => {
        if (state) {
          applyTheme(state.isDarkMode);
        }
      },
    }
  )
);

function applyTheme(isDark: boolean) {
  if (isDark) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

// Initialize theme on load
if (typeof window !== "undefined") {
  const stored = localStorage.getItem("cortex-theme");
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      applyTheme(parsed.state?.isDarkMode ?? false);
    } catch {
      // Default to light mode
    }
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    // Use system preference if no stored preference
    applyTheme(true);
  }
}
