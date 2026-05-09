import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

export function Header() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
  }, []);

  return (
    <header className="bg-white border-b border-surface-200 px-6 py-3 flex items-center justify-between sticky top-0 z-50 backdrop-blur-sm bg-white/95">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-glow">
          <span className="text-white text-lg font-bold">T</span>
        </div>
        <div>
          <h1 className="text-lg font-bold text-surface-900">TikTok AI Suite</h1>
          <p className="text-xs text-surface-400">Creator Platform</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="btn-ghost btn-sm relative">
          🔔
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">3</span>
        </button>
        {health && (
          <div className="flex items-center gap-2 bg-emerald-50 px-3 py-1.5 rounded-full">
            <span className="status-active" />
            <span className="text-xs font-medium text-emerald-700">v{health.version}</span>
          </div>
        )}
        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-medium text-sm">
          U
        </div>
      </div>
    </header>
  );
}
