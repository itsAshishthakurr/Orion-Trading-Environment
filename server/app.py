"""
server/app.py — Orion Trading Environment FastAPI Server

Endpoints required by the OpenEnv validator:
  GET  /health   → liveness check
  POST /reset    → start new episode, returns observation text
  POST /step     → take one action, returns observation + reward + done
  GET  /state    → current environment state snapshot
  GET  /tasks    → list all available tasks
  GET  /grader   → current episode grader scores (all three tasks)

All reward values returned are strictly in (0.01, 0.99).
"""

import os
import sys

# ── Make sure imports resolve whether run from root or server/ ────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from typing import Optional

import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from env.environment import TradingEnvironment
from tasks.tasks import TASKS
from grader import Grader

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Orion Trading Environment",
    description=(
        "Indian NSE equity trading simulation with STCG/LTCG tax, "
        "brokerage, and DP charges across bull, volatile, and bear regimes."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _clamp(value: float) -> float:
    """Clamp reward/score to strict (0.01, 0.99)."""
    return max(0.01, min(0.99, float(value)))


def _make_task(name: str) -> dict:
    """Return a task dict with name injected."""
    task = dict(TASKS[name])
    task["name"] = name
    return task


# ── Global environment instance ───────────────────────────────────────────────
_current_task_name = "easy"
env = TradingEnvironment(_make_task(_current_task_name))
env.reset()

# Episode tracking (for /grader)
_episode_step_rewards: list[float] = []
_episode_action_log:   list[str]   = []
_episode_invalid:      int         = 0
_episode_initial_balance: float    = 10000.0


# ── Request / Response Models ─────────────────────────────────────────────────
class ResetRequest(BaseModel):
    task: Optional[str] = "easy"


class StepRequest(BaseModel):
    action: Optional[str] = "HOLD"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Liveness check — required by OpenEnv validator."""
    return {
        "status":      "healthy",
        "environment": "orion-trading-env",
        "version":     "1.0.0",
    }


@app.get("/tasks")
def list_tasks():
    """Return all available task definitions."""
    return [
        {
            "id":          name,
            "name":        name,
            "difficulty":  name,
            "steps":       t["steps"],
            "max_holdings":t["max_holdings"],
            "tax":         t["tax"],
            "dp_charge":   t["dp_charge"],
            "description": (
                f"Indian NSE equity trading — {name} difficulty. "
                f"{t['steps']} steps, max {t['max_holdings']} holdings."
            ),
            "reward_range": [0.01, 0.99],
        }
        for name, t in TASKS.items()
    ]


@app.api_route("/reset", methods=["GET", "POST"])
def reset(body: Optional[ResetRequest] = Body(default=None)):
    """
    Reset the environment for a given task.

    Body (optional JSON):
        { "task": "easy" | "medium" | "hard" }
    """
    global env, _current_task_name
    global _episode_step_rewards, _episode_action_log
    global _episode_invalid, _episode_initial_balance

    task_name = (body.task if body else None) or "easy"
    if task_name not in TASKS:
        task_name = "easy"

    _current_task_name    = task_name
    _episode_step_rewards = []
    _episode_action_log   = []
    _episode_invalid      = 0

    env = TradingEnvironment(_make_task(task_name))
    obs = env.reset()

    _episode_initial_balance = env.state.balance

    return {
        "observation": obs["text"],
        "task":        task_name,
        "max_steps":   env.state.max_steps,
        "info": {
            "price":    round(env.state.price, 2),
            "balance":  round(env.state.balance, 2),
            "holdings": env.state.holdings,
            "regime":   env.state.regime,
        },
    }


@app.post("/step")
def step(body: Optional[StepRequest] = Body(default=None)):
    """
    Take one action in the environment.

    Body (optional JSON):
        { "action": "BUY" | "SELL" | "HOLD" }

    Returns observation text, reward (0.01–0.99), and done flag.
    """
    global _episode_step_rewards, _episode_action_log, _episode_invalid

    raw_action = (body.action if body else None) or "HOLD"
    action = raw_action.strip().upper()
    if action not in ("BUY", "SELL", "HOLD"):
        action = "HOLD"

    obs, reward_result, done = env.step(action)

    # ── Hard clamp at the API boundary ────────────────────────────────────────
    safe_reward = _clamp(reward_result.total)

    # Track episode stats for /grader
    _episode_step_rewards.append(safe_reward)
    _episode_action_log.append(action)
    if "invalid" in reward_result.penalties:
        _episode_invalid += 1

    return {
        "observation": obs["text"],
        "reward":      safe_reward,        # strictly in (0.01, 0.99)
        "done":        done,
        "info": {
            "action":          action,
            "price":           round(env.state.price, 2),
            "balance":         round(env.state.balance, 2),
            "holdings":        env.state.holdings,
            "regime":          env.state.regime,
            "step":            env.state.step,
            "steps_remaining": env.state.max_steps - env.state.step,
            "reward_components": reward_result.components,
            "reward_penalties":  reward_result.penalties,
        },
    }


@app.get("/state")
def state():
    """Return the full current environment state snapshot."""
    s = env.state
    portfolio_value = s.balance + s.holdings * s.price
    return {
        "episode_step":      s.step,
        "max_steps":         s.max_steps,
        "price":             round(s.price, 2),
        "balance":           round(s.balance, 2),
        "holdings":          s.holdings,
        "avg_buy_price":     round(s.avg_buy_price, 2),
        "portfolio_value":   round(portfolio_value, 2),
        "regime":            s.regime,
        "regime_confidence": round(s.regime_confidence, 2),
        "task":              _current_task_name,
        "done":              s.done,
    }


@app.get("/grader")
def grader_scores():
    """
    Return grader scores for the current episode so far.
    All scores are strictly in (0.01, 0.99).
    """
    final_balance = env.state.balance + env.state.holdings * env.state.price

    stats = {
        "final_balance": final_balance,
        "step_rewards":  _episode_step_rewards,
        "action_log":    _episode_action_log,
        "invalid_count": _episode_invalid,
        "difficulty":    _current_task_name,
    }

    g      = Grader()
    result = g.evaluate("current_episode", _episode_initial_balance, stats)

    # Extra safety clamp on the score that leaves this endpoint
    result["score"] = _clamp(result["score"])

    return {
        "task":   _current_task_name,
        "score":  result["score"],          # strictly in (0.01, 0.99)
        "detail": result,
    }


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()