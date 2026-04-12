"""
grader.py — Orion Trading Environment Grader

Every score and every sub-score returned by this file is strictly
inside (0.01, 0.99). Never 0.0, never 1.0.
"""


def _clamp(value: float) -> float:
    """Clamp any float to the strict open interval (0.01, 0.99)."""
    return max(0.01, min(0.99, float(value)))


class Grader:
    """
    Evaluates a completed trading episode into a final score in (0.01, 0.99).

    Score = 0.70 * profit_score
           + 0.20 * consistency_score
           + 0.10 * behavior_score

    All three components and the final score are clamped to (0.01, 0.99).
    """

    def evaluate(self, agent_name: str, initial_balance: float, stats: dict) -> dict:
        final_balance  = stats["final_balance"]
        net_profit     = final_balance - initial_balance
        step_rewards   = stats.get("step_rewards", [])
        action_log     = stats.get("action_log", [])
        invalid_count  = stats.get("invalid_count", 0)

        # ── 1. PROFIT SCORE ──────────────────────────────────────────────
        # return_pct: e.g. +0.05 = earned 5%, -0.05 = lost 5%
        # Centred at 0.50. Each 1% gain/loss moves score ±0.02.
        # So +25% return = 0.50 + 0.50 = 1.0 → clamped to 0.99
        #    -25% return = 0.50 - 0.50 = 0.0 → clamped to 0.01
        return_pct  = net_profit / initial_balance
        profit_score = _clamp(0.50 + (return_pct * 2.0))

        # ── 2. CONSISTENCY SCORE ─────────────────────────────────────────
        # Step rewards are now in (0.01, 0.99).
        # A "good" step is one where reward > 0.50 (above neutral).
        if step_rewards:
            good_steps       = sum(1 for r in step_rewards if r > 0.50)
            consistency_raw  = good_steps / len(step_rewards)
        else:
            consistency_raw  = 0.50

        consistency_score = _clamp(consistency_raw)

        # ── 3. BEHAVIOR SCORE ────────────────────────────────────────────
        total_steps = max(len(step_rewards), 1)

        # Invalid action ratio — penalise heavily
        invalid_ratio = invalid_count / total_steps

        # Overtrading penalty: more than 60% BUY+SELL steps is churn
        if action_log:
            trade_count = sum(1 for a in action_log if a in ("BUY", "SELL"))
            trade_ratio = trade_count / total_steps
        else:
            trade_ratio = 0.0
        overtrade_penalty = max(0.0, trade_ratio - 0.60)

        # HOLD spam penalty: more than 70% HOLD steps is lazy
        if action_log:
            hold_count = sum(1 for a in action_log if a == "HOLD")
            hold_ratio = hold_count / total_steps
        else:
            hold_ratio = 0.0
        hold_spam_penalty = max(0.0, hold_ratio - 0.70)

        behavior_raw = 1.0 - (
            invalid_ratio    * 2.0 +
            overtrade_penalty        +
            hold_spam_penalty
        )
        behavior_score = _clamp(behavior_raw)

        # ── 4. FINAL SCORE ───────────────────────────────────────────────
        raw_score = (
            0.70 * profit_score      +
            0.20 * consistency_score +
            0.10 * behavior_score
        )
        score = _clamp(raw_score)

        # ── 5. HUMAN LABEL ───────────────────────────────────────────────
        if return_pct > 0.10:
            result = "Excellent"
        elif return_pct > 0.0:
            result = "Good"
        elif return_pct > -0.02:
            result = "Neutral"
        elif return_pct > -0.05:
            result = "Poor"
        else:
            result = "Bad"

        return {
            "agent":           agent_name,
            "final_balance":   round(final_balance, 2),
            "net_profit":      round(net_profit, 2),
            "return_pct":      round(return_pct * 100, 2),   # human-readable %
            "score":           round(score, 4),               # ALWAYS in (0.01,0.99)
            "profit_score":    round(profit_score, 4),
            "consistency":     round(consistency_score, 4),
            "behavior":        round(behavior_score, 4),
            "result":          result,
            "invalid_actions": invalid_count,
            "difficulty":      stats.get("difficulty", "unknown"),
        }