import { useState, useEffect } from 'react';
import { api } from '../api';

interface Props {
  darkMode: boolean;
  onToggleDark: () => void;
  onLogout: () => void;
}

export function Header({ darkMode, onToggleDark, onLogout }: Props) {
  const [health, setHealth] = useState<any>(null);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
  }, []);

  return (
    <header className={`border-b px-6 py-3 flex items-center justify-between sticky top-0 z-50 backdrop-blur-sm transition-colors ${
      darkMode
        ? 'bg-slate-900/95 border-slate-800'
        : 'bg-white/95 border-surface-200'
    }`}>
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
          <span className="text-white text-lg font-bold">T</span>
        </div>
        <div>
          <h1 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-surface-900'}`}>TikTok AI Suite</h1>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-surface-400'}`}>Creator Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark mode toggle */}
        <button
          onClick={onToggleDark}
          className={`btn-ghost btn-sm ${darkMode ? 'text-slate-300 hover:text-white' : ''}`}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>

        {/* Notifications */}
        <button className={`btn-ghost btn-sm relative ${darkMode ? 'text-slate-300 hover:text-white' : ''}`}>
          🔔
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">3</span>
        </button>

        {/* Health status */}
        {health && (
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
            darkMode ? 'bg-emerald-900/30' : 'bg-emerald-50'
          }`}>
            <span className="status-active" />
            <span className={`text-xs font-medium ${darkMode ? 'text-emerald-400' : 'text-emerald-700'}`}>
              v{health.version}
            </span>
          </div>
        )}

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className={`w-8 h-8 rounded-full flex items-center justify-center font-medium text-sm transition-all ${
              darkMode
                ? 'bg-blue-600 text-white hover:bg-blue-500'
                : 'bg-primary-100 text-primary-700 hover:bg-primary-200'
            }`}
          >
            U
          </button>

          {showMenu && (
            <div className={`absolute right-0 top-full mt-2 w-48 rounded-xl shadow-lg border py-1 z-50 ${
              darkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-surface-200'
            }`}>
              <button className={`w-full text-left px-4 py-2 text-sm ${
                darkMode ? 'text-slate-300 hover:bg-slate-700' : 'text-surface-700 hover:bg-surface-50'
              }`}>
                👤 Profile
              </button>
              <button className={`w-full text-left px-4 py-2 text-sm ${
                darkMode ? 'text-slate-300 hover:bg-slate-700' : 'text-surface-700 hover:bg-surface-50'
              }`}>
                ⚙️ Settings
              </button>
              <hr className={`my-1 ${darkMode ? 'border-slate-700' : 'border-surface-100'}`} />
              <button
                onClick={onLogout}
                className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                🚪 Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
