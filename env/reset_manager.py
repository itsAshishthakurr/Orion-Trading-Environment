from core.models import OrionState
from core.config import config


class ResetManager:
    def reset(self, task):
        return OrionState(
            price=500.0,
            balance=config.starting_balance,
            holdings=0,
            avg_buy_price=0,
            step=0,
            max_steps=task["steps"],
            regime="sideways",
            regime_confidence=0.5,
            max_holdings=task["max_holdings"],
            done=False
        )