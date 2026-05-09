type Page = 'dashboard' | 'content' | 'voice' | 'video' | 'sound' | 'shop';

interface Props {
  page: Page;
  setPage: (page: Page) => void;
  open: boolean;
  onToggle: () => void;
  darkMode: boolean;
}

const navItems: { id: Page; icon: string; label: string; desc: string }[] = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard', desc: 'Overview & analytics' },
  { id: 'content', icon: '✍️', label: 'Content Factory', desc: 'AI script generation' },
  { id: 'voice', icon: '🎙️', label: 'Voice Studio', desc: 'Text-to-speech' },
  { id: 'video', icon: '🎬', label: 'Video Editor', desc: 'Edit & export' },
  { id: 'sound', icon: '🎵', label: 'Sound Lab', desc: 'Trending & AI music' },
  { id: 'shop', icon: '🛒', label: 'TikTok Shop', desc: 'Products & sales' },
];

export function Sidebar({ page, setPage, open, onToggle, darkMode }: Props) {
  return (
    <aside className={`${open ? 'w-64' : 'w-20'} flex flex-col transition-all duration-300 ease-in-out border-r ${
      darkMode
        ? 'bg-slate-900 border-slate-800'
        : 'bg-white border-surface-200'
    }`}>
      {/* Toggle */}
      <div className={`p-4 flex items-center justify-between border-b ${
        darkMode ? 'border-slate-800' : 'border-surface-100'
      }`}>
        {open && (
          <span className={`text-sm font-semibold ${darkMode ? 'text-slate-400' : 'text-surface-500'}`}>
            Navigation
          </span>
        )}
        <button onClick={onToggle} className={`btn-ghost btn-sm ${darkMode ? 'text-slate-400' : ''}`}>
          {open ? '←' : '→'}
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition-all duration-200 ${
              page === item.id
                ? darkMode
                  ? 'bg-blue-600/20 text-blue-400 font-medium'
                  : 'bg-primary-50 text-primary-700 font-medium shadow-sm'
                : darkMode
                  ? 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  : 'text-surface-600 hover:bg-surface-50 hover:text-surface-900'
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            {open && (
              <div className="text-left">
                <div className="font-medium">{item.label}</div>
                <div className={`text-xs ${darkMode ? 'text-slate-500' : 'text-surface-400'}`}>
                  {item.desc}
                </div>
              </div>
            )}
          </button>
        ))}
      </nav>

      {/* Pro tip */}
      <div className={`p-4 border-t ${darkMode ? 'border-slate-800' : 'border-surface-100'}`}>
        {open && (
          <div className={`rounded-xl p-3 ${
            darkMode ? 'bg-blue-900/20' : 'bg-primary-50'
          }`}>
            <p className={`text-xs font-medium ${darkMode ? 'text-blue-400' : 'text-primary-700'}`}>
              💡 Pro Tip
            </p>
            <p className={`text-xs mt-1 ${darkMode ? 'text-blue-300/60' : 'text-primary-600'}`}>
              Use AI to generate scripts first, then add voice and video!
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
