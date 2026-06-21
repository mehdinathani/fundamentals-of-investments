interface Props {
  verdict: string;
  confidence: string;
}

const VERDICT_COLOR: Record<string, string> = {
  BUY: '#0ecb81',
  BUY_BACK: '#0ecb81',
  SELL: '#f6465d',
  SHORT_SELL: '#f6465d',
  STOP_LOSS: '#f0b90b',
  HOLD: '#848e9c',
  IGNORE: '#5a6577',
};

const VERDICT_LABEL: Record<string, string> = {
  BUY: 'BUY',
  BUY_BACK: 'BUY BACK',
  SELL: 'SELL',
  SHORT_SELL: 'SHORT SELL',
  STOP_LOSS: 'STOP LOSS',
  HOLD: 'HOLD',
  IGNORE: 'IGNORE',
};

const CONF_FRACTION: Record<string, number> = { HIGH: 1, MEDIUM: 0.66, LOW: 0.33 };

export default function VerdictGauge({ verdict, confidence }: Props) {
  const color = VERDICT_COLOR[verdict] ?? '#848e9c';
  const label = VERDICT_LABEL[verdict] ?? verdict;
  const frac = CONF_FRACTION[confidence] ?? 0.33;

  // Semicircle gauge: 180deg arc, radius 60, centered at (75, 70)
  const R = 60;
  const cx = 75;
  const cy = 70;
  const circumference = Math.PI * R; // half circle
  const dash = `${circumference * frac} ${circumference}`;

  return (
    <div className="flex flex-col items-center py-1">
      <svg width="150" height="84" viewBox="0 0 150 84">
        {/* track */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke="#151f38"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* confidence fill */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={dash}
        />
      </svg>
      <div className="-mt-6 text-center">
        <div className="text-lg font-bold tracking-wider" style={{ color }}>{label}</div>
        <div className="text-[10px] text-dim uppercase tracking-wider mt-0.5">
          {confidence} confidence
        </div>
      </div>
    </div>
  );
}
