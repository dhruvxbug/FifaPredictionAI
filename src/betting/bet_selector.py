import numpy as np

from src.utils.config import config
from src.betting.kelly_criterion import KellyCriterion

OUTCOME_NAMES = {0: "HOME", 1: "DRAW", 2: "AWAY"}


class BetSelector:
    def __init__(self):
        self.min_confidence = config["betting"]["min_confidence"]
        self.max_stake_pct = config["betting"]["max_stake_fraction"]
        self.min_stake = config["betting"]["min_stake"]
        self.kelly = KellyCriterion(config["betting"]["kelly_fraction"])

    def evaluate(self, proba: np.ndarray, home_odds: float = None,
                 draw_odds: float = None, away_odds: float = None,
                 bankroll: float = 1000.0) -> dict:
        outcome = int(np.argmax(proba))
        confidence = float(proba[outcome])

        result = {
            "predicted_outcome": OUTCOME_NAMES[outcome],
            "predicted_index": outcome,
            "confidence": confidence,
            "probabilities": {
                "home": float(proba[0]),
                "draw": float(proba[1]),
                "away": float(proba[2]),
            },
            "should_bet": False,
            "stake": 0.0,
            "odds_used": None,
        }

        if confidence < self.min_confidence:
            return result

        odds_map = {0: home_odds, 1: draw_odds, 2: away_odds}
        best_odds = odds_map.get(outcome)
        if best_odds is None:
            return result

        stake = self.kelly.compute_stake(confidence, best_odds, bankroll)
        max_stake = bankroll * self.max_stake_pct
        stake = min(stake, max_stake)
        stake = max(stake, self.min_stake) if stake >= self.min_stake else 0.0

        if stake > 0:
            result["should_bet"] = True
            result["stake"] = round(stake, 2)
            result["odds_used"] = best_odds

        return result

    def confidence_summary(self, proba: np.ndarray) -> str:
        outcome = int(np.argmax(proba))
        conf = float(proba[outcome])
        if conf >= 0.85:
            return "HIGH_CONFIDENCE"
        elif conf >= 0.75:
            return "GOOD_VALUE"
        elif conf >= 0.70:
            return "SPECULATIVE"
        return "NO_BET"
