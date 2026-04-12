from core.config import config


class StepManager:
    def apply_action(self, state, action, task):
        price = state.price

        invalid = False
        traded = False

        if action == "BUY":
            cost = price
            brokerage = max(cost * config.brokerage_pct, config.brokerage_min)
            total_cost = cost + brokerage


            if state.balance >= total_cost and state.holdings < state.max_holdings:
                qty = 1

                cost = price * qty
                brokerage = max(cost * config.brokerage_pct, config.brokerage_min)

                total_cost = cost + brokerage

                state.balance -= total_cost

                # update avg price
                if state.holdings == 0:
                    state.avg_buy_price = price
                else:
                    state.avg_buy_price = (
                        (state.avg_buy_price * state.holdings + price)
                        / (state.holdings + 1)
                    )

                state.holdings += 1
                traded = True
            else:
                invalid = True

        elif action == "SELL":
            if state.holdings > 0:
                qty = 1

                revenue = price * qty
                brokerage = max(revenue * config.brokerage_pct, config.brokerage_min)

                profit = price - state.avg_buy_price

                tax = 0
                dp = 0

                if task.get("tax"):
                    tax = max(profit, 0) * config.stcg_tax

                if task.get("dp_charge"):
                    dp = config.dp_charge
                

                total_gain = revenue - brokerage - tax - dp

                state.balance += total_gain
                state.holdings -= 1

                if state.holdings == 0:
                    state.avg_buy_price = 0

                traded = True
            else:
                invalid = True

        elif action == "HOLD":
            pass

        else:
            invalid = True

        return state, invalid, traded