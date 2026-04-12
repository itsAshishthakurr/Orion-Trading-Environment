import random
from agents.base_agent import BaseAgent


class LearningAgent(BaseAgent):
    def __init__(self):
        self.q_table = {}

        self.alpha = 0.2          # higher learning rate - learn faster
        self.gamma = 0.9
        
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.05   # keep some exploration

        self.last_state = None
        self.last_action = None

    def _discretize(self, obs):
        state = obs["state"]

        price = state.price
        balance = state.balance
        holdings = state.holdings
        regime = state.regime
        avg_price = state.avg_buy_price

        # price vs avg buy price (is it profitable to sell?)
        if avg_price > 0 and price > avg_price * 1.03:
            price_vs_avg = "PROFIT"
        elif avg_price > 0 and price < avg_price * 0.97:
            price_vs_avg = "LOSS"
        else:
            price_vs_avg = "FLAT"

        # holding bucket
        if holdings == 0:
            hold_bucket = "EMPTY"
        elif holdings <= 3:
            hold_bucket = "LOW"
        else:
            hold_bucket = "HIGH"
        
        # can we buy?
        can_buy = "YES" if balance >= price * 1.003 else "NO"

        return (regime, hold_bucket, price_vs_avg, can_buy)

    def _get_q(self, state):
        if state not in self.q_table:
            # Initialize with slight bias toward HOLD to avoid invalid actions
            self.q_table[state] = {
                "BUY": 0.0,
                "SELL": 0.0,
                "HOLD": 0.0
            }
        return self.q_table[state]

    def select_action(self, observation):
        state = self._discretize(observation)
        q = self._get_q(state)

        # epsilon-greedy
        if random.random() < self.epsilon:
            action = random.choice(["BUY", "SELL", "HOLD"])
        else:
            action = max(q, key=q.get)

        self.last_state = state
        self.last_action = action

        return action

    def update(self, reward, next_observation):
        if self.last_state is None or self.last_action is None:
            return
         
        next_state = self._discretize(next_observation)
        next_q = self._get_q(next_state)

        # current Q
        old_q = self.q_table[self.last_state][self.last_action]
        # best future Q
        max_next_q = max(next_q.values())

        # Q-learning update
        new_q = old_q + self.alpha * (
            reward.total + self.gamma * max_next_q - old_q
        )

        self.q_table[self.last_state][self.last_action] = new_q

        # decay epsilon
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )

    def reset(self):
        self.last_state = None
        self.last_action = None