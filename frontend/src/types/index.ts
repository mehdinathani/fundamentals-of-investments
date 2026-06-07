export interface MacroState {
  state: 'RISK_ON' | 'NEUTRAL' | 'RISK_OFF';
  date: string;
  sbp_rate: number | null;
  usdpkr: number | null;
  imf_status: string | null;
  kse100_pe: number | null;
}

export interface SymbolData {
  symbol: string;
  current_price: number | null;
  prev_close: number | null;
  change_pct: number;
  ma20: number | null;
  ma50: number | null;
  ma200: number | null;
  rsi: number | null;
  volume_ratio: number | null;
  adx: number | null;
  breakout: boolean;
  signal: 'BUY' | null;
  signal_strength: string | null;
  macro_state: string;
  date: string;
}

export interface SymbolDetail extends SymbolData {
  macro: MacroState;
}

export interface ScanResult {
  total_scanned: number;
  buy_signals: number;
  macro_state: string;
  symbols: SymbolData[];
}

export interface Trade {
  id: number;
  symbol: string;
  direction: 'LONG' | 'SHORT';
  entry_date: string;
  entry_price: number;
  exit_date: string | null;
  exit_price: number | null;
  shares: number;
  entry_signal: string | null;
  exit_reason: string | null;
  pnl_gross: number | null;
  pnl_net: number | null;
  fees: number | null;
  notes: string | null;
  created_at: string | null;
}

export interface Performance {
  total_trades: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  win_loss_ratio: number;
  expectancy: number;
  total_pnl_net: number;
}

export interface PipelineStatus {
  status: string;
  id?: number;
  started_at?: string;
  completed_at?: string;
  symbols_scanned?: number;
  signals_generated?: number;
  macro_state?: string;
  error?: string;
}

export interface BenchmarkComparison {
  median: number | null;
  deviation_pct: number | null;
  verdict: string | null;
  sector_name?: string;
  count?: number;
  symbols_in_sector?: number;
}

export interface RatioComparison {
  value: number | null;
  name: string;
  comparisons: Record<string, BenchmarkComparison>;
  percentile_rank?: number | null;
}

export interface ComparisonResult {
  symbol: string;
  sector: string | null;
  sector_peers: string[];
  sector_data_available: boolean;
  price: number | null;
  ratios: Record<string, RatioComparison>;
}

export interface AIActionPlan {
  entry_zone: string;
  stop_loss: string;
  target_1: string;
  target_2: string;
  position_sizing: string;
}

export interface AIAnalysisResult {
  symbol: string;
  verdict: 'BUY' | 'SELL' | 'SHORT_SELL' | 'BUY_BACK' | 'STOP_LOSS' | 'HOLD';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  time_horizon: string;
  executive_summary: string;
  fundamental_analysis: string;
  technical_analysis: string;
  macro_context: string;
  risk_factors: string[];
  action_plan: AIActionPlan;
  peer_comparison: string;
  generated_at: string | null;
  ai_available: boolean;
}
