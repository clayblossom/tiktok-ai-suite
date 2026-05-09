import { useState } from 'react';
import { api } from '../api';

interface Script {
  id?: number;
  topic: string;
  niche: string;
  tone: string;
  duration: number;
  content_type: string;
  variations: { hook: string; body: string; cta: string; engagement_score: number }[];
  hashtags: string[];
  best_posting_time: string;
}

const CONTENT_TYPES = [
  { value: 'storytime', label: '📖 Storytime', desc: 'Personal stories with hooks' },
  { value: 'tutorial', label: '📚 Tutorial', desc: 'Step-by-step guides' },
  { value: 'did_you_know', label: '🧠 Did You Know', desc: 'Facts & trivia' },
  { value: 'pov', label: '👁️ POV', desc: 'Point of view scenarios' },
  { value: 'ranking', label: '🏆 Ranking', desc: 'Tier lists & rankings' },
  { value: 'before_after', label: '🔄 Before/After', desc: 'Transformations' },
  { value: 'things_that', label: '📋 Things That...', desc: 'Relatable lists' },
  { value: 'custom', label: '✨ Custom', desc: 'Your own format' },
];

const TONES = ['casual', 'professional', 'funny', 'dramatic', 'educational', 'motivational'];
const NICHES = ['tech', 'fitness', 'food', 'beauty', 'comedy', 'education', 'music', 'fashion', 'travel'];

export function ContentFactory() {
  const [topic, setTopic] = useState('');
  const [niche, setNiche] = useState('');
  const [tone, setTone] = useState('casual');
  const [duration, setDuration] = useState(30);
  const [contentType, setContentType] = useState('storytime');
  const [variations, setVariations] = useState(2);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Script | null>(null);
  const [activeTab, setActiveTab] = useState<'generate' | 'history' | 'templates'>('generate');

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    try {
      const data = await api.generateScript({
        topic, niche, tone, duration,
        content_type: contentType,
        variations,
        language: 'en',
      });
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900">Content Factory</h1>
          <p className="text-sm text-surface-500 mt-1">AI-powered TikTok script generation</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('generate')}
            className={`btn-sm ${activeTab === 'generate' ? 'btn-primary' : 'btn-ghost'}`}
          >
            ✍️ Generate
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`btn-sm ${activeTab === 'history' ? 'btn-primary' : 'btn-ghost'}`}
          >
            📜 History
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`btn-sm ${activeTab === 'templates' ? 'btn-primary' : 'btn-ghost'}`}
          >
            📋 Templates
          </button>
        </div>
      </div>

      {activeTab === 'generate' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input form */}
          <div className="lg:col-span-1 card space-y-4">
            <h3 className="font-semibold text-surface-900">Script Settings</h3>

            <div>
              <label className="label">Topic *</label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                className="input"
                placeholder="e.g., AI trends, morning routine, cooking hacks"
              />
            </div>

            <div>
              <label className="label">Content Type</label>
              <div className="grid grid-cols-2 gap-2">
                {CONTENT_TYPES.slice(0, 4).map(ct => (
                  <button
                    key={ct.value}
                    onClick={() => setContentType(ct.value)}
                    className={`p-2 rounded-lg border text-left text-xs transition-all ${
                      contentType === ct.value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-surface-200 hover:border-surface-300'
                    }`}
                  >
                    <span className="font-medium">{ct.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="label">Niche</label>
              <select value={niche} onChange={e => setNiche(e.target.value)} className="select">
                <option value="">Select niche...</option>
                {NICHES.map(n => (
                  <option key={n} value={n}>{n.charAt(0).toUpperCase() + n.slice(1)}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="label">Tone</label>
              <div className="flex flex-wrap gap-2">
                {TONES.map(t => (
                  <button
                    key={t}
                    onClick={() => setTone(t)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                      tone === t
                        ? 'bg-primary-600 text-white'
                        : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="label">Duration: {duration}s</label>
              <input
                type="range"
                min={15}
                max={180}
                step={15}
                value={duration}
                onChange={e => setDuration(Number(e.target.value))}
                className="w-full accent-primary-600"
              />
              <div className="flex justify-between text-xs text-surface-400">
                <span>15s</span>
                <span>60s</span>
                <span>180s</span>
              </div>
            </div>

            <div>
              <label className="label">Variations: {variations}</label>
              <input
                type="range"
                min={1}
                max={5}
                value={variations}
                onChange={e => setVariations(Number(e.target.value))}
                className="w-full accent-primary-600"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
              className="btn-primary w-full"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                <>🚀 Generate Script</>
              )}
            </button>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 space-y-4">
            {result ? (
              <>
                {/* Meta info */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-surface-900">Generated Script</h3>
                    <div className="flex items-center gap-2">
                      <span className="badge-primary">{result.content_type}</span>
                      <span className="badge-info">{result.duration}s</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.hashtags.map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-surface-100 rounded-full text-xs text-surface-600">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-surface-400 mt-2">
                    📅 Best posting time: {result.best_posting_time}
                  </p>
                </div>

                {/* Variations */}
                {result.variations.map((v, i) => (
                  <div key={i} className="card-hover">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-surface-800">Variation {i + 1}</h4>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-surface-400">Engagement Score</span>
                        <span className={`badge ${
                          v.engagement_score >= 80 ? 'badge-success' :
                          v.engagement_score >= 60 ? 'badge-warning' : 'badge-danger'
                        }`}>
                          {v.engagement_score}%
                        </span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                        <p className="text-xs font-medium text-blue-700 mb-1">🪝 Hook</p>
                        <p className="text-sm text-blue-900">{v.hook}</p>
                      </div>
                      <div className="p-3 bg-surface-50 rounded-lg">
                        <p className="text-xs font-medium text-surface-500 mb-1">📝 Body</p>
                        <p className="text-sm text-surface-700">{v.body}</p>
                      </div>
                      <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                        <p className="text-xs font-medium text-emerald-700 mb-1">📢 Call to Action</p>
                        <p className="text-sm text-emerald-900">{v.cta}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-3">
                      <button className="btn-ghost btn-sm">📋 Copy</button>
                      <button className="btn-ghost btn-sm">🎙️ Add Voice</button>
                      <button className="btn-ghost btn-sm">🎬 Create Video</button>
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <div className="card flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                  <div className="text-6xl mb-4">✍️</div>
                  <h3 className="text-lg font-semibold text-surface-700">Ready to Create</h3>
                  <p className="text-sm text-surface-400 mt-1">
                    Fill in the settings and click Generate to create AI-powered TikTok scripts
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="card">
          <div className="text-center py-12">
            <div className="text-5xl mb-4">📜</div>
            <h3 className="text-lg font-semibold text-surface-700">Script History</h3>
            <p className="text-sm text-surface-400 mt-1">Your previously generated scripts will appear here</p>
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {CONTENT_TYPES.map(ct => (
            <div key={ct.value} className="card-hover cursor-pointer group">
              <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">
                {ct.label.split(' ')[0]}
              </div>
              <h4 className="font-semibold text-surface-800">{ct.label.split(' ').slice(1).join(' ')}</h4>
              <p className="text-xs text-surface-400 mt-1">{ct.desc}</p>
              <button className="btn-ghost btn-sm mt-3 w-full">Use Template</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
