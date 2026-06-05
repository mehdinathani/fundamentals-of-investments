import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { SymbolDetail as SymbolDetailType } from '../types';
import Modal from './Modal';

export default function SymbolDetail({ symbol, onClose }: { symbol: string; onClose: () => void }) {
  const [data, setData] = useState<SymbolDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSymbol(symbol).then((res) => {
      setData(res);
      setLoading(false);
    });
  }, [symbol]);

  return (
    <Modal open={true} onClose={onClose} title={symbol}>
      {loading ? (
        <p className="text-dim text-sm py-4 text-center">Loading...</p>
      ) : data ? (
        <div className="space-y-5 text-sm">
          {/* Price Overview */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold font-mono">
                {data.current_price?.toFixed(2) ?? '-'}
              </div>
              <div className="text-dim text-xs mt-0.5">
                Prev close: {data.prev_close?.toFixed(2) ?? '-'}
              </div>
            </div>
            <div className={`text-right ${(data.change_pct ?? 0) >= 0 ? 'text-green' : 'text-red'}`}>
              <div className="text-lg font-semibold font-mono">
                {(data.change_pct ?? 0) >= 0 ? '+' : ''}{data.change_pct?.toFixed(2)}%
              </div>
              <div className="text-dim text-xs">Change</div>
            </div>
          </div>

          {/* Signal */}
          {data.signal === 'BUY' && (
            <div className="bg-green-900/20 border border-green/30 rounded-lg px-3 py-2 text-center">
              <span className="text-green font-bold text-xs uppercase tracking-wider">
                {data.signal_strength?.includes('Tier 1') ? '★ ' : ''}BUY Signal — {data.signal_strength}
              </span>
            </div>
          )}

          {/* Technical Analysis */}
          <div>
            <h4 className="text-dim text-xs uppercase tracking-wider font-semibold mb-2">Technical Analysis</h4>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2">
              <div className="flex justify-between">
                <span className="text-dim">RSI (14)</span>
                <span className="font-mono font-medium">{data.rsi?.toFixed(1) ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">ADX (14)</span>
                <span className="font-mono font-medium">{data.adx?.toFixed(1) ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">MA20</span>
                <span className="font-mono font-medium">{data.ma20?.toFixed(2) ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">MA50</span>
                <span className="font-mono font-medium">{data.ma50?.toFixed(2) ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">MA200</span>
                <span className="font-mono font-medium">{data.ma200?.toFixed(2) ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">Volume Ratio</span>
                <span className="font-mono font-medium">{data.volume_ratio?.toFixed(2)}x</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">Breakout</span>
                <span className={data.breakout ? 'text-green' : 'text-dim'}>{data.breakout ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dim">Last Date</span>
                <span className="font-mono">{data.date}</span>
              </div>
            </div>
          </div>

          {/* Fundamentals */}
          {data.macro && (
            <div>
              <h4 className="text-dim text-xs uppercase tracking-wider font-semibold mb-2">Fundamentals</h4>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                <div className="flex justify-between">
                  <span className="text-dim">Macro State</span>
                  <span className={`font-semibold ${
                    data.macro.state === 'RISK_ON' ? 'text-green' : data.macro.state === 'RISK_OFF' ? 'text-red' : 'text-yellow'
                  }`}>{data.macro.state}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dim">SBP Rate</span>
                  <span className="font-mono">{data.macro.sbp_rate ?? '-'}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dim">USD/PKR</span>
                  <span className="font-mono">{data.macro.usdpkr ?? '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dim">IMF Status</span>
                  <span className="font-mono">{data.macro.imf_status ?? '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dim">KSE100 P/E</span>
                  <span className="font-mono">{data.macro.kse100_pe ?? '-'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="text-red text-sm py-4 text-center">Symbol not found</p>
      )}
    </Modal>
  );
}