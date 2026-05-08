type Page = 'dashboard' | 'content' | 'voice' | 'video' | 'sound' | 'shop';

interface Props {
  page: Page;
  setPage: (page: Page) => void;
  open: boolean;
  onToggle: () => void;
}

const navItems: { id: Page; icon: string; label: string }[] = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard' },
  { id: 'content', icon: '📝', label: 'Content Factory' },
  { id: 'voice', icon: '🎙️', label: 'Voice Studio' },
  { id: 'video', icon: '🎬', label: 'Video Editor' },
  { id: 'sound', icon: '🎵', label: 'Sound Lab' },
  { id: 'shop', icon: '🛒', label: 'TikTok Shop' },
];

export function Sidebar({ page, setPage, open, onToggle }: Props) {
  return (
    <aside className={`${open ? 'w-56' : 'w-16'} bg-tiktok-darker border-r border-gray-800 flex flex-col transition-all duration-300`}>
      <button onClick={onToggle} className="p-4 text-gray-500 hover:text-white text-left">
        {open ? '✕' : '☰'}
      </button>
      <nav className="flex-1 space-y-1 px-2">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              page === item.id
                ? 'bg-tiktok-pink/20 text-tiktok-pink'
                : 'text-gray-400 hover:text-white hover:bg-tiktok-gray'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {open && <span>{item.label}</span>}
          </button>
        ))}
      </nav>
      <div className="p-3 border-t border-gray-800">
        {open && <p className="text-xs text-gray-600 text-center">TikTok AI Suite v0.1</p>}
      </div>
    </aside>
  );
}
