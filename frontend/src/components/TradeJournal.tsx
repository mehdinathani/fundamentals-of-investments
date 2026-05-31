import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Trade } from '../types';

export default function TradeJournal() {
  const [trades, setTrades] = useState<Trade[]>([]);

  useEffect(() => {
    api.getTrades().then(setTrades);
  }, []);

  if (trades.length === 0) {
    return (
      <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
        <h3 className="text-xs font-semibold text-dim uppercase tracking-wider mb-3">Trade Journal</h3>
        <p className="text-sm text-dim">No trades recorded.</p>
      </div>
    );
  }

  return (
    <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
      <h3 className="text-xs font-semibold text-dim uppercase tracking-wider mb-3">Recent Trades</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-dim text-xs uppercase tracking-wider">
              <th className="text-left pb-2 font-medium">Symbol</th>
              <th className="text-left pb-2 font-medium">Entry</th>
              <th className="text-right pb-2 font-medium">Entry Price</th>
              <th className="text-right pb-2 font-medium">Exit Price</th>
              <th className="text-right pb-2 font-medium">P&L</th>
              <th className="text-left pb-2 font-medium">Exit Reason</th>
            </tr>
          </thead>
          <tbody>
            {trades.slice(0, 10).map((t) => (
              <tr key={t.id} className="border-t border-navy-700 text-xs">
                <td className="py-2.5 font-medium">{t.symbol}</td>
                <td className="py-2.5 text-dim">{t.entry_date}</td>
                <td className="py-2.5 text-right font-mono">{t.entry_price.toFixed(2)}</td>
                <td className="py-2.5 text-right font-mono">{t.exit_price?.toFixed(2) ?? '—'}</td>
                <td className={`py-2.5 text-right font-mono ${(t.pnl_net ?? 0) >= 0 ? 'text-green' : 'text-red'}`}>
                  {t.pnl_net != null ? `${t.pnl_net >= 0 ? '+' : ''}${t.pnl_net.toFixed(0)}` : '—'}
                </td>
                <td className="py-2.5 text-dim">{t.exit_reason ?? 'Open'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
