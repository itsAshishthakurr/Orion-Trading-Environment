"""
core/observation_builder.py - Orion Trading Environment

Builds rich, dynamic observations from live simulation state.

Two consumers:
  - LLM agent (inference.py): reads obs["text"] - a natural language market report
  - Local agents (main.py): read obs["state"] - the raw OrionState dataclass

Both are returned together so the environment works in both modes simultaneously.
"""

from core.config import config


def compute_momentum(price_history: list, window: int = 5) -> float:
    """
    Compute momentum score from recent price history.
    Returns a value 0.0-1.0 where:
      0.5 = flat / no trend
      >0.5 = upward momentum
      <0.5 = downward momentum
    """
    if len(price_history) < 2:
        return 0.5

    recent = price_history[-window:]
    changes = [
        (recent[i] - recent[i - 1]) / recent[i - 1]
        for i in range(1, len(recent))
        if recent[i - 1] > 0
    ]

    if not changes:
        return 0.5

    avg = sum(changes) / len(changes)
    # Normalise: avg of +-0.5% per step maps to 0.5 +- 0.5 score range
    score = 0.5 + (avg * 50)
    return round(min(1.0, max(0.0, score)), 2)


def _tax_line(task: dict) -> str:
    """Build the tax/cost line based on task config."""
    parts = [f"Brokerage: 0.3% per trade (min Rs.{config.brokerage_min:.0f})"]
    if task.get("tax"):
        parts.append(f"STCG Tax: {config.stcg_tax * 100:.0f}% on profit")
    if task.get("dp_charge"):
        parts.append(f"DP Charge: Rs.{config.dp_charge:.0f} per SELL")
    if not task.get("tax") and not task.get("dp_charge"):
        parts.append("Tax: None (easy mode)")
    return " | ".join(parts)


def _regime_label(regime: str, confidence: float) -> str:
    labels = {
        "bull":     "BULLISH",
        "bear":     "BEARISH",
        "sideways": "SIDEWAYS",
        "volatile": "VOLATILE",
    }
    label = labels.get(regime, regime.upper())
    strength = "strong" if confidence >= 0.7 else "moderate" if confidence >= 0.5 else "weak"
    return f"{label} ({strength}, confidence {confidence:.2f})"


def _profit_loss_line(state, portfolio_value: float, initial_balance: float) -> str:
    pnl = portfolio_value - initial_balance
    pnl_pct = (pnl / initial_balance) * 100 if initial_balance > 0 else 0.0
    direction = "PROFIT" if pnl >= 0 else "LOSS"
    return f"Rs.{abs(pnl):.2f} {direction} ({pnl_pct:+.2f}% vs start)"


def _unrealised_pnl(state) -> str:
    if state.holdings == 0 or state.avg_buy_price == 0:
        return "No open position"
    unrealised = (state.price - state.avg_buy_price) * state.holdings
    pct = ((state.price - state.avg_buy_price) / state.avg_buy_price) * 100
    direction = "gain" if unrealised >= 0 else "loss"
    return f"Rs.{abs(unrealised):.2f} unrealised {direction} ({pct:+.2f}% per unit)"


def build_observation(state, task: dict, market, initial_balance: float = 10000.0) -> dict:
    """
    Build a complete observation dict from current simulation state.

    Args:
        state: OrionState dataclass (from environment)
        task: task config dict (volatility, tax, dp_charge, steps, etc.)
        market: Market instance (for price_history and volatility)
        initial_balance: starting balance for P&L calculation

    Returns:
        dict with:
          "text"  -> rich natural language report for LLM
          "state" -> raw OrionState for local agents
          "task_metrics" -> helper fields
    """
    s = state
    portfolio_value = s.balance + s.holdings * s.price
    steps_remaining = s.max_steps - s.step
    momentum = compute_momentum(market.price_history)

    # Price change vs previous (from history)
    if len(market.price_history) >= 2:
        prev_price = market.price_history[-2]
        price_change_pct = ((s.price - prev_price) / prev_price) * 100
    else:
        price_change_pct = 0.0

    # Urgency signal for end-of-episode
    if steps_remaining <= 5:
        urgency = "CRITICAL - Episode ending very soon!"
    elif steps_remaining <= 10:
        urgency = "WARNING - Episode ending soon. Consider closing positions."
    elif steps_remaining <= 20:
        urgency = "CAUTION - Less than 20 steps left."
    else:
        urgency = "Normal"

    text = f"""Market Report - NSE Simulation (Step {s.step}/{s.max_steps}):

[MARKET]
Regime: {_regime_label(s.regime, s.regime_confidence)}
Price: Rs.{s.price:.2f}  |  Change: {price_change_pct:+.2f}%
Momentum: {momentum:.2f}  (>0.5 = upward, <0.5 = downward)
Volatility: {market.volatility:.2f}

[PORTFOLIO]
Cash Balance: Rs.{s.balance:.2f}
Holdings: {s.holdings} units (max allowed: {s.max_holdings})
Avg Buy Price: Rs.{s.avg_buy_price:.2f}
Portfolio Value: Rs.{portfolio_value:.2f}
Overall P&L: {_profit_loss_line(s, portfolio_value, initial_balance)}
Unrealised: {_unrealised_pnl(s)}

[COSTS]
{_tax_line(task)}

[EPISODE]
Steps Remaining: {steps_remaining}
Status: {urgency}

Decide your next action: BUY, SELL, or HOLD."""

    return {
        "text": text,
        "state": s,
        "task_metrics": {
            "steps_remaining": steps_remaining,
            "portfolio_value": round(portfolio_value, 2),
            "momentum": momentum,
            "price_change_pct": round(price_change_pct, 2),
        },
    }