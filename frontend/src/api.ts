const API_BASE = '/api';

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });

  if (resp.status === 401) {
    // Token expired, try refresh
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
      const retryResp = await fetch(`${API_BASE}${path}`, { headers, ...options });
      if (!retryResp.ok) throw new Error(`API error: ${retryResp.status}`);
      return retryResp.json();
    }
    // Redirect to login
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.reload();
    throw new Error('Session expired');
  }

  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  try {
    const resp = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!resp.ok) return false;
    const data = await resp.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export const api = {
  // Auth
  login: (email: string, password: string) => fetchJson<any>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }),
  register: (email: string, password: string, display_name: string) => fetchJson<any>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, display_name }),
  }),

  // Health
  health: () => fetchJson<any>('/health'),

  // Dashboard
  dashboard: () => fetchJson<any>('/dashboard/overview'),
  calendar: (month?: string) => fetchJson<any>(`/dashboard/calendar${month ? `?month=${month}` : ''}`),
  activity: () => fetchJson<any[]>('/dashboard/activity'),

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
  contentTemplates: () => fetchJson<any[]>('/content/content-templates'),

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
  generateListing: (data: any) => fetchJson<any>('/shop/listings/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  shopAnalytics: () => fetchJson<any>('/shop/analytics'),
};
