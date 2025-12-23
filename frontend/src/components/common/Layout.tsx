import { Fragment, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Dialog, Transition } from '@headlessui/react'
import {
  Bars3Icon,
  HomeIcon,
  BuildingOfficeIcon,
  ShieldExclamationIcon,
  LinkIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  UsersIcon,
  UserCircleIcon,
  // Phase 2 icons
  ArrowsRightLeftIcon,
  ScaleIcon,
  ClockIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '../../stores/authStore'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Entities', href: '/entities', icon: BuildingOfficeIcon },
  { name: 'Constraints', href: '/constraints', icon: ShieldExclamationIcon },
  { name: 'Dependencies', href: '/dependencies', icon: LinkIcon },
  { name: 'Risks', href: '/risks', icon: ExclamationTriangleIcon },
  { name: 'Scenarios', href: '/scenarios', icon: BeakerIcon },
  { name: 'Audit Log', href: '/audit', icon: ClipboardDocumentListIcon },
]

const phase2Navigation = [
  { name: 'Scenario Chains', href: '/scenario-chains', icon: ArrowsRightLeftIcon },
  { name: 'Risk Justification', href: '/risk-justification', icon: ScaleIcon },
  { name: 'Institutional Memory', href: '/history', icon: ClockIcon },
  { name: 'AI Analysis', href: '/ai-analysis', icon: SparklesIcon },
]

const adminNavigation = [
  { name: 'User Management', href: '/admin/users', icon: UsersIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

const userNavigation = [
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
]

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const { user, logout } = useAuthStore()

  return (
    <div>
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50 lg:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-900/80" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-primary-900 px-6 pb-4">
                  <div className="flex h-16 shrink-0 items-center">
                    <span className="text-2xl font-bold text-white">CORTEX-CI</span>
                  </div>
                  <nav className="flex flex-1 flex-col">
                    <ul role="list" className="flex flex-1 flex-col gap-y-7">
                      <li>
                        <ul role="list" className="-mx-2 space-y-1">
                          {navigation.map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href
                                    ? 'bg-primary-800 text-white'
                                    : 'text-primary-200 hover:text-white hover:bg-primary-800',
                                  'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                                )}
                                onClick={() => setSidebarOpen(false)}
                              >
                                <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                                {item.name}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                    </ul>
                  </nav>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-primary-900 px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
            <span className="text-2xl font-bold text-white">CORTEX-CI</span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'bg-primary-800 text-white'
                            : 'text-primary-200 hover:text-white hover:bg-primary-800',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                        )}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
              <li>
                <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">Phase 2</div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {phase2Navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'bg-primary-800 text-white'
                            : 'text-primary-200 hover:text-white hover:bg-primary-800',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                        )}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
              {user?.role?.toUpperCase() === 'ADMIN' && (
                <li>
                  <div className="text-xs font-semibold leading-6 text-primary-400 uppercase">Admin</div>
                  <ul role="list" className="-mx-2 mt-2 space-y-1">
                    {adminNavigation.map((item) => (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={classNames(
                            location.pathname === item.href
                              ? 'bg-primary-800 text-white'
                              : 'text-primary-200 hover:text-white hover:bg-primary-800',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                          )}
                        >
                          <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                          {item.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              )}
              <li className="mt-auto">
                <ul role="list" className="-mx-2 space-y-1 mb-4">
                  {userNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'bg-primary-800 text-white'
                            : 'text-primary-200 hover:text-white hover:bg-primary-800',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                        )}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
                <div className="text-primary-200 text-sm mb-2 border-t border-primary-700 pt-4">
                  {user?.full_name}
                  <span className="text-primary-400 block text-xs">{user?.email}</span>
                </div>
                <button
                  onClick={logout}
                  className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-primary-200 hover:bg-primary-800 hover:text-white w-full"
                >
                  Sign out
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      <div className="lg:pl-72">
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex items-center gap-x-4 lg:gap-x-6 ml-auto">
              <span className="text-sm text-gray-500">
                Role: <span className="font-medium text-gray-900 capitalize">{user?.role}</span>
              </span>
            </div>
          </div>
        </div>

        <main className="py-10">
          <div className="px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
