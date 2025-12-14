import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Box,
  Workflow,
  GitBranch,
  AlertTriangle,
  Shield,
  Scale,
  BarChart3,
  Menu,
} from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Atoms', href: '/atoms', icon: Box },
  { name: 'Molecules', href: '/molecules', icon: GitBranch },
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Risks', href: '/risks', icon: AlertTriangle },
  { name: 'Controls', href: '/controls', icon: Shield },
  { name: 'Regulations', href: '/regulations', icon: Scale },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-white border-b border-zinc-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-indigo-600 rounded-md flex items-center justify-center">
                  <span className="text-white font-semibold text-lg">DC</span>
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-zinc-900">
                    Docs-as-Code Platform
                  </h1>
                  <p className="text-sm text-zinc-500">Banking Knowledge Graph</p>
                </div>
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <button className="text-sm text-zinc-700 hover:text-zinc-900">
                Documentation
              </button>
              <div className="w-8 h-8 rounded-full bg-zinc-200 flex items-center justify-center">
                <span className="text-sm font-medium text-zinc-700">U</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-white border-r border-zinc-200 overflow-y-auto scrollbar-thin">
          <nav className="px-3 py-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors
                    ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900'
                    }
                  `}
                >
                  <Icon
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-indigo-600' : 'text-zinc-500'
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Sidebar Footer */}
          <div className="absolute bottom-0 w-64 p-4 border-t border-zinc-200 bg-white">
            <div className="text-xs text-zinc-500">
              <p className="font-medium">Environment: Production</p>
              <p className="mt-1">Version 1.0.0</p>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto scrollbar-thin bg-zinc-50">
          <div className="max-w-9xl mx-auto px-6 py-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
