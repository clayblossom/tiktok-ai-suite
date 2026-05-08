const API_BASE = '/api';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export const api = {
  // Health
  health: () => fetchJson<any>('/health'),

  // Dashboard
  overview: () => fetchJson<any>('/dashboard/overview'),
  calendar: (month?: string) => fetchJson<any>(`/dashboard/calendar${month ? `?month=${month}` : ''}`),
  activity: () => fetchJson<any[]>('/dashboard/activity'),
  chat: (message: string) => fetchJson<any>('/dashboard/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }),

  // Content Factory
  generateScript: (data: any) => fetchJson<any>('/content/scripts/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  listScripts: () => fetchJson<any[]>('/content/scripts'),
  getScript: (id: number) => fetchJson<any>(`/content/scripts/${id}`),
  generateCaptions: (data: any) => fetchJson<any>('/content/captions/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  contentTemplates: () => fetchJson<any[]>('/content/templates'),

  // Voice
  generateVoice: (data: any) => fetchJson<any>('/voice/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  listVoices: () => fetchJson<any[]>('/voice/voices'),

  // Video
  listVideos: () => fetchJson<any[]>('/videos'),
  getVideo: (id: number) => fetchJson<any>(`/videos/${id}`),
  autoCut: (id: number, data: any) => fetchJson<any>(`/videos/${id}/auto-cut`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  addCaptions: (id: number, data: any) => fetchJson<any>(`/videos/${id}/captions`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  exportVideo: (id: number, data: any) => fetchJson<any>(`/videos/${id}/export`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  videoTemplates: () => fetchJson<any[]>('/videos/templates'),

  // Sound
  trendingSounds: () => fetchJson<any[]>('/sounds/trending'),
  generateMusic: (data: any) => fetchJson<any>('/sounds/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  soundLibrary: () => fetchJson<any[]>('/sounds/library'),

  // Shop
  listProducts: () => fetchJson<any[]>('/shop/products'),
  createProduct: (data: any) => fetchJson<any>('/shop/products', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  researchProducts: (category?: string) => fetchJson<any>('/shop/products/research', {
    method: 'POST',
    body: JSON.stringify({ category }),
  }),
  generateListing: (data: any) => fetchJson<any>('/shop/listings/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  shopAnalytics: () => fetchJson<any>('/shop/analytics'),
};
