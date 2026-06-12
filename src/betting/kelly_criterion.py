import numpy as np


class KellyCriterion:
    def __init__(self, fraction: float = 0.25):
        self.fraction = fraction

    def compute_stake(self, prob: float, odds: float, bankroll: float) -> float:
        if odds <= 1 or prob <= 0 or prob >= 1:
            return 0.0
        implied_prob = 1.0 / odds
        if prob <= implied_prob:
            return 0.0
        edge = prob - implied_prob
        q = 1.0 - prob
        kelly_pct = (prob * (odds - 1) - q) / (odds - 1)
        if kelly_pct <= 0:
            return 0.0
        return kelly_pct * self.fraction * bankroll
