type Page = 'dashboard' | 'content' | 'voice' | 'video' | 'sound' | 'shop';

interface Props {
  page: Page;
  setPage: (page: Page) => void;
  open: boolean;
  onToggle: () => void;
}

const navItems: { id: Page; icon: string; label: string; desc: string }[] = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard', desc: 'Overview & analytics' },
  { id: 'content', icon: '✍️', label: 'Content Factory', desc: 'AI script generation' },
  { id: 'voice', icon: '🎙️', label: 'Voice Studio', desc: 'Text-to-speech' },
  { id: 'video', icon: '🎬', label: 'Video Editor', desc: 'Edit & export' },
  { id: 'sound', icon: '🎵', label: 'Sound Lab', desc: 'Trending & AI music' },
  { id: 'shop', icon: '🛒', label: 'TikTok Shop', desc: 'Products & sales' },
];

export function Sidebar({ page, setPage, open, onToggle }: Props) {
  return (
    <aside className={`${open ? 'w-64' : 'w-20'} bg-white border-r border-surface-200 flex flex-col transition-all duration-300 ease-in-out`}>
      <div className="p-4 flex items-center justify-between border-b border-surface-100">
        {open && <span className="text-sm font-semibold text-surface-500">Navigation</span>}
        <button onClick={onToggle} className="btn-ghost btn-sm">
          {open ? '←' : '→'}
        </button>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition-all duration-200 ${
              page === item.id
                ? 'bg-primary-50 text-primary-700 font-medium shadow-sm'
                : 'text-surface-600 hover:bg-surface-50 hover:text-surface-900'
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            {open && (
              <div className="text-left">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs text-surface-400">{item.desc}</div>
              </div>
            )}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-surface-100">
        {open && (
          <div className="bg-primary-50 rounded-xl p-3">
            <p className="text-xs font-medium text-primary-700">💡 Pro Tip</p>
            <p className="text-xs text-primary-600 mt-1">Use AI to generate scripts first, then add voice and video!</p>
          </div>
        )}
      </div>
    </aside>
  );
}
