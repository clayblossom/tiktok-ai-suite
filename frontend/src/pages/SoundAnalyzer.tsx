import { useState, useEffect } from 'react';
import { api } from '../api';

export function SoundAnalyzer() {
  const [trending, setTrending] = useState<any[]>([]);
  const [genre, setGenre] = useState('pop');
  const [mood, setMood] = useState('upbeat');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    api.trendingSounds().then(setTrending).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generateMusic({
        prompt: `${mood} ${genre} music for TikTok`,
        genre, mood, duration: 30, bpm: 120, instrumental: true,
      });
    } catch (err) {
      console.error(err);
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">🎵 Sound Lab</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trending Sounds */}
        <div className="lg:col-span-2 card">
          <h3 className="font-semibold mb-3">🔥 Trending Sounds</h3>
          <div className="space-y-2">
            {trending.map(s => (
              <div key={s.id} className="bg-tiktok-darker rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎵</span>
                  <div>
                    <p className="text-sm font-medium">{s.title}</p>
                    <p className="text-xs text-gray-500">{s.artist} • {s.category}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-tiktok-pink">{s.viral_score}/100</p>
                  <p className="text-xs text-gray-500">{(s.usage_count / 1000000).toFixed(1)}M uses</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Music Generator */}
        <div className="card space-y-4">
          <h3 className="font-semibold">🎹 AI Music Generator</h3>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Genre</label>
            <select value={genre} onChange={e => setGenre(e.target.value)} className="input-field">
              <option value="pop">Pop</option>
              <option value="hip-hop">Hip-Hop</option>
              <option value="electronic">Electronic</option>
              <option value="lo-fi">Lo-Fi</option>
              <option value="cinematic">Cinematic</option>
              <option value="ambient">Ambient</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Mood</label>
            <select value={mood} onChange={e => setMood(e.target.value)} className="input-field">
              <option value="upbeat">Upbeat 🔥</option>
              <option value="chill">Chill 😌</option>
              <option value="dramatic">Dramatic 🎭</option>
              <option value="funny">Funny 😂</option>
              <option value="motivational">Motivational 💪</option>
            </select>
          </div>

          <button onClick={handleGenerate} disabled={generating} className="btn-teal w-full">
            {generating ? '⏳ Generating...' : '🎹 Generate Music'}
          </button>
        </div>
      </div>
    </div>
  );
}
