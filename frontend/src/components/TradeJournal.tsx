import { useEffect, useState, useRef } from 'react';
import { Plus } from 'lucide-react';
import { api } from '../api/client';
import type { Trade } from '../types';
import Modal from './Modal';

const dirBadge = { LONG: 'text-green border-green/30 bg-green/10', SHORT: 'text-red border-red/30 bg-red/10' };

export default function TradeJournal({ quickLogSymbol, onQuickLogHandled }: {
  quickLogSymbol?: string | null;
  onQuickLogHandled?: () => void;
}) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [version, setVersion] = useState(0);
  const [showAdd, setShowAdd] = useState(false);
  const [addDir, setAddDir] = useState<'LONG' | 'SHORT'>('LONG');
  const [closing, setClosing] = useState<Trade | null>(null);

  const symbolRef = useRef<HTMLInputElement>(null);
  const [fetchedPrice, setFetchedPrice] = useState<number | null>(null);
  const [fetching, setFetching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    api.getTrades().then(setTrades);
  }, [version]);

  // Quick-log from market scan
  useEffect(() => {
    if (quickLogSymbol) {
      setAddDir('LONG');
      setFetchedPrice(null);
      setShowAdd(true);
      onQuickLogHandled?.();
      // Pre-fetch price for the symbol
      api.getSymbol(quickLogSymbol).then((data) => {
        if (data?.current_price) setFetchedPrice(data.current_price);
      }).catch(() => {});
    }
  }, [quickLogSymbol]);

  // Debounced price fetch on symbol input
  const onSymbolInput = () => {
    const sym = symbolRef.current?.value.trim().toUpperCase();
    if (!sym || sym.length < 2) return;
    setFetching(true);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      api.getSymbol(sym).then((data) => {
        if (data?.current_price != null) setFetchedPrice(data.current_price);
        setFetching(false);
      }).catch(() => setFetching(false));
    }, 400);
  };

  const openAddModal = (dir: 'LONG' | 'SHORT') => {
    setAddDir(dir);
    setFetchedPrice(null);
    setShowAdd(true);
  };

  const addTrade = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    await api.addTrade({
      direction: fd.get('direction') as 'LONG' | 'SHORT',
      symbol: fd.get('symbol') as string,
      entry_date: fd.get('entry_date') as string,
      entry_price: parseFloat(fd.get('entry_price') as string),
      shares: parseInt(fd.get('shares') as string),
      entry_signal: (fd.get('entry_signal') as string) || null,
      notes: (fd.get('notes') as string) || null,
    });
    setShowAdd(false);
    setVersion((v) => v + 1);
  };

  const closeTrade = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!closing) return;
    const fd = new FormData(e.currentTarget);
    await api.closeTrade(closing.id, {
      exit_date: fd.get('exit_date') as string,
      exit_price: parseFloat(fd.get('exit_price') as string),
      exit_reason: (fd.get('exit_reason') as string) || null,
      fees: parseFloat(fd.get('fees') as string) || null,
    });
    setClosing(null);
    setVersion((v) => v + 1);
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <>
      <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-semibold text-dim uppercase tracking-wider">Trade Journal</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => openAddModal('LONG')}
              className="flex items-center gap-1 text-xs font-medium text-green hover:brightness-110 transition-all"
            >
              <Plus className="w-3 h-3" />
              Add Trade
            </button>
          </div>
        </div>

        {trades.length === 0 ? (
          <p className="text-sm text-dim">No trades recorded.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-dim text-xs uppercase tracking-wider">
                  <th className="text-left pb-2 font-medium">Dir</th>
                  <th className="text-left pb-2 font-medium">Symbol</th>
                  <th className="text-left pb-2 font-medium">Entry</th>
                  <th className="text-right pb-2 font-medium">Entry Price</th>
                  <th className="text-right pb-2 font-medium">Exit Price</th>
                  <th className="text-right pb-2 font-medium">P&L</th>
                  <th className="text-left pb-2 font-medium">Exit Reason</th>
                  <th className="text-right pb-2 font-medium" />
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 20).map((t) => {
                  const Icon = t.direction === 'SHORT' ? 'S' : 'L';
                  return (
                    <tr key={t.id} className="border-t border-navy-700 text-xs">
                      <td className="py-2.5">
                        <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-semibold border ${dirBadge[t.direction]}`}>
                          {Icon}
                        </span>
                      </td>
                      <td className="py-2.5 font-medium">{t.symbol}</td>
                      <td className="py-2.5 text-dim whitespace-nowrap">{t.entry_date}</td>
                      <td className="py-2.5 text-right font-mono">{t.entry_price.toFixed(2)}</td>
                      <td className="py-2.5 text-right font-mono">{t.exit_price?.toFixed(2) ?? '—'}</td>
                      <td className={`py-2.5 text-right font-mono ${(t.pnl_net ?? 0) >= 0 ? 'text-green' : 'text-red'}`}>
                        {t.pnl_net != null ? `${t.pnl_net >= 0 ? '+' : ''}${t.pnl_net.toFixed(0)}` : '—'}
                      </td>
                      <td className="py-2.5 text-dim">{t.exit_reason ?? 'Open'}</td>
                      <td className="py-2.5 text-right whitespace-nowrap">
                        {!t.exit_date && (
                          <button
                            onClick={() => setClosing(t)}
                            className="text-dim hover:text-gold transition-colors text-xs"
                          >
                            {t.direction === 'SHORT' ? 'Cover' : 'Sell'}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal open={showAdd} onClose={() => setShowAdd(false)} title="Add Trade">
        <form onSubmit={addTrade} className="space-y-3">
          <input type="hidden" name="direction" value={addDir} />
          <div>
            <label className="block text-xs text-dim mb-1">Action</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setAddDir('LONG')}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all border ${
                  addDir === 'LONG'
                    ? 'bg-green/10 text-green border-green/50'
                    : 'bg-navy-900 text-dim border-navy-600 hover:text-white'
                }`}
              >
                Buy (Long)
              </button>
              <button
                type="button"
                onClick={() => setAddDir('SHORT')}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all border ${
                  addDir === 'SHORT'
                    ? 'bg-red/10 text-red border-red/50'
                    : 'bg-navy-900 text-dim border-navy-600 hover:text-white'
                }`}
              >
                Short Sell
              </button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-dim mb-1">Symbol</label>
              <input
                ref={symbolRef}
                name="symbol"
                required
                defaultValue={quickLogSymbol ?? ''}
                onInput={onSymbolInput}
                className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold uppercase"
                placeholder="FABL"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="block text-xs text-dim mb-1">Shares</label>
              <input
                name="shares"
                type="number"
                min="1"
                required
                className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
                placeholder="500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Entry Date</label>
            <input
              name="entry_date"
              type="date"
              required
              defaultValue={today}
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Entry Price (PKR)</label>
            <div className="relative">
              <input
                name="entry_price"
                type="number"
                step="0.01"
                min="0"
                required
                defaultValue={fetchedPrice ?? ''}
                key={fetchedPrice ?? 'manual'}
                className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
                placeholder={fetching ? 'Fetching...' : '42.50'}
              />
              {fetching && (
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-dim">...</span>
              )}
            </div>
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Signal (optional)</label>
            <input
              name="entry_signal"
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
              placeholder="MA crossover, breakout, etc."
            />
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Notes (optional)</label>
            <input
              name="notes"
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold"
              placeholder={addDir === 'SHORT' ? 'Why you shorted' : 'Why you entered'}
            />
          </div>
          <button
            type="submit"
            className={`w-full py-2 rounded-lg font-semibold text-sm hover:brightness-110 transition-all ${
              addDir === 'LONG' ? 'bg-green text-navy-900' : 'bg-red text-white'
            }`}
          >
            Record {addDir === 'SHORT' ? 'Short' : 'Buy'}
          </button>
        </form>
      </Modal>

      <Modal open={!!closing} onClose={() => setClosing(null)} title={`${closing?.direction === 'SHORT' ? 'Cover' : 'Sell'} ${closing?.symbol ?? ''}`}>
        <form onSubmit={closeTrade} className="space-y-3">
          <div>
            <label className="block text-xs text-dim mb-1">Exit Date</label>
            <input name="exit_date" type="date" required defaultValue={today} className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-gold" />
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Exit Price (PKR)</label>
            <input name="exit_price" type="number" step="0.01" min="0" required className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold" placeholder="48.75" />
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Exit Reason</label>
            <select name="exit_reason" className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-gold">
              <option value="">Select reason</option>
              <option value="Target hit">Target hit</option>
              <option value="Stop loss">Stop loss</option>
              <option value="Trailing stop">Trailing stop</option>
              <option value="Time exit">Time exit</option>
              <option value="Signal reversed">Signal reversed</option>
              <option value="Manual">Manual</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-dim mb-1">Fees (PKR, optional)</label>
            <input name="fees" type="number" step="0.01" min="0" className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-sm text-white placeholder-dim focus:outline-none focus:border-gold" placeholder="250" />
          </div>
          <button type="submit" className="w-full py-2 bg-gold text-navy-900 rounded-lg font-semibold text-sm hover:brightness-110 transition-all">
            Record {closing?.direction === 'SHORT' ? 'Cover' : 'Sell'}
          </button>
        </form>
      </Modal>
    </>
  );
}
