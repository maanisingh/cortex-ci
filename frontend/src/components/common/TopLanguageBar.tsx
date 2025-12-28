import { useLanguage, LanguageCode } from "../../contexts/LanguageContext";

export default function TopLanguageBar() {
  const { language, setLanguage, languages, t } = useLanguage();

  // Show popular languages inline, rest in a dropdown
  const popularLanguages: LanguageCode[] = ["ru", "en", "kk", "uz", "tt"];
  const otherLanguages = (Object.keys(languages) as LanguageCode[]).filter(
    (lang) => !popularLanguages.includes(lang),
  );

  return (
    <div className="bg-gray-900 text-gray-300 text-sm py-2.5 px-4 flex items-center justify-end gap-3 border-b border-gray-800 relative z-[60]">
      <span className="text-gray-500 mr-2 hidden sm:inline">
        {t("selectLanguage")}:
      </span>
      <div className="flex items-center gap-1">
        {popularLanguages.map((langCode) => {
          const lang = languages[langCode];
          const isSelected = langCode === language;
          return (
            <button
              key={langCode}
              type="button"
              onClick={() => setLanguage(langCode)}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                isSelected
                  ? "bg-primary-600 text-white"
                  : "hover:bg-gray-800 text-gray-400 hover:text-white"
              }`}
            >
              <span className="mr-1.5">{lang.flag}</span>
              <span className="hidden sm:inline">{lang.nativeName}</span>
              <span className="sm:hidden">{langCode.toUpperCase()}</span>
            </button>
          );
        })}

        {/* Dropdown for other languages */}
        <div className="relative group">
          <button
            type="button"
            className="px-3 py-1.5 rounded hover:bg-gray-800 text-gray-400 hover:text-white flex items-center gap-1 cursor-pointer"
          >
            <span>+{otherLanguages.length}</span>
            <svg
              className="w-3 h-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          <div className="absolute right-0 top-full mt-1 bg-gray-800 rounded-md shadow-lg py-1 z-[70] hidden group-hover:block min-w-[150px]">
            {otherLanguages.map((langCode) => {
              const lang = languages[langCode];
              const isSelected = langCode === language;
              return (
                <button
                  key={langCode}
                  type="button"
                  onClick={() => setLanguage(langCode)}
                  className={`w-full text-left px-3 py-2 flex items-center gap-2 cursor-pointer ${
                    isSelected
                      ? "bg-primary-600 text-white"
                      : "hover:bg-gray-700 text-gray-300"
                  }`}
                >
                  <span>{lang.flag}</span>
                  <span>{lang.nativeName}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
