import { useState, useCallback } from 'react';
import MacroIndicator from './components/MacroIndicator';
import MarketGrid from './components/MarketGrid';
import PipelineControls from './components/PipelineControls';
import PerformanceCard from './components/PerformanceCard';
import TradeJournal from './components/TradeJournal';
import { BarChart3 } from 'lucide-react';

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const refresh = useCallback(() => setRefreshKey((k) => k + 1), []);

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
            <MarketGrid />
          </div>
        </div>

        <div key={`journal-${refreshKey}`}>
          <TradeJournal />
        </div>
      </main>
    </div>
  );
}
