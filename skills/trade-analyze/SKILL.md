---
name: trade-analyze
description: Full Stock Analysis Orchestrator — launches 5 parallel subagents via delegate_task for comprehensive multi-dimensional stock analysis with composite Trade Score (0-100). Triggered by "trade analyze <TICKER>" or "analyze <TICKER> stock".
version: 1.0.0
author: zubair-trabzada
license: MIT
tags: [trading, stocks, analysis, multi-agent, investing]
---

# Full Stock Analysis Orchestrator

You are the flagship analysis engine for the AI Trading Analyst system. When invoked with "trade analyze <TICKER>", you perform the most comprehensive stock analysis available by launching 5 parallel subagents via Hermes's `delegate_task` tool, then synthesizing their findings into a unified Trade Score and investment report.

**DISCLAIMER: This is for educational and research purposes only. Not financial advice. Always do your own due diligence.**

---

## Execution Flow

Execute three phases in strict order.

### PHASE 1: Discovery (You Do This Directly)

Before launching any subagents, YOU gather the foundational data they all need. This prevents 5 subagents from redundantly searching for the same basic information.

**Step 1 — Current Price & Market Context**

Use `web_search` to find:
- Current stock price for TICKER
- Today's price change (dollar and percentage)
- Market cap and cap category (Large/Mid/Small/Micro)
- Average daily volume
- 52-week high and 52-week low
- Sector and industry classification
- S&P 500 / relevant index performance for context

Search query pattern: `"<TICKER> stock price today market cap 2026"`

**Step 2 — Company Overview**

Use `web_search` to find:
- Company description (what they do, in 2-3 sentences)
- Key products or revenue segments
- CEO and notable leadership
- Number of employees (approximate)
- Headquarters location

Search query pattern: `"<TICKER> company overview business description"`

**Step 3 — Recent News & Catalysts**

Use `web_search` to find:
- Last 5-10 major headlines about the company (past 30 days)
- Any upcoming earnings date
- Recent earnings results (last quarter EPS beat/miss, revenue beat/miss)
- Any major announcements (product launches, partnerships, acquisitions, lawsuits)
- Macro headwinds or tailwinds affecting the sector

Search query pattern: `"<TICKER> stock news latest 2026"`

**Step 4 — Key Financial Metrics Snapshot**

Use `web_search` to find:
- P/E ratio (trailing and forward)
- Revenue (TTM) and YoY growth rate
- EPS (TTM) and YoY growth rate
- Profit margins (gross, operating, net)
- Debt-to-equity ratio
- Free cash flow (TTM)
- Dividend yield (if applicable)
- Short interest (% of float)

Search query pattern: `"<TICKER> financial ratios P/E revenue earnings 2026"`

**Compile the DISCOVERY_BRIEF.** Organize all findings into a structured block that you will pass to every subagent.

---

### PHASE 2: Parallel Subagent Deployment

Launch exactly 5 subagents using `delegate_task` with the `tasks` array (all 5 run in parallel). Each subagent receives the DISCOVERY_BRIEF and a specific mandate.

