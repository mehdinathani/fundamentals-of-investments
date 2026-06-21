import { useState } from 'react';
import { api } from '../api/client';
import { RefreshCw, Play, Activity } from 'lucide-react';

export default function PipelineControls({ onRun }: { onRun: () => void }) {
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setStatus(null);
    try {
      const res = await api.runPipeline();
      setStatus(`Pipeline ${res.status}: ${res.signals_generated} signals from ${res.symbols_scanned} symbols`);
      onRun();
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleRun}
        disabled={running}
        className="flex items-center gap-2 px-4 py-2 bg-gold text-navy-900 rounded-lg font-semibold text-sm hover:brightness-110 disabled:opacity-50 transition-all"
      >
        {running ? (
          <RefreshCw className="w-4 h-4 animate-spin" />
        ) : (
          <Play className="w-4 h-4" />
        )}
        {running ? 'Running...' : 'Run Pipeline'}
      </button>
      {status && (
        <span className="text-xs text-dim">{status}</span>
      )}
      <button onClick={onRun} className="p-2 text-dim hover:text-white transition-colors" title="Refresh">
        <Activity className="w-4 h-4" />
      </button>
    </div>
  );
}
