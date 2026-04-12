from core.models import RewardResult


def compute_reward(prev_value, new_value, action, invalid, traded, state):
    initial_balance = 10000.0

    # How much did portfolio value change as % of starting balance
    portfolio_change_pct = (new_value - prev_value) / initial_balance

    # Base reward centered at 0.50, scaled so 1% gain = +0.05 reward
    base = 0.50 + (portfolio_change_pct * 5.0)

    # Reward correct action in correct regime
    if action == "BUY" and state.regime == "bull":
        base += 0.05
    elif action == "SELL" and state.regime == "bear" and state.holdings > 0:
        base += 0.05
    elif action == "HOLD" and state.regime == "sideways":
        base += 0.03

    # Reward profit-taking (sell above avg buy price)
    if action == "SELL" and state.holdings >= 0 and state.avg_buy_price > 0:
        if state.price > state.avg_buy_price * 1.02:
            base += 0.04

    # Penalize wrong actions in wrong regimes
    if action == "BUY" and state.regime == "bear":
        base -= 0.05
    elif action == "SELL" and state.regime == "bull" and state.holdings > 0:
        base -= 0.03

    # Invalid action penalty
    if invalid:
        base -= 0.10

    # Overtrading penalty (brokerage hurts)
    if traded:
        base -= 0.01

    # HOLD spam penalty - only if holding stocks and price is rising
    if action == "HOLD" and state.holdings > 0 and state.regime == "bull":
        base -= 0.02

    # Final clamp strictly within (0.01, 0.99)
    total = max(0.01, min(0.99, base))

    return RewardResult(
        total=total,
        components={"base": round(base, 4)},
        penalties={}
    )