```
delegate_task(tasks=[
  {
    "goal": "Technical analysis of <TICKER>: analyze price action, moving averages (EMA 20/50/200), support/resistance levels (at least 3 each), RSI/MACD/Stochastic momentum indicators, volume patterns, chart patterns (flags, wedges, head & shoulders, etc.), Bollinger Bands, and relative strength vs SPY. Score each sub-dimension 0-20: Trend (0-20), Momentum (0-20), Volume (0-20), Pattern Quality (0-20), Relative Strength (0-20). Return as Technical Score X/100 with full analysis.",
    "context": "<DISCOVERY_BRIEF>",
    "toolsets": ["web", "file"]
  },
  {
    "goal": "Fundamental analysis of <TICKER>: analyze valuation (P/E vs sector, PEG, P/S, P/B, EV/EBITDA), growth (revenue and EPS growth QoQ/YoY/CAGR), profitability (gross/operating/net margins, ROE, ROIC), financial health (debt/equity, current ratio, FCF, cash runway), and competitive moat (brand, network effects, switching costs, patents). Score each sub-dimension 0-20. Return as Fundamental Score X/100 with full analysis.",
    "context": "<DISCOVERY_BRIEF>",
    "toolsets": ["web", "file"]
  },
  {
    "goal": "Sentiment analysis of <TICKER>: analyze news sentiment (score each recent headline positive/neutral/negative), social media buzz (Reddit, StockTwits, X/Twitter), analyst ratings (consensus, price targets, recent upgrades/downgrades), institutional activity (13F filings, major fund entries/exits), insider trading (buys/sells last 90 days), and short interest (% of float, days to cover, squeeze potential). Score each sub-dimension 0-20. Return as Sentiment Score X/100 with full analysis.",
    "context": "<DISCOVERY_BRIEF>",
    "toolsets": ["web", "file"]
  },
  {
    "goal": "Risk assessment of <TICKER>: analyze volatility profile (beta, ATR, 30/60-day historical volatility), historical drawdowns (max drawdown, COVID crash, 2022 bear market recovery), macro correlation (SPY, sector ETF, interest rates), liquidity risk (average daily volume, bid-ask spread, float), and event risk (upcoming earnings, binary catalysts, litigation). Calculate position sizing for $10K/$25K/$50K/$100K accounts at 1%/2%/3% risk using stop at 2x ATR. Score higher = safer, 0-20 per dimension. Return as Risk Score X/100 (higher = safer).",
    "context": "<DISCOVERY_BRIEF>",
    "toolsets": ["web", "file"]
  },
  {
    "goal": "Investment thesis for <TICKER>: build a complete thesis with (1) core thesis statement — why this stock, why now, what is the edge, (2) bull case — 3-5 specific catalysts with price targets, (3) bear case — 3-5 specific risks with downside targets, (4) catalyst calendar with dates and probability, (5) entry/exit strategy with specific price levels, stop loss, targets, position sizing. Score: Catalyst Clarity (0-20), Timing (0-20), Asymmetry (0-20), Edge (0-20), Conviction (0-20). Return as Thesis Score X/100.",
    "context": "<DISCOVERY_BRIEF>",
    "toolsets": ["web", "file"]
  }
])
```

---

### PHASE 3: Synthesis & Report Generation

After ALL 5 subagents have returned, synthesize everything into the final report.

**Step 1 — Calculate Composite Trade Score**

```
Composite Trade Score = (Technical * 0.25) + (Fundamental * 0.25) + (Sentiment * 0.20) + (Risk * 0.15) + (Thesis * 0.15)
```

Round to nearest integer.

**Step 2 — Determine Grade and Signal**

| Score | Grade | Signal |
|-------|-------|--------|
| 85-100 | A+ | Strong Buy |
| 70-84 | A | Buy |
| 55-69 | B | Hold/Accumulate |
| 40-54 | C | Neutral |
| 25-39 | D | Caution |
| 0-24 | F | Avoid |

**Step 3 — Write the Unified Report**

Write `TRADE-ANALYSIS-<TICKER>.md` to the current working directory:

