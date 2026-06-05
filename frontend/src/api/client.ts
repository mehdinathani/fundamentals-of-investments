import type { MacroState, ScanResult, Trade, Performance, PipelineStatus } from '../types';

// Dev: Vite proxy handles /api -> localhost:8000
// Production: VITE_API_URL points to the Render backend
const BASE = import.meta.env.VITE_API_URL ?? '/api';

let _auth: string | null = null;

export function setAuth(user: string, pass: string) {
  _auth = btoa(`${user}:${pass}`);
}

export function clearAuth() {
  _auth = null;
}

export function isAuthed(): boolean {
  return _auth !== null;
}

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (_auth) {
    headers['Authorization'] = `Basic ${_auth}`;
  }
  const res = await fetch(`${BASE}${url}`, {
    headers,
    ...opts,
  });
  if (res.status === 401) {
    clearAuth();
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

export async function login(user: string, pass: string): Promise<void> {
  const headers: Record<string, string> = {};
  headers['Authorization'] = `Basic ${btoa(`${user}:${pass}`)}`;
  const res = await fetch(`${BASE}/auth/login`, { method: 'POST', headers });
  if (!res.ok) throw new Error('Invalid credentials');
  setAuth(user, pass);
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
