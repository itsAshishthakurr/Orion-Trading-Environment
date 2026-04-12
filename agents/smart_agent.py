from agents.base_agent import BaseAgent


class SmartAgent(BaseAgent):
    def select_action(self, observation):
        state = observation["state"]

        price = state.price
        avg_price = state.avg_buy_price
        holdings = state.holdings
        regime = state.regime
        balance = state.balance

        # Can we afford to buy?
        can_buy = balance >= price * 1.003 and holdings < state.max_holdings

        # Sell in bear market if we hold anything
        if regime == "bear" and holdings > 0:
            return "SELL"

        # Take profits: sell if price > 3% above avg buy
        if holdings > 0 and avg_price > 0 and price > avg_price * 1.03:
            return "SELL"

        # Buy in bull market if we have room and funds
        if regime == "bull" and can_buy:
            return "BUY"

        # In sideways/volatile: buy low if no holdings and can afford
        if regime in ["sideways", "volatile"] and holdings == 0 and can_buy:
            return "BUY"

        # Cut losses: sell if price dropped more than 4% below avg buy
        if holdings > 0 and avg_price > 0 and price < avg_price * 0.96:
            return "SELL"

        return "HOLD"