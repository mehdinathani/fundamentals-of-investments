import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { HeatmapSector } from '../types';

function cellColor(chg: number): string {
  // green for gains, red for losses, intensity scaled by magnitude
  const clamped = Math.max(-3, Math.min(3, chg));
  const intensity = Math.abs(clamped) / 3; // 0..1
  if (clamped >= 0) {
    return `rgba(14, 203, 129, ${0.15 + intensity * 0.55})`;
  }
  return `rgba(246, 70, 93, ${0.15 + intensity * 0.55})`;
}

export default function SectorHeatmap({ highlightSector }: { highlightSector?: string | null }) {
  const [sectors, setSectors] = useState<HeatmapSector[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHeatmap()
      .then((r) => setSectors(r.sectors))
      .catch(() => setSectors([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-dim text-sm py-8 text-center">Loading heatmap…</p>;
  if (!sectors || sectors.length === 0)
    return <p className="text-dim text-sm py-8 text-center">Heatmap data unavailable.</p>;

  const norm = (s?: string | null) => (s ?? '').trim().toUpperCase();
  const hl = norm(highlightSector);

  return (
    <div className="space-y-2">
      <span className="text-xs text-dim">Today's sector performance — each tile is a sector, sized by activity, colored by average change.</span>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
        {sectors.map((s) => {
          const isHl = hl && (norm(s.name) === hl || norm(s.code) === hl);
          return (
            <div
              key={s.code}
              className={`rounded-md p-2 border ${isHl ? 'border-gold' : 'border-navy-700'}`}
              style={{ backgroundColor: cellColor(s.avg_change_pct) }}
              title={`${s.name} — ${s.stock_count} stocks`}
            >
              <div className="text-[10px] text-white/90 font-medium leading-tight truncate">{s.name}</div>
              <div className="flex items-center justify-between mt-1">
                <span className={`text-xs font-mono font-bold ${s.avg_change_pct >= 0 ? 'text-green' : 'text-red'}`}>
                  {s.avg_change_pct >= 0 ? '+' : ''}{s.avg_change_pct.toFixed(2)}%
                </span>
                <span className="text-[9px] text-dim">{s.stock_count}</span>
              </div>
            </div>
          );
        })}
      </div>
      {hl && <div className="text-[10px] text-gold">★ Highlighted: this stock's sector</div>}
    </div>
  );
}
