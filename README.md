---
title: Orion Trading Environment
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
tags:
  - openenv
  - trading
  - reinforcement-learning
  - indian-markets
  - nse
---

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=200&section=header&text=Orion%20Trading%20Environment&fontSize=52&fontColor=ffffff&fontAlignY=42&desc=Indian%20NSE%20Equity%20Trading%20·%20Reinforcement%20Learning%20·%20OpenEnv&descAlignY=62&descSize=16&animation=fadeIn" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-6a85b6?style=for-the-badge)](https://github.com/meta-pytorch/OpenEnv)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

> *A realistic Indian NSE equity trading simulation — where LLMs learn to trade under real market conditions, taxes, and brokerage costs.*

</div>

---

## 🌐 Live Demo

👉 **[itsashishthakurr/orion-trading-simulation](https://huggingface.co/spaces/itsashishthakurr/orion-trading-simulation)**

---

## 🔥 What is Orion?

**Orion** is an OpenEnv-compliant reinforcement learning environment that simulates **real Indian NSE equity trading** — the kind that every retail investor in India actually faces.

Most trading RL environments ignore the costs that destroy real returns. Orion doesn't.

The agent manages a portfolio across dynamic market regimes and must reason about:

- **Market regime** — Bull, Bear, Sideways, or Volatile
- **Real transaction costs** — 0.3% brokerage (min ₹3 per trade)
- **Indian taxation** — STCG at 20% on short-term profits
- **DP charges** — ₹15 per SELL on Hard difficulty
- **Capital preservation** — knowing when to do nothing is a skill

---

## 🧠 Why This Environment Is Hard

Most LLMs can do basic sentiment analysis. Orion tests something harder:

| Challenge | What the LLM must learn |
| :--- | :--- |
| **Regime Detection** | Distinguish bull momentum from volatile chop |
| **Cost Awareness** | Factor in brokerage + tax before trading |
| **Capital Preservation** | Recognise sideways markets and HOLD |
| **Loss Cutting** | Exit losing positions before they compound |
| **End-of-Episode Urgency** | Sell holdings before the episode ends |

A model that blindly buys in every bull signal will lose to brokerage. A model that holds too long pays tax on gains it never realised. **Orion rewards disciplined, cost-aware decisions — not noise.**

---

## 📋 Tasks and Difficulty

| Task | Difficulty | Steps | Max Holdings | Tax | DP Charge | Core Challenge |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `easy` | 🟢 Easy | 50 | 12 | ❌ None | ❌ No | Follow bull/bear regimes cleanly |
| `medium` | 🟡 Medium | 100 | 8 | ✅ STCG 20% | ❌ No | Trade profitably after tax |
| `hard` | 🔴 Hard | 150 | 5 | ✅ STCG 20% | ✅ ₹15/sell | Survive high volatility + full costs |

---

## 👁️ Observation Space

Each step the agent receives a **rich natural language market report** — designed to give LLMs exactly the signal they need to reason correctly:

```
Market Report - NSE Simulation (Step 12/50):

[MARKET]
Regime: BULLISH (strong, confidence 0.82)
Price: Rs.512.40  |  Change: +0.84%
Momentum: 0.71  (>0.5 = upward, <0.5 = downward)
Volatility: 0.50

[PORTFOLIO]
Cash Balance: Rs.8943.20
Holdings: 2 units (max allowed: 12)
Avg Buy Price: Rs.498.60
Portfolio Value: Rs.9968.00
Overall P&L: Rs.968.00 PROFIT (+9.68% vs start)
Unrealised: Rs.27.60 unrealised gain (+2.77% per unit)

[COSTS]
Brokerage: 0.3% per trade (min Rs.3) | Tax: None (easy mode)

[EPISODE]
Steps Remaining: 38
Status: Normal

Decide your next action: BUY, SELL, or HOLD.
```

---

## ⚡ Action Space

Three discrete actions — simple enough for any LLM to produce, hard enough to require real reasoning:

| Action | Effect | When to use |
| :--- | :--- | :--- |
| `BUY` | Buy 1 unit at current price + brokerage | Bull regime, price trending up |
| `SELL` | Sell 1 unit, deduct brokerage + tax + DP | Bear regime, profit-taking, loss-cutting |
| `HOLD` | Do nothing — no cost | Sideways, volatile, or uncertain |

---

## 🏆 Reward System

Every step reward is **strictly inside (0.01, 0.99)** — never exactly 0 or 1.

```
base = 0.50 + (portfolio_change_pct × 5.0)

Bonuses:
  + BUY  in BULL regime      → +0.05
  + SELL in BEAR regime      → +0.05
  + HOLD in SIDEWAYS         → +0.03
  + SELL above avg_buy × 1.02 → +0.04

Penalties:
  - BUY  in BEAR regime      → -0.05
  - SELL in BULL (when holding) → -0.03
  - Invalid action            → -0.10
  - Overtrading churn         → -0.01

Final: max(0.01, min(0.99, base))
```

**Final episode score** = `0.70 × profit_score + 0.20 × consistency_score + 0.10 × behavior_score`

---

## 📊 Benchmark Results

*Evaluated on 50-step episodes (Easy task). Scores represent Mean Reward [0.01 – 0.99].*

<!-- BENCHMARK TABLE — paste your results here after running inference.py against each model -->

| Model | Easy | Medium | Hard | Overall | Result |
| :--- | :---: | :---: | :---: | :---: | :---: |
| *(run inference.py to fill this table)* | — | — | — | — | — |

---

### 📸 Benchmark Screenshot

<!-- Replace the line below with your actual screenshot after running -->
> **Drop your benchmark screenshot here.**
> Run `python inference.py` with 3–5 different models, capture the `[SUMMARY]` output, and paste the image.

```
Coming soon — benchmark run in progress
```

---

## 🤖 Built-in Agents (Local Simulation)

Three agents are included for local testing and benchmarking via `python main.py`:

| Agent | Strategy | Best at |
| :--- | :--- | :--- |
| `RandomAgent` | Random BUY/SELL/HOLD | Baseline chaos |
| `SmartAgent` | Regime + profit/loss rules | Consistent, no learning needed |
| `LearningAgent` | Q-Learning (tabular RL) | Improves over 20,000 training episodes |

---

## 🏗️ Project Structure

```
Orion-RL-Trading-Env/
│
├── server/
│   └── app.py               # FastAPI server — all OpenEnv endpoints
│
├── env/
│   ├── environment.py        # Core RL loop: reset(), step()
│   ├── market.py             # Price simulation: 4 regimes, volatility scaling
│   ├── step_manager.py       # BUY/SELL/HOLD execution + costs
│   ├── reset_manager.py      # Episode initialisation
│   └── reward.py             # Reward computation, strictly (0.01, 0.99)
│
├── core/
│   ├── config.py             # Env-var tunable config (ORION_*)
│   ├── models.py             # OrionState, RewardResult dataclasses
│   ├── observation_builder.py # Rich text observation for LLM
│   └── utils.py              # clamp(), calculate_brokerage()
│
├── agents/
│   ├── base_agent.py         # BaseAgent ABC
│   ├── random_agent.py       # Random baseline
│   ├── smart_agent.py        # Rule-based agent
│   └── learning_agent.py     # Q-Learning agent
│
├── tasks/
│   └── tasks.py              # Task definitions: easy, medium, hard
│
├── simulation/
│   ├── runner.py             # Episode runner + grader integration
│   └── benchmark.py          # Run all agents across all tasks
│
├── grader.py                 # Deterministic score: profit + consistency + behavior
├── leaderboard.py            # Terminal leaderboard display
├── inference.py              # OpenEnv validator script — LLM agent loop
├── main.py                   # Local demo: python main.py
├── openenv.yaml              # OpenEnv manifest
├── Dockerfile                # Container for HuggingFace Spaces
├── requirements.txt
└── pyproject.toml
```

---

## 🚀 Quick Start

### Run locally (no LLM needed)

```bash
git clone https://huggingface.co/spaces/itsashishthakurr/orion-trading-simulation
cd Orion-RL-Trading-Env

pip install -r requirements.txt

# Run all 3 agents across all 3 difficulties
python main.py

# Run a specific difficulty
python main.py --difficulty easy
```

### Start the API server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

### Run LLM inference

```bash
export HF_TOKEN=hf_your_token_here
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export ENV_BASE_URL=http://localhost:7860

python inference.py
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/health` | GET | Liveness check |
| `/reset` | POST | Start new episode `{"task": "easy"}` |
| `/step` | POST | Take one action `{"action": "BUY"}` |
| `/state` | GET | Current environment state snapshot |
| `/tasks` | GET | List all available tasks |
| `/grader` | GET | Current episode score (0.01–0.99) |

### Example: `/reset`

```json
POST /reset
{ "task": "medium" }

→ {
    "observation": "Market Report - NSE Simulation...",
    "task": "medium",
    "max_steps": 100,
    "info": { "price": 500.0, "balance": 10000.0, "holdings": 0, "regime": "sideways" }
  }
```

### Example: `/step`

```json
POST /step
{ "action": "BUY" }

→ {
    "observation": "Market Report...",
    "reward": 0.5300,
    "done": false,
    "info": { "price": 503.2, "balance": 9495.3, "holdings": 1, "regime": "bull", ... }
  }
```

---

## ⚙️ Environment Variables

All tuneable without code changes:

```bash
ORION_STARTING_BALANCE=10000   # starting cash in Rs.
ORION_VOLATILITY=1.0           # market volatility multiplier
PORT=7860                      # server port
```

---

## 🛠️ Tech Stack

```python
stack = {
    "Language":    "Python 3.10+",
    "Framework":   "FastAPI + Uvicorn",
    "RL":          "Custom Q-Learning + Rule-based agents",
    "Market":      "Stochastic regime-switching simulation",
    "Taxes":       "Indian STCG 20%, LTCG 12.5%, DP charges",
    "API":         "OpenEnv-compliant REST",
    "Deploy":      "HuggingFace Spaces (Docker)",
}
```

---

## 🇮🇳 Why Indian Markets?

Most RL trading environments use generic US equity models with no realistic costs.

India's NSE has **specific friction** that changes the entire problem:

- **STCG at 20%** on short-term profits — a model that churns loses money even if it picks direction correctly
- **DP charges (₹15–20 per SELL)** — small positions become loss-making to exit
- **Minimum brokerage** — trading ₹100 stocks with ₹3 minimum brokerage is 3% cost per trade
- **Regime volatility** — NIFTY50 is more volatile than the S&P500 relative to its trend

No other project in this competition models these constraints. **Orion is the only environment where the cost structure itself is a core part of the RL problem.**

---

## 👤 Author

**Ashish Thakur**

- HuggingFace: [itsashishthakurr](https://huggingface.co/itsashishthakurr)

---

<div align="center">

*Built for the Meta × Scaler OpenEnv Hackathon 2026*

</div>