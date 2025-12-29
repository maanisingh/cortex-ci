import { NavLink, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  DocumentTextIcon,
  ClipboardDocumentCheckIcon,
  ShieldCheckIcon,
  Bars3BottomLeftIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  DocumentTextIcon as DocumentTextIconSolid,
  ClipboardDocumentCheckIcon as ClipboardDocumentCheckIconSolid,
  ShieldCheckIcon as ShieldCheckIconSolid,
} from '@heroicons/react/24/solid';
import { useLanguage } from '../../contexts/LanguageContext';

interface NavItem {
  name: string;
  nameRu: string;
  href: string;
  icon: React.ElementType;
  activeIcon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  {
    name: 'Dashboard',
    nameRu: 'Главная',
    href: '/dashboard',
    icon: HomeIcon,
    activeIcon: HomeIconSolid,
  },
  {
    name: 'Tasks',
    nameRu: 'Задачи',
    href: '/compliance-tasks',
    icon: ClipboardDocumentCheckIcon,
    activeIcon: ClipboardDocumentCheckIconSolid,
  },
  {
    name: 'Documents',
    nameRu: 'Документы',
    href: '/documents',
    icon: DocumentTextIcon,
    activeIcon: DocumentTextIconSolid,
  },
  {
    name: 'Compliance',
    nameRu: 'Соответствие',
    href: '/russian-compliance',
    icon: ShieldCheckIcon,
    activeIcon: ShieldCheckIconSolid,
  },
];

interface MobileBottomNavProps {
  onMenuClick: () => void;
}

export default function MobileBottomNav({ onMenuClick }: MobileBottomNavProps) {
  const { language } = useLanguage();
  const location = useLocation();
  const isRussian = language === 'ru';

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white dark:bg-dark-800 border-t border-gray-200 dark:border-dark-600 lg:hidden safe-area-pb">
      <div className="flex items-center justify-around h-16">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.href ||
            (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
          const Icon = isActive ? item.activeIcon : item.icon;

          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={`flex flex-col items-center justify-center flex-1 h-full px-2 transition-colors ${
                isActive
                  ? 'text-primary-600 dark:text-primary-400'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              <Icon className="h-6 w-6" />
              <span className="text-xs mt-1 font-medium truncate">
                {isRussian ? item.nameRu : item.name}
              </span>
            </NavLink>
          );
        })}

        {/* Menu button to open sidebar */}
        <button
          onClick={onMenuClick}
          className="flex flex-col items-center justify-center flex-1 h-full px-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
        >
          <Bars3BottomLeftIcon className="h-6 w-6" />
          <span className="text-xs mt-1 font-medium">
            {isRussian ? 'Меню' : 'Menu'}
          </span>
        </button>
      </div>
    </nav>
  );
}
