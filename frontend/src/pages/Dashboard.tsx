import { useState, useEffect } from 'react';
import { api } from '../api';

export function Dashboard() {
  const [overview, setOverview] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: string; text: string }[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    api.overview().then(setOverview).catch(() => {});
    api.activity().then(setActivity).catch(() => {});
  }, []);

  const handleChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', text: msg }]);
    setChatLoading(true);
    try {
      const resp = await api.chat(msg);
      setChatHistory(prev => [...prev, { role: 'assistant', text: resp.reply }]);
    } catch {
      setChatHistory(prev => [...prev, { role: 'assistant', text: 'Error processing request' }]);
    }
    setChatLoading(false);
  };

  const stats = [
    { icon: '📁', label: 'Projects', value: overview?.total_projects || 0, trend: '+12%', color: 'bg-primary-50 text-primary-600' },
    { icon: '✍️', label: 'Scripts', value: overview?.total_scripts || 0, trend: '+8%', color: 'bg-violet-50 text-violet-600' },
    { icon: '🎬', label: 'Videos', value: overview?.total_videos || 0, trend: '+24%', color: 'bg-rose-50 text-rose-600' },
    { icon: '🎙️', label: 'Voiceovers', value: overview?.total_voiceovers || 0, trend: '+15%', color: 'bg-amber-50 text-amber-600' },
    { icon: '🎵', label: 'Sounds', value: overview?.total_sounds || 0, trend: '+6%', color: 'bg-emerald-50 text-emerald-600' },
    { icon: '🛒', label: 'Products', value: overview?.total_products || 0, trend: '+3%', color: 'bg-cyan-50 text-cyan-600' },
  ];

  const weeklyData = [
    { day: 'Mon', scripts: 4, videos: 2, views: 12500 },
    { day: 'Tue', scripts: 6, videos: 3, views: 18200 },
    { day: 'Wed', scripts: 3, videos: 1, views: 9800 },
    { day: 'Thu', scripts: 8, videos: 4, views: 24500 },
    { day: 'Fri', scripts: 5, videos: 2, views: 15600 },
    { day: 'Sat', scripts: 2, videos: 1, views: 8900 },
    { day: 'Sun', scripts: 7, videos: 3, views: 21300 },
  ];
  const maxViews = Math.max(...weeklyData.map(d => d.views));

  const quickActions = [
    { icon: '✍️', label: 'New Script', desc: 'Generate AI script', page: 'content' as Page },
    { icon: '🎙️', label: 'Voice Over', desc: 'Text to speech', page: 'voice' as Page },
    { icon: '🎬', label: 'Edit Video', desc: 'Upload & edit', page: 'video' as Page },
    { icon: '🎵', label: 'Find Sound', desc: 'Trending sounds', page: 'sound' as Page },
    { icon: '📊', label: 'Analytics', desc: 'View reports', page: 'dashboard' as Page },
    { icon: '🛒', label: 'Shop Manager', desc: 'Products & sales', page: 'shop' as Page },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Dashboard</h2>
          <p className="page-subtitle">Welcome back! Here's your content overview.</p>
        </div>
        <button className="btn-primary">
          ⚡ Quick Create
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid-stats">
        {stats.map((stat, i) => (
          <div key={i} className="card-hover group">
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl ${stat.color} flex items-center justify-center text-lg`}>
                {stat.icon}
              </div>
              <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">{stat.trend}</span>
            </div>
            <p className="text-2xl font-bold text-surface-900">{stat.value}</p>
            <p className="text-xs text-surface-500 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Performance Chart */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-surface-900">📈 Weekly Performance</h3>
            <div className="flex gap-4 text-xs">
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-primary-500 rounded-full" /> Scripts</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-violet-500 rounded-full" /> Videos</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 rounded-full" /> Views</span>
            </div>
          </div>
          <div className="space-y-3">
            {weeklyData.map((d, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-surface-500 w-8">{d.day}</span>
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex-1 bg-surface-100 rounded-full h-6 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${(d.views / maxViews) * 100}%` }}>
                      <span className="text-[10px] text-white font-medium">{(d.views / 1000).toFixed(1)}K</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1">
                  <span className="badge-primary text-[10px]">{d.scripts}📝</span>
                  <span className="badge-info text-[10px]">{d.videos}🎬</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Chat */}
        <div className="card flex flex-col h-[420px]">
          <div className="flex items-center gap-2 mb-3 pb-3 border-b border-surface-100">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-violet-500 rounded-lg flex items-center justify-center text-white text-sm">🤖</div>
            <div>
              <h3 className="font-semibold text-surface-900 text-sm">AI Assistant</h3>
              <p className="text-xs text-surface-400">Always ready to help</p>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 mb-3 px-1">
            {chatHistory.length === 0 && (
              <div className="text-center py-8">
                <p className="text-3xl mb-2">💬</p>
                <p className="text-sm text-surface-400">Ask me anything!</p>
                <div className="mt-3 space-y-1">
                  {['Generate a script', 'What\'s trending?', 'Create content plan'].map((q, i) => (
                    <button key={i} onClick={() => { setChatInput(q); }} className="block w-full text-xs text-primary-600 bg-primary-50 rounded-lg px-3 py-1.5 hover:bg-primary-100">
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white rounded-br-md'
                    : 'bg-surface-100 text-surface-800 rounded-bl-md'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex items-center gap-2 text-surface-400 text-sm">
                <div className="flex gap-1"><span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce" /><span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:0.1s]" /><span className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:0.2s]" /></div>
                Thinking...
              </div>
            )}
          </div>
          <div className="flex gap-2 pt-2 border-t border-surface-100">
            <input value={chatInput} onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleChat()}
              placeholder="Ask the AI..." className="input text-sm" />
            <button onClick={handleChat} disabled={chatLoading || !chatInput.trim()} className="btn-primary">➤</button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="font-semibold text-surface-900 mb-4">⚡ Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {quickActions.map((action, i) => (
            <button key={i} className="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-primary-50 transition-colors group">
              <span className="text-2xl group-hover:scale-110 transition-transform">{action.icon}</span>
              <span className="text-sm font-medium text-surface-700">{action.label}</span>
              <span className="text-xs text-surface-400">{action.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="card">
        <h3 className="font-semibold text-surface-900 mb-4">📋 Recent Activity</h3>
        {activity.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-3xl mb-2">📭</p>
            <p className="text-sm text-surface-400">No activity yet. Start creating!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {activity.slice(0, 8).map((a, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface-50 transition-colors">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg ${
                  a.type === 'script' ? 'bg-violet-50' : a.type === 'video' ? 'bg-rose-50' : 'bg-amber-50'
                }`}>
                  {a.type === 'script' ? '✍️' : a.type === 'video' ? '🎬' : '🎵'}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-surface-800">{a.title}</p>
                  <p className="text-xs text-surface-400">{a.action}</p>
                </div>
                <span className="text-xs text-surface-400">{a.timestamp?.split('T')[0]}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

type Page = 'dashboard' | 'content' | 'voice' | 'video' | 'sound' | 'shop';
