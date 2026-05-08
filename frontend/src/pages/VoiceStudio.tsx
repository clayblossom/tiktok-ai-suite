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

  useEffect(() => {
    api.listVoices().then(setVoices).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!text.trim()) return;
    setGenerating(true);
    try {
      const resp = await api.generateVoice({ text, voice_id: voiceId, language, speed });
      setResult(resp);
    } catch (err) {
      console.error(err);
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">🎙️ Voice Studio</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <h3 className="font-semibold">🔊 Text-to-Speech</h3>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Text</label>
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Enter text to convert to speech..."
              rows={6}
              className="input-field resize-none"
            />
            <p className="text-xs text-gray-600 mt-1">{text.length} characters</p>
          </div>

          <div>
            <label className="text-xs text-gray-400 block mb-1">Voice</label>
            <select value={voiceId} onChange={e => setVoiceId(e.target.value)} className="input-field">
              {voices.map(v => (
                <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Language</label>
              <select value={language} onChange={e => setLanguage(e.target.value)} className="input-field">
                <option value="en">English</option>
                <option value="id">Indonesian</option>
                <option value="ja">Japanese</option>
                <option value="ko">Korean</option>
                <option value="zh">Chinese</option>
                <option value="es">Spanish</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Speed: {speed}x</label>
              <input type="range" min={0.5} max={2} step={0.1} value={speed}
                onChange={e => setSpeed(Number(e.target.value))} className="w-full accent-tiktok-pink" />
            </div>
          </div>

          <button onClick={handleGenerate} disabled={generating || !text.trim()} className="btn-primary w-full">
            {generating ? '⏳ Generating...' : '🎙️ Generate Voice'}
          </button>
        </div>

        <div className="space-y-4">
          {result ? (
            <div className="card">
              <h3 className="font-semibold mb-3">🔊 Generated Audio</h3>
              <div className="bg-tiktok-darker rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-2">Voice: {result.voice_name}</p>
                <p className="text-sm text-gray-400 mb-3">Duration: ~{result.duration_sec?.toFixed(1)}s</p>
                <audio controls className="w-full">
                  <source src={`/api/voice/file/${result.id}`} />
                </audio>
                <p className="text-xs text-gray-600 mt-2">File: {result.file_path}</p>
              </div>
            </div>
          ) : (
            <div className="card text-center py-16">
              <p className="text-4xl mb-3">🎙️</p>
              <p className="text-gray-500">Enter text and generate voiceover!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
