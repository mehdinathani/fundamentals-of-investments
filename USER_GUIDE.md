# PSX Investment System — User Guide

Welcome to your PSX (Pakistan Stock Exchange) Investment System. This guide is written for **non-technical users**. No coding knowledge needed.

---

## Table of Contents

1. [What Is This System?](#1-what-is-this-system)
2. [What's Inside](#2-whats-inside)
3. [How to Start the App](#3-how-to-start-the-app)
4. [Dashboard Tour](#4-dashboard-tour)
5. [How to Run the Daily Pipeline](#5-how-to-run-the-daily-pipeline)
6. [How to Log a Trade](#6-how-to-log-a-trade)
7. [How to Close a Trade](#7-how-to-close-a-trade)
8. [How the System Decides What to Buy](#8-how-the-system-decides-what-to-buy)
9. [Use Cases](#9-use-cases)
10. [Tips for Best Results](#10-tips-for-best-results)
11. [Troubleshooting](#11-troubleshooting)
12. [What to Do Daily](#12-what-to-do-daily)

---

## 1. What Is This System?

This is a **decision-support tool** for investing in the Pakistan Stock Exchange (PSX). It does **not** trade automatically. Instead, it:

- **Scans the market** for stocks that match proven buy rules
- **Checks the big picture** (interest rates, USD/PKR, IMF) to decide if now is a good time to trade
- **Tracks every trade** you make so you can see what's working
- **Flags risks** — position size, stop-losses, and when the market regime changes

Think of it as your **co-pilot** — it does the math, you make the final call.

---

## 2. What's Inside

The system has two main parts you interact with:

| Part | What It Is | How You Access It |
|------|-----------|-------------------|
| **Dashboard** | A web page with buttons, tables, and charts | Open `http://localhost:5173` in your browser |
| **Backend (API)** | The brain — does all calculations | Runs automatically when you start the app |

There are also **skill files** (think "instruction manuals for an AI assistant") that encode the trading rules. You don't need to touch these unless you want to change the rules.

---

## 3. How to Start the App

### Step 1: Open a Terminal
On Linux/Mac, open "Terminal". On Windows, open "Command Prompt" or "PowerShell" and navigate to the project folder:
```
cd C:\path\to\psx-skills-creater
```

### Step 2: Run the Start Command
Type this and press Enter:
```
bash start.sh
```

You'll see:
```
Starting PSX Investment System...
[1/2] Starting backend...   ✅ Backend running on http://localhost:8000
[2/2] Starting frontend...  ✅ Frontend running on http://localhost:5173
```

### Step 3: Open the Dashboard
Open your web browser (Chrome, Edge, etc.) and go to:
```
http://localhost:5173
```

That's it. You should see the dashboard with your trade journal, market scan, and macro indicator.

### Step 4: To Stop the App
Press `Ctrl + C` in the terminal window. Both servers will shut down.

---

## 4. Dashboard Tour

When you open `http://localhost:5173`, you'll see a dark-themed dashboard with these sections:

### Top Bar (Header)
- **PSX Invest** — the app name (left side)
- **Macro indicator** (right side) — shows the current market climate:
  - 🟢 **Risk On** — good to trade
  - 🟡 **Neutral** — be careful
  - 🔴 **Risk Off** — stay in cash, don't buy

It also shows the current **SBP interest rate** and **USD/PKR exchange rate**.

### Pipeline Controls (Top Left)
- **Run Pipeline** button — scans all stocks for buy signals
- A small **refresh** button next to it

### Performance Card (Left Column)
Shows your trading stats once you have closed trades:
| Stat | What It Means |
|------|--------------|
| Total Trades | How many trades you've closed |
| Win Rate | % of trades that made money (target: >50%) |
| W/L Ratio | How much you win vs lose (target: >2.0) |
| Net P&L | Total profit or loss in PKR |

### Market Scan (Right, Big Table)
Shows all stocks the system scanned. Each row has:
| Column | What It Means |
|--------|--------------|
| **Symbol** | Stock ticker (e.g., FCCL) |
| **Price** | Current share price |
| **Change** | Today's price change % |
| **RSI** | Momentum indicator (14-day) |
| **ADX** | Trend strength (higher = stronger trend) |
| **Vol** | Volume ratio vs 30-day average (1.2x = 20% above normal) |
| **Signal** | **BUY** (with star for Strong) or — (nothing) |

Use the **All / Signals** toggle at the top to filter.

### Trade Journal (Bottom Section)
Lists every trade you've logged. Shows entry price, exit price, profit/loss, and reason for exiting.

---

## 5. How to Run the Daily Pipeline

The pipeline is the system's main feature. It scans all stocks and tells you which ones have buy signals.

### Daily Routine:
1. Open the dashboard (`http://localhost:5173`)
2. Click the **"Run Pipeline"** button
3. Wait 2-3 seconds
4. The Market Scan table will refresh
5. Look for stocks showing the green **BUY** badge
6. Click the **"Signals"** filter to see only buy candidates

**What the pipeline checks (in order):**
1. **Market Reality** — Is the stock liquid enough to trade? (min 50,000 shares/day)
2. **Fundamentals** — Is the company growing revenue and profits?
3. **Macro overlay** — Is the overall market safe to trade in?
4. **Technical signals** — Does the chart show a buy pattern (breakout + RSI + volume)?
5. **Risk check** — Can your account handle this position?

Stocks that fail any check are skipped with a reason.

---

## 6. How to Log a Trade

When you manually buy a stock, log it so the system can track your performance.

### Method 1: Via API (using curl in terminal)
```bash
curl -X POST http://localhost:8000/api/journal/trades \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "FCCL",
    "entry_date": "2026-05-29",
    "entry_price": 12.50,
    "shares": 2000,
    "entry_signal": "MA crossover + RSI 45 + volume 140%",
    "notes": "Tier 1 signal, macro RISK_ON"
  }'
```

Replace FCCL, the date, price, and shares with your actual trade details.

### Method 2: Via Python (if you have a script)
The API accepts POST requests to `http://localhost:8000/api/journal/trades` with:
```json
{
  "symbol": "YOUR_STOCK",
  "entry_date": "2026-05-29",
  "entry_price": 100.00,
  "shares": 500,
  "entry_signal": "Tier 1 or reason",
  "notes": "Any notes"
}
```

### What to fill in:
| Field | What to put |
|-------|------------|
| `symbol` | Stock ticker (e.g., "ENGRO", "OGDC", "FCCL") |
| `entry_date` | Date you bought (YYYY-MM-DD) |
| `entry_price` | Price per share in PKR |
| `shares` | Number of shares you bought |
| `entry_signal` | Why you bought (e.g., "Tier 1 BUY - Pipeline scan") |
| `notes` | Optional — any thoughts or notes |

---

## 7. How to Close a Trade

When you sell a stock, close the trade so performance metrics update.

Use this command in terminal:
```bash
curl -X PATCH http://localhost:8000/api/journal/trades/1 \
  -H "Content-Type: application/json" \
  -d '{
    "exit_date": "2026-06-15",
    "exit_price": 14.00,
    "exit_reason": "target_hit",
    "pnl_gross": 3000,
    "pnl_net": 2800,
    "fees": 200,
    "notes": "Sold at target. Held 17 days."
  }'
```

Replace `/trades/1` with the trade ID from the journal table.

**Exit reasons you can use:**
| Reason | When |
|--------|------|
| `stop_loss` | Hit your stop-loss (price went against you) |
| `target_hit` | Reached profit target |
| `trailing_stop` | Trailing stop triggered after a gain |
| `ma_sell` | Moving average sell signal fired |
| `rsi_overbought` | RSI > 70 (overbought) |
| `manual_override` | You decided to exit for your own reasons |
| `time_stop` | Position held too long without progress |
| `tax_loss_harvest` | Selling for tax purposes (Q4) |

---

## 8. How the System Decides What to Buy

The system uses **4 layers** of checks. Every stock must pass all 4 to get a BUY signal.

### Layer 0: Market Reality (Can I trade this stock?)
- Volume > 50,000 shares/day (liquid enough)
- Price spread < 2% (not too wide)
- No pump-and-dump patterns

### Layer 1: Fundamentals (Is this a good company?)
- Revenue growing > 8% per year
- Profits growing > 10% per year
- Debt is manageable (D/E < 0.6)
- Profitable in at least 3 of last 4 quarters

### Layer 1.5: Macro Climate (Is now a good time?)
- **Risk On**: Green light — full trading allowed
- **Neutral**: Yellow light — be selective
- **Risk Off**: Red light — prefer cash or defensive stocks
- Also checks: SBP interest rate, USD/PKR trend, IMF program status

### Layer 2: Technical Signals (Is the chart saying BUY?)
- Stock is breaking out above recent highs
- RSI between 50-65 (momentum, not overbought)
- ADX > 20 (trend is strong enough)
- Volume > 120% of normal (confirms the move)

### Layer 3: Risk Management (Can I afford this?)
- Max 5% loss per trade (you never lose more than 5% of your account on one trade)
- Max 10% of account in one stock (diversified)
- Min 30% cash reserve (always have cash ready)
- Max 7 positions at a time
- Stop-loss is set immediately

---

## 9. Use Cases

### Use Case 1: Daily Morning Scan
**What:** Before the market opens, get your watchlist of stocks with BUY signals.
**How:** Click "Run Pipeline" → review the signals → check the macro indicator → plan your day.

### Use Case 2: Validate a Potential Buy
**What:** You hear about a stock and want the system's opinion.
**How:** Check if it passes the layers. Look it up in the Market Scan table.

### Use Case 3: Track Your Performance
**What:** See if your trading is actually working.
**How:** Log every trade you make. Check the Performance card after 10-20 closed trades.

### Use Case 4: Spot Regime Changes
**What:** The market conditions change suddenly.
**How:** Check the macro indicator. If it switches from green to red, stop buying new positions.

### Use Case 5: Learn Your Patterns
**What:** Discover which types of trades work best for you.
**How:** Review the Trade Journal monthly. Look for patterns — which sectors, which tiers, which exit reasons.

---

## 10. Tips for Best Results

### DO:
- ✅ **Run the pipeline daily** before making any buy decisions
- ✅ **Log every trade** — even the small ones. Data = learning
- ✅ **Check the macro indicator first** — don't buy in Risk Off
- ✅ **Set stop-losses** on every trade before you enter
- ✅ **Keep cash reserve ≥ 30%** — opportunities come to those with cash
- ✅ **Review your journal monthly** — what worked, what didn't
- ✅ **Trust the system when it says no signals** — no trade is better than a bad trade
- ✅ **Log the exit reason accurately** — it helps you spot patterns

### DON'T:
- ❌ Don't buy a stock that doesn't have volume confirmation (≥ 120% of normal)
- ❌ Don't move your stop-loss down (only trail it up)
- ❌ Don't average down on losing positions
- ❌ Don't revenge trade after a loss
- ❌ Don't exceed 7 positions at once
- ❌ Don't put more than 10% of your account in one stock
- ❌ Don't force a trade when there are no signals
- ❌ Don't trade without checking the macro overlay first

---

## 11. Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| **Dashboard won't load** | App not started | Run `bash start.sh` in the project folder |
| **"No trades recorded"** | Haven't logged any trades yet | Use the API to log your first trade (see Section 6) |
| **"No closed trades yet"** | All trades are still open | Close a trade via PATCH API (see Section 7) |
| **Pipeline shows 0 signals** | No stocks meet all criteria | That's OK — check macro state. May be Risk Off. |
| **"Failed to fetch" error** | Backend not running | Check terminal — is uvicorn still running? |
| **Port already in use** | Another app on same port | Kill the old process or change the port |
| **Macro shows UNKNOWN** | No historical data loaded | Run the macro setup script first |

### How to Check if Servers Are Running:
Open these in your browser:
- Backend health: `http://localhost:8000/api/health` (should show `{"status":"ok"}`)
- Any trade: `http://localhost:8000/api/journal/trades` (should show your trades)

---

## 12. What to Do Daily

### Morning Routine (5 minutes)
```
☐ Open dashboard: http://localhost:5173
☐ Check macro indicator (green/yellow/red)
☐ Click "Run Pipeline"
☐ Review buy signals
☐ Plan trades for the day
```

### After a Trade (2 minutes)
```
☐ Log entry via API (symbol, price, shares, reason)
☐ Set stop-loss in your brokerage
☐ Note exit target
```

### Weekly Review (10 minutes)
```
☐ Review open positions
☐ Check trailing stops
☐ Count entries this week (max 2)
```

### Monthly Review (15 minutes)
```
☐ Review closed trades
☐ Check performance metrics (win rate, P&L)
☐ Spot patterns — what's working?
☐ Run the backtester if win rate is below 40%
```

---

*This system is a decision-support tool. It does not provide financial advice. All trading involves risk — never trade money you cannot afford to lose.*
