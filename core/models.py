from dataclasses import dataclass
from typing import Dict


@dataclass
class OrionState:
    price: float
    balance: float
    holdings: int
    avg_buy_price: float

    step: int
    max_steps: int

    regime: str
    regime_confidence: float

    max_holdings: int   

    done: bool


@dataclass
class RewardResult:
    total: float
    components: Dict[str, float]
    penalties: Dict[str, float]