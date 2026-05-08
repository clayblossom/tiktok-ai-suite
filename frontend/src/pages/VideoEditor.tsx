import { useState, useEffect } from 'react';
import { api } from '../api';

export function VideoEditor() {
  const [videos, setVideos] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);

  useEffect(() => {
    api.listVideos().then(setVideos).catch(() => {});
    api.videoTemplates().then(setTemplates).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">🎬 Video Editor</h2>

      {/* Upload Area */}
      <div className="card">
        <div className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center hover:border-tiktok-pink transition-colors">
          <p className="text-4xl mb-3">📹</p>
          <p className="text-gray-400 mb-2">Drop your video here or click to upload</p>
          <p className="text-xs text-gray-600">Supports MP4, MOV, AVI • Max 500MB • 9:16 recommended</p>
          <label className="btn-primary inline-block mt-4 cursor-pointer">
            📁 Choose File
            <input type="file" accept="video/*" className="hidden" onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              const formData = new FormData();
              formData.append('file', file);
              try {
                const resp = await fetch('/api/videos/upload', { method: 'POST', body: formData });
                const data = await resp.json();
                setVideos(prev => [data, ...prev]);
              } catch (err) {
                console.error(err);
              }
            }} />
          </label>
        </div>
      </div>

      {/* Templates */}
      <div className="card">
        <h3 className="font-semibold mb-3">🎨 Video Templates</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {templates.map(t => (
            <div key={t.id} className="bg-tiktok-darker rounded-lg p-3 text-center hover:bg-tiktok-gray cursor-pointer transition-colors">
              <p className="text-2xl mb-1">{t.icon}</p>
              <p className="text-sm font-medium">{t.name}</p>
              <p className="text-xs text-gray-500">{t.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Video List */}
      <div className="card">
        <h3 className="font-semibold mb-3">📁 My Videos ({videos.length})</h3>
        {videos.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">No videos yet. Upload your first video!</p>
        ) : (
          <div className="space-y-2">
            {videos.map(v => (
              <div key={v.id} className="bg-tiktok-darker rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎬</span>
                  <div>
                    <p className="text-sm font-medium">Video #{v.id}</p>
                    <p className="text-xs text-gray-500">{v.duration_sec?.toFixed(1)}s • {v.resolution} • {v.file_size_mb}MB</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <span className={`badge ${v.status === 'done' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>
                    {v.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
