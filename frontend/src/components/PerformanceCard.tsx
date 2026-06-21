import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Performance } from '../types';
import { TrendingUp, TrendingDown, BarChart3, DollarSign } from 'lucide-react';

export default function PerformanceCard() {
  const [perf, setPerf] = useState<Performance | null>(null);

  useEffect(() => {
    api.getPerformance().then(setPerf);
  }, []);

  if (!perf || perf.total_trades === 0) {
    return (
      <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
        <h3 className="text-xs font-semibold text-dim uppercase tracking-wider mb-3">Performance</h3>
        <p className="text-sm text-dim">No closed trades yet.</p>
      </div>
    );
  }

  const stats = [
    { label: 'Total Trades', value: perf.total_trades, icon: BarChart3, color: 'text-blue' },
    { label: 'Win Rate', value: `${perf.win_rate}%`, icon: TrendingUp, color: 'text-green' },
    { label: 'W/L Ratio', value: perf.win_loss_ratio.toFixed(2), icon: TrendingDown, color: 'text-gold' },
    { label: 'Net P&L', value: `PKR ${perf.total_pnl_net.toLocaleString()}`, icon: DollarSign, color: perf.total_pnl_net >= 0 ? 'text-green' : 'text-red' },
  ];

  return (
    <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
      <h3 className="text-xs font-semibold text-dim uppercase tracking-wider mb-3">Performance</h3>
      <div className="grid grid-cols-2 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="bg-navy-900 rounded-lg p-3">
            <div className="flex items-center gap-1.5 text-dim text-xs mb-1">
              <s.icon className="w-3 h-3" />
              {s.label}
            </div>
            <div className={`text-lg font-bold font-mono ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-dim">
        <div>Avg Win: <span className="text-green font-mono">PKR {perf.avg_win.toLocaleString()}</span></div>
        <div>Avg Loss: <span className="text-red font-mono">PKR {perf.avg_loss.toLocaleString()}</span></div>
        <div>Expectancy: <span className={`font-mono ${perf.expectancy >= 0 ? 'text-green' : 'text-red'}`}>PKR {perf.expectancy.toLocaleString()}</span></div>
      </div>
    </div>
  );
}
