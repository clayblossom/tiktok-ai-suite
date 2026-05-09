import { useState, useEffect } from 'react';
import { api } from '../api';

export function SoundAnalyzer() {
  const [trending, setTrending] = useState<any[]>([]);
  const [genre, setGenre] = useState('pop');
  const [mood, setMood] = useState('upbeat');
  const [generating, setGenerating] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => { api.trendingSounds().then(setTrending).catch(() => {}); }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generateMusic({ prompt: `${mood} ${genre} music for TikTok`, genre, mood, duration: 30, bpm: 120, instrumental: true });
    } catch (err) { console.error(err); }
    setGenerating(false);
  };

  const categories = ['all', 'pop', 'hip-hop', 'electronic', 'k-pop', 'latin'];
  const filtered = filter === 'all' ? trending : trending.filter(s => s.category === filter);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">🎵 Sound Lab</h2>
          <p className="page-subtitle">Discover trending sounds and create AI music</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-5">
          {/* Trending */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-rose-100 rounded-lg flex items-center justify-center text-rose-600">🔥</div>
                <h3 className="font-semibold text-surface-900">Trending Sounds</h3>
              </div>
              <div className="flex gap-1">
                {categories.map(c => (
                  <button key={c} onClick={() => setFilter(c)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${filter === c ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}>
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Sound</th>
                    <th>Category</th>
                    <th>Uses</th>
                    <th>Viral Score</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((s, i) => (
                    <tr key={s.id}>
                      <td className="font-medium text-surface-400">{i + 1}</td>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-violet-400 rounded-lg flex items-center justify-center text-white">🎵</div>
                          <div>
                            <p className="font-medium text-surface-800">{s.title}</p>
                            <p className="text-xs text-surface-400">{s.artist}</p>
                          </div>
                        </div>
                      </td>
                      <td><span className="badge-info">{s.category}</span></td>
                      <td className="font-medium">{(s.usage_count / 1000000).toFixed(1)}M</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="progress-bar w-20">
                            <div className="progress-fill" style={{width: `${s.viral_score}%`}} />
                          </div>
                          <span className="text-xs font-medium text-surface-600">{s.viral_score}</span>
                        </div>
                      </td>
                      <td><button className="btn-ghost btn-sm">▶️</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Music Generator */}
        <div className="space-y-5">
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600">🎹</div>
              <h3 className="font-semibold text-surface-900">AI Music Generator</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="label">Genre</label>
                <div className="grid grid-cols-2 gap-2">
                  {['pop', 'hip-hop', 'electronic', 'lo-fi', 'cinematic', 'ambient'].map(g => (
                    <button key={g} onClick={() => setGenre(g)}
                      className={`p-2 rounded-lg text-xs font-medium transition-all ${genre === g ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}>
                      {g}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Mood</label>
                <div className="grid grid-cols-2 gap-2">
                  {['upbeat', 'chill', 'dramatic', 'funny', 'motivational', 'romantic'].map(m => (
                    <button key={m} onClick={() => setMood(m)}
                      className={`p-2 rounded-lg text-xs font-medium transition-all ${mood === m ? 'bg-primary-600 text-white' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}>
                      {m === 'upbeat' ? '🔥' : m === 'chill' ? '😌' : m === 'dramatic' ? '🎭' : m === 'funny' ? '😂' : m === 'motivational' ? '💪' : '💕'} {m}
                    </button>
                  ))}
                </div>
              </div>

              <button onClick={handleGenerate} disabled={generating} className="btn-primary w-full">
                {generating ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</span> : '🎹 Generate Music'}
              </button>
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-surface-900 mb-3">💡 Sound Tips</h3>
            <div className="space-y-2 text-xs text-surface-600">
              <p>🎵 Use trending sounds for higher reach</p>
              <p>⏱️ First 3 seconds are crucial</p>
              <p>🔊 Match sound energy to content</p>
              <p>📈 Check viral score before using</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
