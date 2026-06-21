import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { AIAnalysisResult } from '../types';
import { TrendingUp, AlertTriangle, RefreshCw, BarChart3 } from 'lucide-react';

const VERDICT_COLORS: Record<string, string> = {
  BUY: 'text-green',
  BUY_BACK: 'text-green',
  SELL: 'text-red',
  SHORT_SELL: 'text-red',
  STOP_LOSS: 'text-yellow',
  HOLD: 'text-dim',
};

export default function AIScanSummary({ symbols, onViewDetail }: { symbols?: string[]; onViewDetail: (symbol: string) => void }) {
  const [results, setResults] = useState<AIAnalysisResult[]>([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.scanAnalysis(symbols)
      .then((res) => {
        setResults(res.results.filter((r) => r.ai_available));
        setSummary(res.summary);
      })
      .catch(() => setSummary('AI scan unavailable'))
      .finally(() => setLoading(false));
  }, [symbols]);

  if (loading) {
    return (
      <div className="border border-navy-700 rounded-lg p-4">
        <div className="flex items-center gap-2 text-sm text-dim">
          <RefreshCw className="w-4 h-4 animate-spin" />
          Running AI analysis...
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="border border-navy-700 rounded-lg p-4">
        <p className="text-xs text-dim">{summary || 'No AI analysis available.'}</p>
      </div>
    );
  }

  const sorted = [...results].sort((a, b) => {
    const w = { HIGH: 3, MEDIUM: 2, LOW: 1 };
    return (w[b.confidence] ?? 0) - (w[a.confidence] ?? 0);
  });

  const bestBets = sorted.filter((r) => r.verdict === 'BUY' || r.verdict === 'BUY_BACK').slice(0, 3);
  const redFlags = sorted.filter((r) => r.verdict === 'SELL' || r.verdict === 'SHORT_SELL' || r.verdict === 'STOP_LOSS');
  const sectors = new Map<string, { bullish: number; bearish: number }>();
  for (const r of results) {
    const sec = r.peer_comparison?.split(' ')[0] || 'Unknown';
    const e = sectors.get(sec) || { bullish: 0, bearish: 0 };
    if (r.verdict === 'BUY' || r.verdict === 'BUY_BACK') e.bullish++;
    else if (r.verdict === 'SELL' || r.verdict === 'SHORT_SELL' || r.verdict === 'STOP_LOSS') e.bearish++;
    sectors.set(sec, e);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-dim uppercase tracking-wider">AI Scan Summary</h3>
        <span className="text-[10px] text-dim">{summary}</span>
      </div>

      {bestBets.length > 0 && (
        <div className="border border-green/20 bg-green-900/10 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-green" />
            <span className="text-[10px] font-semibold text-green uppercase tracking-wider">Best Bets</span>
          </div>
          <div className="space-y-1.5">
            {bestBets.map((r) => (
              <button
                key={r.symbol}
                onClick={() => onViewDetail(r.symbol)}
                className="w-full flex items-center justify-between text-xs hover:bg-green-900/20 rounded px-2 py-1 transition-colors cursor-pointer"
              >
                <span className="font-medium text-white">{r.symbol}</span>
                <span className={`font-mono ${VERDICT_COLORS[r.verdict]}`}>
                  {r.verdict} ({r.confidence})
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {redFlags.length > 0 && (
        <div className="border border-red/20 bg-red-900/10 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <AlertTriangle className="w-3.5 h-3.5 text-red" />
            <span className="text-[10px] font-semibold text-red uppercase tracking-wider">Red Flags</span>
          </div>
          <div className="space-y-1.5">
            {redFlags.map((r) => (
              <button
                key={r.symbol}
                onClick={() => onViewDetail(r.symbol)}
                className="w-full flex items-center justify-between text-xs hover:bg-red-900/20 rounded px-2 py-1 transition-colors cursor-pointer"
              >
                <span className="font-medium text-white">{r.symbol}</span>
                <span className={`font-mono ${VERDICT_COLORS[r.verdict]}`}>
                  {r.verdict} ({r.confidence})
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {sectors.size > 1 && (
        <div className="border border-navy-700 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <BarChart3 className="w-3.5 h-3.5 text-purple" />
            <span className="text-[10px] font-semibold text-dim uppercase tracking-wider">Sector Rotation</span>
          </div>
          <div className="space-y-1">
            {Array.from(sectors.entries()).map(([sector, counts]) => (
              <div key={sector} className="flex items-center justify-between text-xs">
                <span className="text-dim">{sector}</span>
                <div className="flex gap-2 font-mono">
                  <span className="text-green">{counts.bullish}B</span>
                  <span className="text-red">{counts.bearish}S</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
