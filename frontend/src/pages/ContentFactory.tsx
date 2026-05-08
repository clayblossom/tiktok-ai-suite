import { useState, useEffect } from 'react';
import { api } from '../api';

export function ContentFactory() {
  const [topic, setTopic] = useState('');
  const [niche, setNiche] = useState('');
  const [tone, setTone] = useState('casual');
  const [duration, setDuration] = useState(30);
  const [contentType, setContentType] = useState('custom');
  const [templates, setTemplates] = useState<any[]>([]);
  const [scripts, setScripts] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    api.contentTemplates().then(setTemplates).catch(() => {});
    api.listScripts().then(setScripts).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setGenerating(true);
    try {
      const resp = await api.generateScript({
        topic, niche, tone, duration,
        content_type: contentType,
        variations: 3,
        language: 'en',
      });
      setResult(resp);
      api.listScripts().then(setScripts);
    } catch (err) {
      console.error(err);
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">📝 Content Factory</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Generator Form */}
        <div className="card space-y-4">
          <h3 className="font-semibold">✨ Script Generator</h3>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Topic *</label>
            <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g. Morning routine" className="input-field" />
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Niche</label>
            <input value={niche} onChange={e => setNiche(e.target.value)} placeholder="e.g. fitness, beauty" className="input-field" />
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Template</label>
            <select value={contentType} onChange={e => setContentType(e.target.value)} className="input-field">
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.icon} {t.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Tone</label>
              <select value={tone} onChange={e => setTone(e.target.value)} className="input-field">
                <option value="funny">😂 Funny</option>
                <option value="educational">📚 Educational</option>
                <option value="dramatic">🎭 Dramatic</option>
                <option value="casual">😎 Casual</option>
                <option value="professional">💼 Professional</option>
                <option value="motivational">💪 Motivational</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Duration</label>
              <select value={duration} onChange={e => setDuration(Number(e.target.value))} className="input-field">
                <option value={15}>15 sec</option>
                <option value={30}>30 sec</option>
                <option value={60}>60 sec</option>
                <option value={180}>3 min</option>
              </select>
            </div>
          </div>

          <button onClick={handleGenerate} disabled={generating || !topic.trim()} className="btn-primary w-full">
            {generating ? '⏳ Generating...' : '✨ Generate Script'}
          </button>
        </div>

        {/* Result */}
        <div className="lg:col-span-2 space-y-4">
          {result ? (
            <>
              <div className="card">
                <h3 className="font-semibold mb-3">📋 Generated Scripts</h3>
                {result.variations?.map((v: any, i: number) => (
                  <div key={i} className="bg-tiktok-darker rounded-lg p-4 mb-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-tiktok-pink">Variation {i + 1}</span>
                      <span className="text-xs text-gray-500">Score: {v.engagement_score}/100</span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div><span className="text-yellow-400 font-medium">Hook:</span> {v.hook}</div>
                      <div><span className="text-blue-400 font-medium">Body:</span> {v.body}</div>
                      <div><span className="text-green-400 font-medium">CTA:</span> {v.cta}</div>
                    </div>
                  </div>
                ))}
              </div>
              {result.hashtags?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold mb-2">🏷️ Hashtags</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.hashtags.map((h: string, i: number) => (
                      <span key={i} className="bg-tiktok-pink/20 text-tiktok-pink px-2 py-1 rounded-full text-xs">{h}</span>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="card text-center py-16">
              <p className="text-4xl mb-3">📝</p>
              <p className="text-gray-500">Enter a topic and generate your first script!</p>
            </div>
          )}

          {/* Previous Scripts */}
          {scripts.length > 0 && (
            <div className="card">
              <h3 className="font-semibold mb-3">📚 Previous Scripts ({scripts.length})</h3>
              <div className="space-y-2">
                {scripts.slice(0, 5).map(s => (
                  <div key={s.id} className="bg-tiktok-darker rounded-lg px-3 py-2 flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium">{s.topic}</p>
                      <p className="text-xs text-gray-500">{s.tone} • {s.duration}s • {s.content_type}</p>
                    </div>
                    <span className="text-xs text-gray-600">{s.created_at?.split('T')[0]}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
