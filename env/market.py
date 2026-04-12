import random


class Market:
    def __init__(self, task):
        self.volatility = task["volatility"]
        self.reset()

    def reset(self):    
        self.regime = "sideways"
        self.regime_confidence = 0.5
        

    def _switch_regime(self):
        regimes = ["bull", "bear", "sideways", "volatile"]
        self.regime = random.choice(regimes)
        self.regime_confidence = round(random.uniform(0.4, 0.9), 2)

    def next_price(self, current_price, step):
    
        if step > 0 and step % 15 == 0:
            self._switch_regime()

        # Scale drift/noise as % of current price so it works at any price level
        pct = self.volatility * 0.005  # base = 0.5% of price per step

        if self.regime == "bull":
            drift = current_price * pct
            noise = random.uniform(-current_price * pct * 0.3, current_price * pct * 0.3)
        elif self.regime == "bear":
            drift = -current_price * pct
            noise = random.uniform(-current_price * pct * 0.3, current_price * pct * 0.3)
        elif self.regime == "volatile":
            drift = 0
            noise = random.uniform(-current_price * pct * 2.0, current_price * pct * 2.0)
        else:  # sideways
            drift = 0
            noise = random.uniform(-current_price * pct * 0.8, current_price * pct * 0.8)

        new_price = current_price + drift + noise

        return max(new_price, 1), self.regime, self.regime_confidence