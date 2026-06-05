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
