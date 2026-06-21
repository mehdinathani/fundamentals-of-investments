import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import type { RatioComparison } from '../types';

const INDEX_ORDER = ['SECTOR', 'KSE30', 'KSE100', 'ALLSHR'];
const INDEX_COLORS: Record<string, string> = {
  STOCK: '#f0b90b',
  SECTOR: '#fbbf24',
  KSE30: '#60a5fa',
  KSE100: '#a78bfa',
  ALLSHR: '#34d399',
};

function RatioBlock({ label, ratio }: { label: string; ratio: RatioComparison }) {
  const val = ratio.value;
  const comparisons = ratio.comparisons ?? {};
  if (val == null) return null;

  const data = [
    { key: 'STOCK', name: 'This Stock', value: val },
    ...INDEX_ORDER
      .filter((k) => comparisons[k]?.median != null)
      .map((k) => ({ key: k, name: k, value: comparisons[k]!.median as number })),
  ];
  if (data.length < 2) return null;

  const pct = ratio.percentile_rank;

  return (
    <div className="border border-navy-700 rounded-lg p-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-white">{label}</span>
        <div className="text-right">
          <span className="text-sm font-mono font-bold text-gold">{val.toFixed(2)}</span>
          {pct != null && (
            <div className="text-[10px] text-dim">{pct.toFixed(0)}th percentile in sector</div>
          )}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={130}>
        <BarChart data={data} margin={{ top: 5, right: 4, left: -12, bottom: 0 }}>
          <CartesianGrid stroke="#151f38" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: '#848e9c', fontSize: 9 }} tickLine={false} />
          <YAxis tick={{ fill: '#848e9c', fontSize: 9 }} tickLine={false} />
          <Tooltip
            cursor={{ fill: '#1c2a4a', opacity: 0.3 }}
            contentStyle={{ background: '#0f1629', border: '1px solid #151f38', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#848e9c' }}
          />
          <Bar dataKey="value" radius={[3, 3, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.key} fill={INDEX_COLORS[d.key] ?? '#6b7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

const RATIO_LABELS: Record<string, string> = {
  PE: 'Price-to-Earnings (P/E)',
  EPS: 'Earnings Per Share (EPS)',
  ROE: 'Return on Equity (ROE)',
  DE: 'Debt-to-Equity (D/E)',
  DIVIDEND_YIELD: 'Dividend Yield',
};

export default function RatioRadar({ ratios }: { ratios: Record<string, RatioComparison> }) {
  const keys = Object.keys(ratios ?? {});
  if (keys.length === 0)
    return <p className="text-dim text-sm py-4 text-center">No benchmark data available.</p>;

  return (
    <div className="space-y-2">
      <span className="text-xs text-dim">
        Each ratio compared against its sector, KSE30, KSE100 and the whole market — gold is this stock.
      </span>
      <div className="grid grid-cols-1 gap-2">
        {keys.map((k) => (
          <RatioBlock key={k} label={ratios[k].name || RATIO_LABELS[k] || k} ratio={ratios[k]} />
        ))}
      </div>
    </div>
  );
}
