import { Fragment } from "react";
import { Menu, Transition } from "@headlessui/react";
import { GlobeAltIcon, ChevronDownIcon } from "@heroicons/react/24/outline";
import { useLanguage, LanguageCode } from "../../contexts/LanguageContext";

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(" ");
}

interface LanguageSelectorProps {
  variant?: "light" | "dark";
  showLabel?: boolean;
}

export default function LanguageSelector({
  variant = "light",
  showLabel = true,
}: LanguageSelectorProps) {
  const { language, setLanguage, languages, t } = useLanguage();
  const currentLang = languages[language];

  const textColor = variant === "dark" ? "text-gray-300" : "text-gray-700";
  const hoverBg =
    variant === "dark" ? "hover:bg-gray-700" : "hover:bg-gray-100";
  const menuBg = variant === "dark" ? "bg-gray-800" : "bg-white";
  const borderColor = variant === "dark" ? "ring-gray-700" : "ring-gray-200";

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <Menu.Button
          className={classNames(
            "inline-flex items-center gap-x-1.5 rounded-md px-3 py-2 text-sm font-medium",
            textColor,
            hoverBg,
            "transition-colors",
          )}
        >
          <GlobeAltIcon className="h-5 w-5" aria-hidden="true" />
          {showLabel && (
            <>
              <span>{currentLang.flag}</span>
              <span className="hidden sm:inline">{currentLang.nativeName}</span>
            </>
          )}
          <ChevronDownIcon className="h-4 w-4" aria-hidden="true" />
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items
          className={classNames(
            "absolute right-0 z-50 mt-2 w-56 origin-top-right rounded-md shadow-lg ring-1 ring-opacity-5 focus:outline-none",
            menuBg,
            borderColor,
          )}
        >
          <div className="py-1 max-h-96 overflow-y-auto">
            <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase">
              {t("selectLanguage")}
            </div>
            {(Object.keys(languages) as LanguageCode[]).map((langCode) => {
              const lang = languages[langCode];
              const isSelected = langCode === language;
              return (
                <Menu.Item key={langCode}>
                  {({ active }) => (
                    <button
                      onClick={() => setLanguage(langCode)}
                      className={classNames(
                        active
                          ? variant === "dark"
                            ? "bg-gray-700"
                            : "bg-gray-100"
                          : "",
                        isSelected ? "font-semibold" : "",
                        "flex w-full items-center gap-x-3 px-4 py-2 text-sm",
                        variant === "dark" ? "text-gray-200" : "text-gray-700",
                      )}
                    >
                      <span className="text-lg">{lang.flag}</span>
                      <span className="flex-1 text-left">
                        {lang.nativeName}
                      </span>
                      {isSelected && (
                        <svg
                          className="h-5 w-5 text-primary-600"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </button>
                  )}
                </Menu.Item>
              );
            })}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
