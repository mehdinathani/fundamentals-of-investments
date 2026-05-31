import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { MacroState } from '../types';

const stateConfig = {
  RISK_ON: { label: 'Risk On', bg: 'bg-green-900/40 text-green border-green/30', pulse: false },
  NEUTRAL: { label: 'Neutral', bg: 'bg-yellow-900/40 text-yellow border-yellow/30', pulse: false },
  RISK_OFF: { label: 'Risk Off', bg: 'bg-red-900/40 text-red border-red/30', pulse: true },
};

export default function MacroIndicator() {
  const [macro, setMacro] = useState<MacroState | null>(null);

  useEffect(() => {
    api.getMacroState().then(setMacro);
  }, []);

  if (!macro) return null;

  const cfg = stateConfig[macro.state];

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${cfg.bg} ${cfg.pulse ? 'animate-pulse-glow' : ''}`}>
      <span className={`w-2 h-2 rounded-full ${macro.state === 'RISK_ON' ? 'bg-green' : macro.state === 'RISK_OFF' ? 'bg-red' : 'bg-yellow'}`} />
      <span className="text-xs font-semibold tracking-wider uppercase">{cfg.label}</span>
      <span className="text-[10px] text-dim ml-1">
        SBP {macro.sbp_rate}% • USD/PKR {macro.usdpkr}
      </span>
    </div>
  );
}
