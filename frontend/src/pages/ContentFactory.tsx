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
  const [selectedVariation, setSelectedVariation] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.contentTemplates().then(setTemplates).catch(() => {});
    api.listScripts().then(setScripts).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setGenerating(true);
    try {
      const resp = await api.generateScript({ topic, niche, tone, duration, content_type: contentType, variations: 3, language: 'en' });
      setResult(resp);
      setSelectedVariation(0);
      api.listScripts().then(setScripts);
    } catch (err) { console.error(err); }
    setGenerating(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">✍️ Content Factory</h2>
          <p className="page-subtitle">AI-powered TikTok script generation</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Generator Form */}
        <div className="card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600">✨</div>
            <h3 className="font-semibold text-surface-900">Script Generator</h3>
          </div>

          <div>
            <label className="label">Topic *</label>
            <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g. Morning routine for productivity" className="input" />
          </div>

          <div>
            <label className="label">Niche</label>
            <input value={niche} onChange={e => setNiche(e.target.value)} placeholder="e.g. fitness, beauty, tech" className="input" />
          </div>

          <div>
            <label className="label">Template</label>
            <div className="grid grid-cols-2 gap-2">
              {templates.slice(0, 6).map(t => (
                <button key={t.id} onClick={() => setContentType(t.id)}
                  className={`flex items-center gap-2 p-2 rounded-lg text-xs transition-all ${
                    contentType === t.id ? 'bg-primary-50 text-primary-700 border-2 border-primary-300' : 'bg-surface-50 text-surface-600 border-2 border-transparent hover:bg-surface-100'
                  }`}>
                  <span>{t.icon}</span>
                  <span className="font-medium">{t.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Tone</label>
            <div className="flex flex-wrap gap-2">
              {['funny', 'educational', 'dramatic', 'casual', 'professional', 'motivational'].map(t => (
                <button key={t} onClick={() => setTone(t)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                    tone === t ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
                  }`}>
                  {t === 'funny' ? '😂' : t === 'educational' ? '📚' : t === 'dramatic' ? '🎭' : t === 'casual' ? '😎' : t === 'professional' ? '💼' : '💪'} {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Duration: {duration}s</label>
            <input type="range" min={15} max={180} step={15} value={duration}
              onChange={e => setDuration(Number(e.target.value))} className="w-full accent-primary-600" />
            <div className="flex justify-between text-xs text-surface-400 mt-1">
              <span>15s</span><span>30s</span><span>60s</span><span>3min</span>
            </div>
          </div>

          <button onClick={handleGenerate} disabled={generating || !topic.trim()} className="btn-primary w-full btn-lg">
            {generating ? (
              <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</span>
            ) : '✨ Generate Script'}
          </button>
        </div>

        {/* Result */}
        <div className="lg:col-span-2 space-y-5">
          {result ? (
            <>
              {/* Variation Tabs */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-surface-900">📋 Generated Scripts</h3>
                  <span className="badge-success">✓ {result.variations?.length} variations</span>
                </div>

                <div className="flex gap-2 mb-4">
                  {result.variations?.map((_: any, i: number) => (
                    <button key={i} onClick={() => setSelectedVariation(i)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        selectedVariation === i ? 'bg-primary-600 text-white shadow-sm' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
                      }`}>
                      Variation {i + 1}
                    </button>
                  ))}
                </div>

                {result.variations?.[selectedVariation] && (
                  <div className="space-y-4">
                    <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-amber-700 uppercase tracking-wide">🪝 Hook (First 3 seconds)</span>
                        <button onClick={() => copyToClipboard(result.variations[selectedVariation].hook)} className="btn-ghost btn-sm text-amber-600">
                          {copied ? '✓' : '📋'}
                        </button>
                      </div>
                      <p className="text-surface-800 font-medium">{result.variations[selectedVariation].hook}</p>
                    </div>

                    <div className="bg-surface-50 rounded-xl p-4 border border-surface-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-surface-500 uppercase tracking-wide">📝 Body</span>
                        <button onClick={() => copyToClipboard(result.variations[selectedVariation].body)} className="btn-ghost btn-sm">📋</button>
                      </div>
                      <p className="text-surface-700 whitespace-pre-wrap">{result.variations[selectedVariation].body}</p>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-4 border border-emerald-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-emerald-700 uppercase tracking-wide">📢 Call to Action</span>
                        <button onClick={() => copyToClipboard(result.variations[selectedVariation].cta)} className="btn-ghost btn-sm text-emerald-600">📋</button>
                      </div>
                      <p className="text-surface-800 font-medium">{result.variations[selectedVariation].cta}</p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-surface-100">
                      <div className="flex items-center gap-4 text-xs text-surface-500">
                        <span>⏱️ ~{result.variations[selectedVariation].estimated_duration}s</span>
                        <span>📊 Score: {result.variations[selectedVariation].engagement_score}/100</span>
                      </div>
                      <button onClick={() => copyToClipboard(result.variations[selectedVariation].full_text)} className="btn-secondary btn-sm">
                        📋 Copy Full Script
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Hashtags */}
              {result.hashtags?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-surface-900 mb-3">🏷️ Hashtags</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.hashtags.map((h: string, i: number) => (
                      <button key={i} onClick={() => copyToClipboard(h)}
                        className="bg-primary-50 text-primary-700 px-3 py-1.5 rounded-full text-xs font-medium hover:bg-primary-100 transition-colors">
                        {h}
                      </button>
                    ))}
                  </div>
                  {result.best_posting_time && (
                    <p className="text-xs text-surface-500 mt-3">⏰ Best posting time: <strong>{result.best_posting_time}</strong></p>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="card text-center py-16">
              <div className="text-5xl mb-4">✍️</div>
              <h3 className="text-lg font-semibold text-surface-800 mb-2">Create Your First Script</h3>
              <p className="text-sm text-surface-400">Enter a topic and let AI generate engaging TikTok scripts</p>
            </div>
          )}

          {/* Previous Scripts */}
          {scripts.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-surface-900 mb-4">📚 Previous Scripts ({scripts.length})</h3>
              <div className="space-y-2">
                {scripts.slice(0, 8).map(s => (
                  <div key={s.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-50 transition-colors cursor-pointer"
                    onClick={() => { setResult(s); }}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-violet-50 rounded-xl flex items-center justify-center text-violet-600">✍️</div>
                      <div>
                        <p className="text-sm font-medium text-surface-800">{s.topic}</p>
                        <p className="text-xs text-surface-400">{s.tone} • {s.duration}s • {s.content_type}</p>
                      </div>
                    </div>
                    <span className="text-xs text-surface-400">{s.created_at?.split('T')[0]}</span>
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
