from core.models import OrionState
from env.market import Market
from env.step_manager import StepManager
from env.reset_manager import ResetManager
from env.reward import compute_reward
from core.config import config


class TradingEnvironment:
    def __init__(self, task):
        self.task = task
        self.market = Market(task)
        self.step_manager = StepManager()
        self.reset_manager = ResetManager()

        self.state = None

    def reset(self):
        self.state = self.reset_manager.reset(self.task)
        self.market.reset()
        return self._get_observation()

    def step(self, action):
        prev_value = self._portfolio_value()

        # apply action
        self.state, invalid, traded = self.step_manager.apply_action(
            self.state, action, self.task
        )

        # market moves
        new_price, regime, confidence = self.market.next_price(
            self.state.price, self.state.step
        )

        self.state.price = new_price
        self.state.regime = regime
        self.state.regime_confidence = confidence

        self.state.step += 1

        # compute reward
        new_value = self._portfolio_value()
        reward = compute_reward(prev_value, new_value, action, invalid, traded, self.state)

        # done check
        if self.state.step >= self.state.max_steps:
            self.state.done = True

        return self._get_observation(), reward, self.state.done

    def _portfolio_value(self):
        return self.state.balance + self.state.holdings * self.state.price

    def _get_observation(self):
        return {
            "text": self._build_text_observation(),
            "state": self.state,
            "task_metrics": {
                "steps_remaining": self.state.max_steps - self.state.step
            }
        }

    def _build_text_observation(self):
        return f"""
Market Report:
Price: ₹{round(self.state.price,2)}
Regime: {self.state.regime} (confidence {self.state.regime_confidence})

Portfolio:
Balance: ₹{round(self.state.balance,2)}
Holdings: {self.state.holdings}
Avg Buy Price: ₹{round(self.state.avg_buy_price,2)}

Steps Remaining: {self.state.max_steps - self.state.step}
"""