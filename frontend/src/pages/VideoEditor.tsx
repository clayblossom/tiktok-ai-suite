import { useState, useEffect } from 'react';
import { api } from '../api';

export function VideoEditor() {
  const [videos, setVideos] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');

  useEffect(() => {
    api.listVideos().then(setVideos).catch(() => {});
    api.videoTemplates().then(setTemplates).catch(() => {});
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const resp = await fetch('/api/videos/upload', { method: 'POST', body: formData });
      const data = await resp.json();
      setVideos(prev => [data, ...prev]);
    } catch (err) { console.error(err); }
    setUploading(false);
  };

  const tools = [
    { icon: '✂️', name: 'Auto Cut', desc: 'AI-powered pacing', color: 'bg-rose-50 text-rose-600' },
    { icon: '📝', name: 'Captions', desc: 'Auto-generate subs', color: 'bg-primary-50 text-primary-600' },
    { icon: '🎨', name: 'Overlays', desc: 'Text & stickers', color: 'bg-violet-50 text-violet-600' },
    { icon: '🔄', name: 'Transitions', desc: 'Smooth effects', color: 'bg-amber-50 text-amber-600' },
    { icon: '🎵', name: 'Music', desc: 'Background audio', color: 'bg-emerald-50 text-emerald-600' },
    { icon: '📤', name: 'Export', desc: '9:16 TikTok format', color: 'bg-cyan-50 text-cyan-600' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">🎬 Video Editor</h2>
          <p className="page-subtitle">Edit and optimize videos for TikTok</p>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="card">
        <div className="border-2 border-dashed border-surface-300 rounded-2xl p-12 text-center hover:border-primary-400 hover:bg-primary-50/30 transition-all cursor-pointer"
          onDragOver={e => e.preventDefault()}
          onDrop={e => { e.preventDefault(); const file = e.dataTransfer.files[0]; if (file) handleUpload(file); }}
          onClick={() => document.getElementById('video-upload')?.click()}>
          {uploading ? (
            <div>
              <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4" />
              <p className="text-surface-600 font-medium">Uploading...</p>
            </div>
          ) : (
            <>
              <div className="text-5xl mb-4">📹</div>
              <h3 className="text-lg font-semibold text-surface-800 mb-2">Drop your video here</h3>
              <p className="text-sm text-surface-400 mb-4">or click to browse files</p>
              <div className="flex justify-center gap-4 text-xs text-surface-400">
                <span>MP4, MOV, AVI</span>
                <span>•</span>
                <span>Max 500MB</span>
                <span>•</span>
                <span>9:16 recommended</span>
              </div>
            </>
          )}
        </div>
        <input id="video-upload" type="file" accept="video/*" className="hidden" onChange={e => { const f = e.target.files?.[0]; if (f) handleUpload(f); }} />
      </div>

      {/* Tools */}
      <div className="card">
        <h3 className="font-semibold text-surface-900 mb-4">🛠️ Editing Tools</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {tools.map((tool, i) => (
            <button key={i} className="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-surface-50 transition-all group">
              <div className={`w-12 h-12 rounded-xl ${tool.color} flex items-center justify-center text-xl group-hover:scale-110 transition-transform`}>
                {tool.icon}
              </div>
              <span className="text-sm font-medium text-surface-700">{tool.name}</span>
              <span className="text-xs text-surface-400">{tool.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Templates */}
      <div className="card">
        <h3 className="font-semibold text-surface-900 mb-4">🎨 Video Templates</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {templates.map(t => (
            <button key={t.id} onClick={() => setSelectedTemplate(t.id)}
              className={`p-4 rounded-xl text-center transition-all ${
                selectedTemplate === t.id ? 'bg-primary-50 border-2 border-primary-300 shadow-sm' : 'bg-surface-50 border-2 border-transparent hover:bg-surface-100'
              }`}>
              <p className="text-3xl mb-2">{t.icon}</p>
              <p className="text-sm font-medium text-surface-800">{t.name}</p>
              <p className="text-xs text-surface-400 mt-1">{t.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Video List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-surface-900">📁 My Videos ({videos.length})</h3>
        </div>
        {videos.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-5xl mb-4">🎬</div>
            <h3 className="text-lg font-semibold text-surface-800 mb-2">No videos yet</h3>
            <p className="text-sm text-surface-400">Upload your first video to get started!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {videos.map(v => (
              <div key={v.id} className="flex items-center justify-between p-4 rounded-xl bg-surface-50 hover:bg-surface-100 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-surface-200 rounded-xl flex items-center justify-center text-2xl">🎬</div>
                  <div>
                    <p className="font-medium text-surface-800">Video #{v.id}</p>
                    <p className="text-xs text-surface-400">{v.duration_sec?.toFixed(1)}s • {v.resolution} • {v.file_size_mb}MB</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`badge ${v.status === 'done' ? 'badge-success' : v.status === 'error' ? 'badge-danger' : 'badge-warning'}`}>
                    {v.status}
                  </span>
                  <button className="btn-secondary btn-sm">Edit</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
