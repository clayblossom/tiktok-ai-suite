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

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">📊 Dashboard</h2>

      {/* Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard icon="📁" label="Projects" value={overview.total_projects} />
          <StatCard icon="📝" label="Scripts" value={overview.total_scripts} />
          <StatCard icon="🎬" label="Videos" value={overview.total_videos} />
          <StatCard icon="🎙️" label="Voiceovers" value={overview.total_voiceovers} />
          <StatCard icon="🎵" label="Sounds" value={overview.total_sounds} />
          <StatCard icon="🛒" label="Products" value={overview.total_products} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Feed */}
        <div className="lg:col-span-2 card">
          <h3 className="font-semibold mb-3">📋 Recent Activity</h3>
          {activity.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">No activity yet. Start creating!</p>
          ) : (
            <div className="space-y-2">
              {activity.map((a, i) => (
                <div key={i} className="flex items-center gap-3 bg-tiktok-darker rounded-lg px-3 py-2">
                  <span>{a.type === 'script' ? '📝' : a.type === 'video' ? '🎬' : '🎵'}</span>
                  <div>
                    <p className="text-sm">{a.title}</p>
                    <p className="text-xs text-gray-500">{a.action} • {a.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Chat */}
        <div className="card flex flex-col h-[400px]">
          <h3 className="font-semibold mb-3">🤖 AI Assistant</h3>
          <div className="flex-1 overflow-y-auto space-y-2 mb-3">
            {chatHistory.length === 0 && (
              <p className="text-gray-500 text-sm text-center mt-8">Ask me anything about TikTok content!</p>
            )}
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
                  msg.role === 'user' ? 'bg-tiktok-pink text-white' : 'bg-tiktok-gray text-gray-200'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {chatLoading && <p className="text-gray-500 text-sm animate-pulse">Thinking...</p>}
          </div>
          <div className="flex gap-2">
            <input
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleChat()}
              placeholder="Ask the AI..."
              className="input-field flex-1"
            />
            <button onClick={handleChat} className="btn-primary">➤</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: number }) {
  return (
    <div className="card text-center">
      <p className="text-2xl mb-1">{icon}</p>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
