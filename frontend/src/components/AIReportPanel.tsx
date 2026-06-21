import { useState } from 'react';
import type { AIAnalysisResult } from '../types';
import { ChevronDown, ChevronRight, AlertTriangle, Target, TrendingUp, BarChart3, Globe } from 'lucide-react';
import VerdictGauge from './VerdictGauge';

interface Props {
  analysis: AIAnalysisResult;
}

const VERDICT_STYLES: Record<string, { bg: string; border: string; text: string; label: string }> = {
  BUY: { bg: 'bg-green-900/30', border: 'border-green/40', text: 'text-green', label: 'BUY' },
  SELL: { bg: 'bg-red-900/30', border: 'border-red/40', text: 'text-red', label: 'SELL' },
  SHORT_SELL: { bg: 'bg-red-900/30', border: 'border-red/40', text: 'text-red', label: 'SHORT SELL' },
  BUY_BACK: { bg: 'bg-green-900/30', border: 'border-green/40', text: 'text-green', label: 'BUY BACK' },
  STOP_LOSS: { bg: 'bg-yellow-900/30', border: 'border-yellow/40', text: 'text-yellow', label: 'STOP LOSS' },
  HOLD: { bg: 'bg-navy-700', border: 'border-navy-500', text: 'text-dim', label: 'HOLD' },
  IGNORE: { bg: 'bg-navy-900', border: 'border-navy-700', text: 'text-dim', label: 'IGNORE' },
};

function Section({ title, icon, children, defaultOpen }: { title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen ?? true);
  return (
    <div className="border border-navy-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-3 py-2 bg-navy-800/50 hover:bg-navy-700/50 transition-colors text-left"
      >
        {open ? <ChevronDown className="w-3.5 h-3.5 text-dim" /> : <ChevronRight className="w-3.5 h-3.5 text-dim" />}
        {icon}
        <span className="text-xs font-semibold text-dim uppercase tracking-wider">{title}</span>
      </button>
      {open && <div className="px-3 py-2.5 text-sm text-white/90 leading-relaxed">{children}</div>}
    </div>
  );
}

export default function AIReportPanel({ analysis }: Props) {
  const vs = VERDICT_STYLES[analysis.verdict] ?? VERDICT_STYLES.HOLD;

  return (
    <div className="space-y-3">
      {!analysis.ai_available && (
        <div className="flex items-center gap-2 px-3 py-2 bg-yellow-900/20 border border-yellow/30 rounded-lg text-xs text-yellow">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          AI analysis unavailable. Add GEMINI_API_KEY to .env to enable.
        </div>
      )}

      <div className={`${vs.bg} ${vs.border} border rounded-lg p-4`}>
        <VerdictGauge verdict={analysis.verdict} confidence={analysis.confidence} />
        <div className="text-[10px] text-dim text-center mt-1">{analysis.time_horizon}</div>
      </div>

      <div className="text-sm text-white/90 px-1">{analysis.executive_summary}</div>

      <Section title="Fundamental Analysis" icon={<BarChart3 className="w-3.5 h-3.5 text-blue" />}>
        {analysis.fundamental_analysis}
      </Section>

      <Section title="Technical Analysis" icon={<TrendingUp className="w-3.5 h-3.5 text-green" />}>
        {analysis.technical_analysis}
      </Section>

      <Section title="Macro Context" icon={<Globe className="w-3.5 h-3.5 text-purple" />}>
        {analysis.macro_context}
      </Section>

      <Section title="Risk Factors" icon={<AlertTriangle className="w-3.5 h-3.5 text-red" />} defaultOpen={false}>
        <ul className="list-disc list-inside space-y-1">
          {analysis.risk_factors.map((r, i) => (
            <li key={i} className="text-sm text-red/80">{r}</li>
          ))}
        </ul>
      </Section>

      <Section title="Action Plan" icon={<Target className="w-3.5 h-3.5 text-gold" />}>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-navy-900 rounded p-2">
            <div className="text-[10px] text-dim uppercase tracking-wider">Entry Zone</div>
            <div className="font-mono text-gold">{analysis.action_plan.entry_zone}</div>
          </div>
          <div className="bg-navy-900 rounded p-2">
            <div className="text-[10px] text-dim uppercase tracking-wider">Stop Loss</div>
            <div className="font-mono text-red">{analysis.action_plan.stop_loss}</div>
          </div>
          <div className="bg-navy-900 rounded p-2">
            <div className="text-[10px] text-dim uppercase tracking-wider">Target 1</div>
            <div className="font-mono text-green">{analysis.action_plan.target_1}</div>
          </div>
          <div className="bg-navy-900 rounded p-2">
            <div className="text-[10px] text-dim uppercase tracking-wider">Target 2</div>
            <div className="font-mono text-green">{analysis.action_plan.target_2}</div>
          </div>
        </div>
      </Section>

      <div className="text-xs text-dim px-1 pt-1 border-t border-navy-700">
        {analysis.peer_comparison}
      </div>

      {analysis.generated_at && (
        <div className="text-[10px] text-dim/60 px-1">
          Generated: {new Date(analysis.generated_at).toLocaleString()}
        </div>
      )}
    </div>
  );
}
