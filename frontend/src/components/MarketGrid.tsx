import { useEffect, useState } from 'react';
import { Receipt } from 'lucide-react';
import { api } from '../api/client';
import type { SymbolData } from '../types';

export default function MarketGrid({ onQuickLog, onViewDetail }: { onQuickLog: (symbol: string) => void; onViewDetail: (symbol: string) => void }) {
  const [data, setData] = useState<SymbolData[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'buys'>('all');

  useEffect(() => {
    api.scanMarket().then((res) => {
      setData(res.symbols);
      setLoading(false);
    });
  }, []);

  const displayed = filter === 'buys' ? data.filter((s) => s.signal === 'BUY') : data;

  if (loading) return <div className="text-center py-8 text-dim">Scanning market...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-dim uppercase tracking-wider">Market Scan</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-2.5 py-1 text-xs rounded ${filter === 'all' ? 'bg-navy-600 text-white' : 'text-dim hover:text-white'}`}
          >
            All ({data.length})
          </button>
          <button
            onClick={() => setFilter('buys')}
            className={`px-2.5 py-1 text-xs rounded ${filter === 'buys' ? 'bg-green-900/50 text-green' : 'text-dim hover:text-white'}`}
          >
            Signals ({data.filter((s) => s.signal === 'BUY').length})
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-navy-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-navy-800 text-dim text-xs uppercase tracking-wider">
              <th className="text-left p-3 font-medium">Symbol</th>
              <th className="text-right p-3 font-medium">Price</th>
              <th className="text-right p-3 font-medium">Change</th>
              <th className="text-right p-3 font-medium">RSI</th>
              <th className="text-right p-3 font-medium">ADX</th>
              <th className="text-right p-3 font-medium">Vol</th>
              <th className="text-center p-3 font-medium">Signal</th>
              <th className="text-right p-3 font-medium" />
            </tr>
          </thead>
          <tbody>
            {displayed.map((s) => (
              <tr key={s.symbol} className="border-t border-navy-700 hover:bg-navy-800/50 transition-colors">
                <td className="p-3 font-medium">
                  <button onClick={() => onViewDetail(s.symbol)} className="hover:text-gold transition-colors cursor-pointer">
                    {s.symbol}
                  </button>
                </td>
                <td className="p-3 text-right font-mono">
                  {s.current_price?.toFixed(2) ?? '-'}
                </td>
                <td className={`p-3 text-right font-mono ${(s.change_pct ?? 0) >= 0 ? 'text-green' : 'text-red'}`}>
                  {(s.change_pct ?? 0) >= 0 ? '+' : ''}{s.change_pct?.toFixed(2)}%
                </td>
                <td className="p-3 text-right font-mono">{s.rsi?.toFixed(1) ?? '-'}</td>
                <td className="p-3 text-right font-mono">{s.adx?.toFixed(1) ?? '-'}</td>
                <td className="p-3 text-right font-mono">{s.volume_ratio?.toFixed(1)}x</td>
                <td className="p-3 text-center">
                  {s.signal === 'BUY' ? (
                    <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded bg-green-900/40 text-green border border-green/30">
                      {s.signal_strength?.includes('Tier 1') ? '★' : ''} BUY
                    </span>
                  ) : (
                    <span className="text-dim text-xs">—</span>
                  )}
                </td>
                <td className="p-3 text-right">
                  <button
                    onClick={() => onQuickLog(s.symbol)}
                    className="text-dim hover:text-gold transition-colors"
                    title={`Log trade for ${s.symbol}`}
                  >
                    <Receipt className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
