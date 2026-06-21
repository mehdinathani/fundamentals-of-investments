import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { SymbolDetail as SymbolDetailType, ComparisonResult, AIAnalysisResult } from '../types';
import Modal from './Modal';
import AIReportPanel from './AIReportPanel';
import PriceChart from './PriceChart';
import SectorHeatmap from './SectorHeatmap';
import RatioRadar from './RatioRadar';

type Tab = 'chart' | 'technical' | 'fundamentals' | 'ai' | 'benchmarks' | 'market';

export default function SymbolDetail({ symbol, onClose }: { symbol: string; onClose: () => void }) {
  const [data, setData] = useState<SymbolDetailType | null>(null);
  const [benchmarks, setBenchmarks] = useState<ComparisonResult | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('chart');

  useEffect(() => {
    Promise.all([
      api.getSymbol(symbol),
      api.getBenchmarks(symbol),
      api.getAnalysis(symbol),
    ]).then(([sym, bm, ai]) => {
      setData(sym);
      setBenchmarks(bm);
      setAnalysis(ai);
      setLoading(false);
    });
  }, [symbol]);

  const tabs: { key: Tab; label: string }[] = [
    { key: 'chart', label: 'Chart' },
    { key: 'ai', label: 'AI Mentor' },
    { key: 'benchmarks', label: 'Benchmarks' },
    { key: 'technical', label: 'Technical' },
    ...(data?.macro ? [{ key: 'fundamentals' as Tab, label: 'Fundamentals' }] : []),
    { key: 'market', label: 'Market' },
  ];

  return (
    <Modal open={true} onClose={onClose} title={symbol} size="lg">
      {loading ? (
        <p className="text-dim text-sm py-4 text-center">Loading...</p>
      ) : (
        <div className="space-y-4">
          <div className="flex gap-1 border-b border-navy-700 pb-1">
            {tabs.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                className={`px-2.5 py-1 text-xs rounded-t transition-colors ${
                  tab === t.key
                    ? 'bg-navy-700 text-white border-b-2 border-gold'
                    : 'text-dim hover:text-white'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === 'chart' && (
            <PriceChart symbol={symbol} />
          )}

          {tab === 'technical' && data && (
            <div className="space-y-3 text-sm">
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

              {data.signal === 'BUY' && (
                <div className="bg-green-900/20 border border-green/30 rounded-lg px-3 py-2 text-center">
                  <span className="text-green font-bold text-xs uppercase tracking-wider">
                    {data.signal_strength?.includes('Tier 1') ? '\u2605 ' : ''}BUY Signal — {data.signal_strength}
                  </span>
                </div>
              )}

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
            </div>
          )}

          {tab === 'fundamentals' && data?.macro && (
            <div>
              <h4 className="text-dim text-xs uppercase tracking-wider font-semibold mb-2">Macro Fundamentals</h4>
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

          {tab === 'ai' && analysis && (
            <AIReportPanel analysis={analysis} />
          )}

          {tab === 'benchmarks' && benchmarks && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs text-dim">
                <span>Sector: {benchmarks.sector ?? 'N/A'}</span>
                {benchmarks.sector_peers.length > 0 && (
                  <span>| Peers: {benchmarks.sector_peers.join(', ')}</span>
                )}
              </div>
              <RatioRadar ratios={benchmarks.ratios} />
            </div>
          )}

          {tab === 'market' && (
            <SectorHeatmap highlightSector={benchmarks?.sector} />
          )}
        </div>
      )}
    </Modal>
  );
}
