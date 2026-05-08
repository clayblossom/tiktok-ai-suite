import { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { ContentFactory } from './pages/ContentFactory';
import { VoiceStudio } from './pages/VoiceStudio';
import { VideoEditor } from './pages/VideoEditor';
import { SoundAnalyzer } from './pages/SoundAnalyzer';
import { ShopManager } from './pages/ShopManager';

type Page = 'dashboard' | 'content' | 'voice' | 'video' | 'sound' | 'shop';

function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'content': return <ContentFactory />;
      case 'voice': return <VoiceStudio />;
      case 'video': return <VideoEditor />;
      case 'sound': return <SoundAnalyzer />;
      case 'shop': return <ShopManager />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-tiktok-dark flex">
      <Sidebar page={page} setPage={setPage} open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 overflow-y-auto">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;
