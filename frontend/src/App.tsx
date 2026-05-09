import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { ContentFactory } from './pages/ContentFactory';
import { VoiceStudio } from './pages/VoiceStudio';
import { VideoEditor } from './pages/VideoEditor';
import { SoundAnalyzer } from './pages/SoundAnalyzer';
import { ShopManager } from './pages/ShopManager';
import { GrowthOS } from './pages/GrowthOS';
import { LoginPage } from './pages/LoginPage';

type Page = 'dashboard' | 'growth' | 'content' | 'voice' | 'video' | 'sound' | 'shop';

function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) setAuthenticated(true);

    const savedDark = localStorage.getItem('dark_mode');
    if (savedDark === 'true') setDarkMode(true);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('dark_mode', String(darkMode));
  }, [darkMode]);

  const handleLogin = () => {
    setAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAuthenticated(false);
  };

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'growth': return <GrowthOS />;
      case 'content': return <ContentFactory />;
      case 'voice': return <VoiceStudio />;
      case 'video': return <VideoEditor />;
      case 'sound': return <SoundAnalyzer />;
      case 'shop': return <ShopManager />;
      default: return <Dashboard />;
    }
  };

  if (!authenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className={`min-h-screen flex transition-colors duration-200 ${darkMode ? 'bg-slate-950 text-white' : 'bg-surface-50 text-surface-800'}`}>
      <Sidebar
        page={page}
        setPage={setPage}
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        darkMode={darkMode}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          darkMode={darkMode}
          onToggleDark={() => setDarkMode(!darkMode)}
          onLogout={handleLogout}
        />
        <main className={`flex-1 p-6 overflow-y-auto ${darkMode ? 'bg-slate-950' : 'bg-surface-50'}`}>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;
