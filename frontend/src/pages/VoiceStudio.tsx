import { useState, useEffect } from 'react';
import { api } from '../api';

export function VoiceStudio() {
  const [text, setText] = useState('');
  const [voiceId, setVoiceId] = useState('alloy');
  const [language, setLanguage] = useState('en');
  const [speed, setSpeed] = useState(1.0);
  const [voices, setVoices] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => { api.listVoices().then(setVoices).catch(() => {}); }, []);

  const handleGenerate = async () => {
    if (!text.trim()) return;
    setGenerating(true);
    try {
      const resp = await api.generateVoice({ text, voice_id: voiceId, language, speed });
      setResult(resp);
      setHistory(prev => [resp, ...prev]);
    } catch (err) { console.error(err); }
    setGenerating(false);
  };

  const presets = [
    { label: 'TikTok Narrator', voice: 'nova', speed: 1.1, lang: 'en' },
    { label: 'Whisper ASMR', voice: 'shimmer', speed: 0.8, lang: 'en' },
    { label: 'Energetic', voice: 'echo', speed: 1.3, lang: 'en' },
    { label: 'Calm Storyteller', voice: 'fable', speed: 0.9, lang: 'en' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">🎙️ Voice Studio</h2>
          <p className="page-subtitle">Generate professional voiceovers with AI</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-5">
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-violet-100 rounded-lg flex items-center justify-center text-violet-600">🔊</div>
              <h3 className="font-semibold text-surface-900">Text-to-Speech</h3>
            </div>

            <div className="mb-4">
              <label className="label">Text</label>
              <textarea value={text} onChange={e => setText(e.target.value)}
                placeholder="Enter text to convert to speech...&#10;&#10;Tip: Use punctuation for natural pauses. Add ! for excitement, ? for questions."
                rows={6} className="textarea" />
              <div className="flex justify-between mt-1">
                <span className="text-xs text-surface-400">{text.length} characters</span>
                <span className="text-xs text-surface-400">~{(text.length * 0.05).toFixed(1)}s estimated</span>
              </div>
            </div>

            <div className="mb-4">
              <label className="label">Voice Presets</label>
              <div className="grid grid-cols-2 gap-2">
                {presets.map((p, i) => (
                  <button key={i} onClick={() => { setVoiceId(p.voice); setSpeed(p.speed); setLanguage(p.lang); }}
                    className="flex items-center gap-2 p-2.5 rounded-lg bg-surface-50 hover:bg-primary-50 text-xs transition-all">
                    <span className="text-lg">{i === 0 ? '🎤' : i === 1 ? '🤫' : i === 2 ? '⚡' : '🧘'}</span>
                    <span className="font-medium text-surface-700">{p.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="label">Voice</label>
                <select value={voiceId} onChange={e => setVoiceId(e.target.value)} className="select">
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Language</label>
                <select value={language} onChange={e => setLanguage(e.target.value)} className="select">
                  <option value="en">🇺🇸 English</option>
                  <option value="id">🇮🇩 Indonesian</option>
                  <option value="ja">🇯🇵 Japanese</option>
                  <option value="ko">🇰🇷 Korean</option>
                  <option value="zh">🇨🇳 Chinese</option>
                  <option value="es">🇪🇸 Spanish</option>
                </select>
              </div>
            </div>

            <div className="mb-4">
              <label className="label">Speed: {speed.toFixed(1)}x</label>
              <input type="range" min={0.5} max={2} step={0.1} value={speed}
                onChange={e => setSpeed(Number(e.target.value))} className="w-full accent-primary-600" />
              <div className="flex justify-between text-xs text-surface-400"><span>0.5x Slow</span><span>1.0x Normal</span><span>2.0x Fast</span></div>
            </div>

            <button onClick={handleGenerate} disabled={generating || !text.trim()} className="btn-primary w-full btn-lg">
              {generating ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</span> : '🎙️ Generate Voice'}
            </button>
          </div>
        </div>

        <div className="space-y-5">
          {result ? (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600">🔊</div>
                <h3 className="font-semibold text-surface-900">Generated Audio</h3>
              </div>
              <div className="bg-surface-50 rounded-xl p-6 text-center">
                <div className="flex justify-center gap-1 mb-4">
                  {Array.from({length: 20}, (_, i) => (
                    <div key={i} className="w-1.5 bg-primary-400 rounded-full animate-pulse"
                      style={{height: `${10 + Math.random() * 30}px`, animationDelay: `${i * 0.05}s`}} />
                  ))}
                </div>
                <audio controls className="w-full mb-3">
                  <source src={`/api/voice/file/${result.id}`} />
                </audio>
                <div className="flex justify-center gap-4 text-xs text-surface-500">
                  <span>🎙️ {result.voice_name}</span>
                  <span>⏱️ ~{result.duration_sec?.toFixed(1)}s</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="card text-center py-16">
              <div className="text-5xl mb-4">🎙️</div>
              <h3 className="text-lg font-semibold text-surface-800 mb-2">Generate Your Voiceover</h3>
              <p className="text-sm text-surface-400">Enter text and choose a voice to get started</p>
            </div>
          )}

          {history.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-surface-900 mb-3">📁 Generated ({history.length})</h3>
              <div className="space-y-2">
                {history.slice(0, 5).map((h, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-surface-50">
                    <span className="text-sm text-surface-700 truncate flex-1">{h.voice_name}</span>
                    <span className="text-xs text-surface-400">{h.duration_sec?.toFixed(1)}s</span>
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
