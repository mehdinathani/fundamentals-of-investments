import { useState, useCallback, useRef } from 'react';
import MacroIndicator from './components/MacroIndicator';
import MarketGrid from './components/MarketGrid';
import PipelineControls from './components/PipelineControls';
import PerformanceCard from './components/PerformanceCard';
import TradeJournal from './components/TradeJournal';
import SymbolDetail from './components/SymbolDetail';
import AIScanSummary from './components/AIScanSummary';
import { BarChart3, Lock } from 'lucide-react';
import { isAuthed, login } from './api/client';

function LoginForm({ onLogin }: { onLogin: () => void }) {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(user, pass);
      onLogin();
    } catch {
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 flex items-center justify-center px-4">
      <div className="bg-navy-800 rounded-xl border border-navy-700 p-8 w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-6">
          <Lock className="w-5 h-5 text-gold" />
          <h1 className="text-xl font-bold">
            PSX <span className="text-gold">Invest</span>
          </h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-dim mb-1 uppercase tracking-wider">Username</label>
            <input
              type="text"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
              placeholder="admin"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs text-dim mb-1 uppercase tracking-wider">Password</label>
            <input
              type="password"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
              placeholder="psx2026"
            />
          </div>
          {error && <p className="text-red text-xs">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-gold text-navy-900 rounded-lg font-semibold text-sm hover:brightness-110 disabled:opacity-50 transition-all"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(isAuthed());
  const [refreshKey, setRefreshKey] = useState(0);
  const [quickLogSymbol, setQuickLogSymbol] = useState<string | null>(null);
  const [detailSymbol, setDetailSymbol] = useState<string | null>(null);
  const [scanSymbols, setScanSymbols] = useState<string[] | null>(null);
  const scanTriggered = useRef(false);
  const refresh = useCallback(() => {
    setRefreshKey((k) => k + 1);
    scanTriggered.current = true;
  }, []);

  if (!authed) {
    return <LoginForm onLogin={() => setAuthed(true)} />;
  }

  return (
    <div className="min-h-screen bg-navy-900">
      {/* Header */}
      <header className="border-b border-navy-700 bg-navy-800/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-gold" />
              <h1 className="text-lg font-bold tracking-tight">
                PSX <span className="text-gold">Invest</span>
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <MacroIndicator />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Controls */}
        <div className="mb-6">
          <PipelineControls onRun={refresh} />
        </div>

        {/* Grid: Performance + Market + Journal */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
          <div className="lg:col-span-1">
            <PerformanceCard />
          </div>
          <div className="lg:col-span-3" key={`market-${refreshKey}`}>
            <MarketGrid onQuickLog={setQuickLogSymbol} onViewDetail={setDetailSymbol} onScanReady={setScanSymbols} />
          </div>
          <div className="lg:col-span-1" key={`ai-${refreshKey}`}>
            <AIScanSummary symbols={scanSymbols ?? undefined} onViewDetail={setDetailSymbol} />
          </div>
        </div>

        <div key={`journal-${refreshKey}`}>
          <TradeJournal quickLogSymbol={quickLogSymbol} onQuickLogHandled={() => setQuickLogSymbol(null)} />
        </div>
      </main>

      {detailSymbol && (
        <SymbolDetail symbol={detailSymbol} onClose={() => setDetailSymbol(null)} />
      )}
    </div>
  );
}
