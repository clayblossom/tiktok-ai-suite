import { useEffect, useState } from 'react';
import { api } from '../api';

export function Header() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
  }, []);

  return (
    <header className="bg-tiktok-darker border-b border-gray-800 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <span className="text-tiktok-pink text-2xl font-bold">T</span>
          <span className="text-tiktok-blue text-2xl font-bold">T</span>
        </div>
        <div>
          <h1 className="text-lg font-bold">TikTok AI Creator Suite</h1>
          <p className="text-xs text-gray-500">All-in-one AI content platform</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        {health && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-gray-500">v{health.version} • {Math.floor(health.uptime_seconds / 60)}m</span>
          </div>
        )}
      </div>
    </header>
  );
}
