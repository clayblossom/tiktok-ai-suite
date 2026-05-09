import { useState, useEffect } from 'react';
import { api } from '../api';

interface StatCard {
  label: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: string;
  color: string;
}

interface Activity {
  id: number;
  type: string;
  title: string;
  time: string;
  icon: string;
  status: 'success' | 'pending' | 'error';
}

export function Dashboard() {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard().then(setOverview).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const stats: StatCard[] = [
    { label: 'Total Scripts', value: overview?.total_scripts ?? 0, change: '+12%', trend: 'up', icon: '✍️', color: 'from-blue-500 to-blue-600' },
    { label: 'Videos Created', value: overview?.total_videos ?? 0, change: '+8%', trend: 'up', icon: '🎬', color: 'from-purple-500 to-purple-600' },
    { label: 'Voice Clips', value: overview?.total_sounds ?? 0, change: '+23%', trend: 'up', icon: '🎙️', color: 'from-pink-500 to-pink-600' },
    { label: 'Products', value: overview?.total_products ?? 0, change: '+5%', trend: 'up', icon: '🛒', color: 'from-emerald-500 to-emerald-600' },
    { label: 'API Cost Today', value: `$${overview?.api_cost_today?.toFixed(2) ?? '0.00'}`, change: '-15%', trend: 'down', icon: '💰', color: 'from-amber-500 to-amber-600' },
    { label: 'Projects', value: overview?.total_projects ?? 0, change: '+2', trend: 'up', icon: '📁', color: 'from-cyan-500 to-cyan-600' },
  ];

  const activities: Activity[] = [
    { id: 1, type: 'script', title: 'Generated "AI Trends 2026" script', time: '2 min ago', icon: '✍️', status: 'success' },
    { id: 2, type: 'voice', title: 'Voice clip rendered (ElevenLabs)', time: '15 min ago', icon: '🎙️', status: 'success' },
    { id: 3, type: 'video', title: 'Video export queued', time: '1 hour ago', icon: '🎬', status: 'pending' },
    { id: 4, type: 'shop', title: 'Product listing updated', time: '3 hours ago', icon: '🛒', status: 'success' },
    { id: 5, type: 'sound', title: 'AI music generation failed', time: '5 hours ago', icon: '🎵', status: 'error' },
  ];

  const quickActions = [
    { label: 'Generate Script', desc: 'AI-powered TikTok scripts', icon: '✍️', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', action: 'content' },
    { label: 'Create Voice', desc: 'Text-to-speech with AI', icon: '🎙️', color: 'bg-purple-500/10 text-purple-400 border-purple-500/20', action: 'voice' },
    { label: 'Edit Video', desc: 'AI video editing tools', icon: '🎬', color: 'bg-pink-500/10 text-pink-400 border-pink-500/20', action: 'video' },
    { label: 'Browse Shop', desc: 'TikTok Shop manager', icon: '🛒', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20', action: 'shop' },
  ];

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-surface-200 rounded w-48" />
        <div className="grid grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-32 bg-surface-200 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900">Dashboard</h1>
          <p className="text-sm text-surface-500 mt-1">Welcome back! Here's what's happening with your content.</p>
        </div>
        <div className="flex items-center gap-3">
          <select className="select text-sm py-2">
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>This month</option>
          </select>
          <button className="btn-primary btn-sm">
            <span>📊</span> Export Report
          </button>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat, i) => (
          <div key={i} className="card-hover group cursor-pointer">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center text-white text-lg shadow-lg group-hover:scale-110 transition-transform`}>
                {stat.icon}
              </div>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                stat.trend === 'up' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
              }`}>
                {stat.change}
              </span>
            </div>
            <p className="text-2xl font-bold text-surface-900">{stat.value}</p>
            <p className="text-xs text-surface-500 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity feed */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-surface-900">Recent Activity</h3>
            <button className="btn-ghost btn-sm text-xs">View All</button>
          </div>
          <div className="space-y-3">
            {activities.map(activity => (
              <div key={activity.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-50 transition-colors group">
                <div className="w-10 h-10 rounded-xl bg-surface-100 flex items-center justify-center text-lg group-hover:scale-110 transition-transform">
                  {activity.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-800 truncate">{activity.title}</p>
                  <p className="text-xs text-surface-400">{activity.time}</p>
                </div>
                <span className={`badge ${
                  activity.status === 'success' ? 'badge-success' :
                  activity.status === 'pending' ? 'badge-warning' : 'badge-danger'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick actions */}
        <div className="card">
          <h3 className="font-semibold text-surface-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {quickActions.map((action, i) => (
              <button
                key={i}
                className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-all duration-200 hover:scale-[1.02] ${action.color}`}
              >
                <span className="text-2xl">{action.icon}</span>
                <div className="text-left">
                  <p className="text-sm font-medium">{action.label}</p>
                  <p className="text-xs opacity-60">{action.desc}</p>
                </div>
                <span className="ml-auto opacity-40">→</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Performance chart placeholder */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-surface-900">Content Performance</h3>
          <div className="flex items-center gap-2">
            <button className="btn-ghost btn-sm text-xs">Scripts</button>
            <button className="btn-ghost btn-sm text-xs">Videos</button>
            <button className="btn-ghost btn-sm text-xs">Engagement</button>
          </div>
        </div>
        {/* Simulated chart */}
        <div className="h-48 flex items-end gap-2 px-4">
          {[65, 45, 80, 55, 70, 90, 60, 75, 85, 50, 95, 70].map((h, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-lg transition-all duration-500 hover:from-blue-400 hover:to-blue-300 cursor-pointer"
                style={{ height: `${h}%` }}
              />
              <span className="text-[10px] text-surface-400">
                {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* API usage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-surface-900 mb-4">API Usage Today</h3>
          <div className="space-y-3">
            {[
              { name: 'OpenAI', cost: 2.45, limit: 5, color: 'bg-emerald-500' },
              { name: 'ElevenLabs', cost: 1.20, limit: 3, color: 'bg-purple-500' },
              { name: 'Replicate', cost: 0.80, limit: 2, color: 'bg-blue-500' },
              { name: 'Suno', cost: 0.50, limit: 1, color: 'bg-pink-500' },
            ].map((api, i) => (
              <div key={i}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium text-surface-700">{api.name}</span>
                  <span className="text-surface-500">${api.cost.toFixed(2)} / ${api.limit}</span>
                </div>
                <div className="progress-bar">
                  <div className={`progress-fill ${api.color}`} style={{ width: `${(api.cost / api.limit) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-surface-900 mb-4">System Status</h3>
          <div className="space-y-3">
            {[
              { name: 'API Server', status: 'online', latency: '45ms' },
              { name: 'Database', status: 'online', latency: '12ms' },
              { name: 'AI Connectors', status: 'online', latency: '230ms' },
              { name: 'Storage', status: 'online', latency: '8ms' },
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-surface-50">
                <div className="flex items-center gap-3">
                  <span className="status-active" />
                  <span className="text-sm font-medium text-surface-700">{service.name}</span>
                </div>
                <span className="text-xs text-surface-400">{service.latency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
