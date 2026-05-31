import type { MacroState, ScanResult, Trade, Performance, PipelineStatus } from '../types';

const BASE = '/api';

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

export const api = {
  // Market
  scanMarket: (macroState?: string) => {
    const params = macroState ? `?macro_state=${macroState}` : '';
    return fetchJSON<ScanResult>(`/market/scan${params}`);
  },
  getSymbol: (symbol: string) => fetchJSON<any>(`/market/symbol/${symbol}`),

  // Macro
  getMacroState: () => fetchJSON<MacroState>('/macro/state'),
  refreshMacro: () => fetchJSON<{ status: string; state: string }>('/macro/refresh', { method: 'POST' }),

  // Pipeline
  runPipeline: () => fetchJSON<any>('/pipeline/run', { method: 'POST' }),
  getPipelineStatus: () => fetchJSON<PipelineStatus>('/pipeline/status'),

  // Journal
  getTrades: (symbol?: string) => {
    const params = symbol ? `?symbol=${symbol}` : '';
    return fetchJSON<Trade[]>(`/journal/trades${params}`);
  },
  getOpenTrades: () => fetchJSON<Trade[]>('/journal/trades/open'),
  addTrade: (trade: Partial<Trade>) =>
    fetchJSON<Trade>('/journal/trades', { method: 'POST', body: JSON.stringify(trade) }),
  closeTrade: (id: number, update: Partial<Trade>) =>
    fetchJSON<Trade>(`/journal/trades/${id}`, { method: 'PATCH', body: JSON.stringify(update) }),
  getPerformance: () => fetchJSON<Performance>('/journal/performance'),
};
