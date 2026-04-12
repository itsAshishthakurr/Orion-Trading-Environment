import os
from dataclasses import dataclass


@dataclass
class Config:
    # trading defaults (fallback only)
    starting_balance: float = float(os.getenv("ORION_STARTING_BALANCE", 10000))

    # market
    volatility: float = float(os.getenv("ORION_VOLATILITY", 1.0))

    # costs
    brokerage_pct: float = 0.003   # 0.3%
    brokerage_min: float = 3.0

    stcg_tax: float = 0.20
    dp_charge: float = 15.0

    # reward shaping
    hold_penalty: float = 0.02
    invalid_penalty: float = 0.02
    churn_penalty: float = 0.01


config = Config()