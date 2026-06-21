import { useEffect, useState } from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { api } from '../api/client';
import type { Candle } from '../types';

const RANGES = [
  { label: '3M', days: 90 },
  { label: '6M', days: 180 },
  { label: '1Y', days: 252 },
];

export default function PriceChart({ symbol }: { symbol: string }) {
  const [candles, setCandles] = useState<Candle[] | null>(null);
  const [days, setDays] = useState(180);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getHistory(symbol, days)
      .then((r) => setCandles(r.candles))
      .catch(() => setCandles([]))
      .finally(() => setLoading(false));
  }, [symbol, days]);

  if (loading) return <p className="text-dim text-sm py-8 text-center">Loading chart…</p>;
  if (!candles || candles.length === 0)
    return <p className="text-dim text-sm py-8 text-center">No price history available for {symbol}.</p>;

  const last = candles[candles.length - 1];
  const first = candles[0];
  const up = (last.close ?? 0) >= (first.close ?? 0);
  const lineColor = up ? '#0ecb81' : '#f6465d';

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-dim">Close price with MA20 / MA50 / MA200 and volume</span>
        <div className="flex gap-1">
          {RANGES.map((r) => (
            <button
              key={r.label}
              onClick={() => setDays(r.days)}
              className={`px-2 py-0.5 text-[11px] rounded ${
                days === r.days ? 'bg-navy-600 text-white' : 'text-dim hover:text-white'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={candles} margin={{ top: 5, right: 4, left: -8, bottom: 0 }}>
          <CartesianGrid stroke="#151f38" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: '#848e9c', fontSize: 9 }} minTickGap={40} tickLine={false} />
          <YAxis yAxisId="price" domain={['auto', 'auto']} tick={{ fill: '#848e9c', fontSize: 9 }} width={42} tickLine={false} />
          <YAxis yAxisId="vol" orientation="right" hide domain={[0, (max: number) => max * 4]} />
          <Tooltip
            contentStyle={{ background: '#0f1629', border: '1px solid #151f38', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#848e9c' }}
          />
          <Legend wrapperStyle={{ fontSize: 10 }} />
          <Bar yAxisId="vol" dataKey="volume" name="Vol" fill="#1c2a4a" />
          <Line yAxisId="price" dataKey="close" name="Close" stroke={lineColor} dot={false} strokeWidth={1.6} />
          <Line yAxisId="price" dataKey="ma20" name="MA20" stroke="#f0b90b" dot={false} strokeWidth={1} />
          <Line yAxisId="price" dataKey="ma50" name="MA50" stroke="#60a5fa" dot={false} strokeWidth={1} />
          <Line yAxisId="price" dataKey="ma200" name="MA200" stroke="#a78bfa" dot={false} strokeWidth={1} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