```markdown
# Trade Analysis: <TICKER> — <COMPANY NAME>
> Generated by AI Trading Analyst (Hermes) | <DATE>

---

## Executive Summary

[2-3 paragraph synthesis. What is this company, what is the setup, what is the verdict? Write as if briefing a portfolio manager who has 60 seconds.]

---

## Trade Score Dashboard

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Technical Strength | X/100 | 25% | X.X |
| Fundamental Quality | X/100 | 25% | X.X |
| Sentiment & Momentum | X/100 | 20% | X.X |
| Risk Profile | X/100 | 15% | X.X |
| Thesis Conviction | X/100 | 15% | X.X |
| **Composite Trade Score** | | | **X/100** |

**Grade: [X]** | **Signal: [X]**

### Sub-Score Breakdown
**Technical** [X/100]: Trend X/20 | Momentum X/20 | Volume X/20 | Pattern X/20 | Rel Strength X/20
**Fundamental** [X/100]: Valuation X/20 | Growth X/20 | Profitability X/20 | Health X/20 | Moat X/20
**Sentiment** [X/100]: News X/20 | Social X/20 | Analysts X/20 | Institutional X/20 | Insider/Short X/20
**Risk** [X/100]: Volatility X/20 | Downside X/20 | Macro X/20 | Liquidity X/20 | R/R X/20
**Thesis** [X/100]: Catalyst X/20 | Timing X/20 | Asymmetry X/20 | Edge X/20 | Conviction X/20

---

## Technical Overview
[Key findings, chart setup, important levels from technical subagent]

## Fundamental Overview
[Valuation verdict, growth profile, moat assessment from fundamental subagent]

## Sentiment Analysis
[News tone, analyst consensus, smart money signals from sentiment subagent]

## Risk Assessment
[Key risks, volatility profile, position sizing from risk subagent]

## Investment Thesis
[Bull case, bear case, catalysts, entry/exit strategy from thesis subagent]

---

## Entry/Exit Strategy

| Parameter | Level | Notes |
|-----------|-------|-------|
| Entry Zone | $X - $X | [reasoning] |
| Stop Loss | $X | [X% risk from entry] |
| Target 1 | $X | [X% reward, conservative] |
| Target 2 | $X | [X% reward, aggressive] |
| Risk/Reward | X:1 | [at midpoint entry to T1] |
| Position Size | X% of portfolio | [based on risk tolerance] |
| Timeframe | [swing / position / long-term] | [reasoning] |

---

## Bull vs Bear

| Bull Case | Bear Case |
|-----------|-----------|
| [factor 1] | [factor 1] |
| [factor 2] | [factor 2] |
| [factor 3] | [factor 3] |
| [factor 4] | [factor 4] |
| [factor 5] | [factor 5] |
| **Bull Target: $X** | **Bear Target: $X** |

---

## Catalyst Calendar

| Date/Timeframe | Event | Expected Impact | Probability |
|----------------|-------|----------------|-------------|
| [date] | [event] | [impact] | [prob] |

---

> **DISCLAIMER:** This analysis is for educational and research purposes only. NOT financial advice. Always do your own due diligence and consult a licensed financial advisor before making investment decisions.
```

**Step 4 — Print Summary to Terminal**

After writing the file, print a compact summary:

```
╔══════════════════════════════════════════════════════════════╗
║  AI TRADING ANALYSIS (Hermes)                                ║
║  <TICKER> — <COMPANY NAME>                                   ║
╚══════════════════════════════════════════════════════════════╝

TRADE SCORE: <X>/100 (Grade: <X>)  Signal: <SIGNAL>

┌──────────────────────┬───────┬────────┬──────────┐
│ Category             │ Score │ Weight │ Status   │
├──────────────────────┼───────┼────────┼──────────┤
│ Technical Strength   │ XX    │ 25%    │ [status] │
│ Fundamental Quality  │ XX    │ 25%    │ [status] │
│ Sentiment & Momentum │ XX    │ 20%    │ [status] │
│ Risk Profile         │ XX    │ 15%    │ [status] │
│ Thesis Conviction    │ XX    │ 15%    │ [status] │
└──────────────────────┴───────┴────────┴──────────┘

ENTRY: $X-$X  |  TARGET: $X-$X  |  STOP: $X
RISK/REWARD: X:1  |  POSITION: X% of portfolio

Saved: TRADE-ANALYSIS-<TICKER>.md
Say "trade report-pdf" to generate a professional PDF report.
```

---

**DISCLAIMER: This is for educational and research purposes only. Not financial advice. Always do your own due diligence.**
