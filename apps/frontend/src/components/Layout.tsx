// ============================================================
// CodeWhisper PR - Layout Components
// ============================================================

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../contexts/ThemeContext';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: '📊' },
  { name: 'Reviews', href: '/reviews', icon: '🔍' },
  { name: 'Analytics', href: '/analytics', icon: '📈' },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <Navigation />
      <main className="ml-64 p-6">{children}</main>
    </div>
  );
}

function Navigation() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="fixed top-0 left-0 h-screen w-64 bg-gray-800 border-r border-gray-700 p-4 overflow-y-auto">
      <div className="mb-8">
        <Link href="/dashboard">
          <a className="text-xl font-bold text-white">CodeWhisper PR</a>
        </Link>
      </div>

      <ul className="space-y-2 mb-8">
        {navigation.map((item) => {
          const isActive = router.pathname === item.href;
          return (
            <li key={item.href}>
              <Link href={item.href}>
                <a
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <span>{item.icon}</span>
                  {item.name}
                </a>
              </Link>
            </li>
          );
        })}
      </ul>

      <div className="border-t border-gray-700 pt-4">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-lg transition-colors"
        >
          <span>{theme === 'dark' ? '☀️' : '🌙'}</span>
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>

        {user && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex items-center gap-3 px-3 mb-2">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                {user.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div>
                <p className="font-medium text-white">{user.username}</p>
                <p className="text-sm text-gray-400">{user.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-3 py-2 text-gray-300 hover:bg-red-600 hover:text-white rounded-lg transition-colors"
            >
              <span>🚪</span>
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
