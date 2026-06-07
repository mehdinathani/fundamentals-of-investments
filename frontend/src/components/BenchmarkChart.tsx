import type { RatioComparison } from '../types';

interface Props {
  label: string;
  ratio: RatioComparison;
}

const INDEX_COLORS: Record<string, string> = {
  SECTOR: '#fbbf24',
  KSE30: '#60a5fa',
  KSE100: '#a78bfa',
  ALLSHR: '#34d399',
};

const INDEX_ORDER = ['SECTOR', 'KSE30', 'KSE100', 'ALLSHR'];

export default function BenchmarkChart({ label, ratio }: Props) {
  const comparisons = ratio.comparisons ?? {};
  const val = ratio.value;

  const entries = INDEX_ORDER
    .filter((k) => comparisons[k]?.median != null)
    .map((k) => ({ index: k, ...comparisons[k]! }));

  if (!val || entries.length === 0) return null;

  const maxMedian = Math.max(...entries.map((e) => e.median ?? 0), val) * 1.2;

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-dim font-medium">{label}</span>
        <span className="text-xs font-mono text-white font-bold">{val.toFixed(2)}</span>
      </div>
      {entries.map((e) => {
        const pct = ((e.median ?? 0) / maxMedian) * 100;
        const valPct = (val / maxMedian) * 100;
        const isAbove = val >= (e.median ?? 0);
        return (
          <div key={e.index} className="mb-1.5">
            <div className="flex items-center justify-between text-[11px] mb-0.5">
              <span className="text-dim">{e.index}{e.sector_name ? ` (${e.sector_name})` : ''}</span>
              <span className="text-dim font-mono">
                {e.median?.toFixed(2)}
                {e.deviation_pct != null && (
                  <span className={isAbove ? 'text-green ml-1' : 'text-red ml-1'}>
                    {e.deviation_pct > 0 ? '+' : ''}{e.deviation_pct.toFixed(1)}%
                  </span>
                )}
              </span>
            </div>
            <div className="relative h-3 bg-navy-900 rounded-sm overflow-hidden">
              <div
                className="absolute h-full rounded-sm transition-all"
                style={{ width: `${pct}%`, backgroundColor: INDEX_COLORS[e.index] || '#6b7280', opacity: 0.5 }}
              />
              <div
                className="absolute h-full w-0.5 bg-white rounded transition-all"
                style={{ left: `${Math.min(valPct, 100)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
