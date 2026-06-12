import numpy as np
from datetime import datetime

from src.models.ensemble import EnsemblePredictor
from src.features.feature_pipeline import FeaturePipeline, FEATURE_NAMES
from src.betting.bet_selector import BetSelector
from src.betting.bankroll import Bankroll
from src.betting.odds import OddsFetcher
from src.evaluation.tracker import PredictionTracker
from src.data_collection.exa_search import ExaSearchAgent


class MatchPredictor:
    def __init__(self, use_exa: bool = False):
        self.ensemble = EnsemblePredictor()
        self.features = FeaturePipeline()
        self.bet_selector = BetSelector()
        self.bankroll = Bankroll()
        self.odds_fetcher = OddsFetcher()
        self.tracker = PredictionTracker()
        self.exa = ExaSearchAgent() if use_exa else None

    def predict_match(self, home: str, away: str, match_date: str = "",
                      match_location: str = "New York",
                      prev_home_date: str = None, prev_away_date: str = None,
                      home_odds: float = None, draw_odds: float = None,
                      away_odds: float = None,
                      use_exa: bool = False) -> dict:
        feature_vector = self.features.compute_features_for_match(
            home, away, match_date, match_location, prev_home_date, prev_away_date,
        )

        exa_intel = {}
        if use_exa and self.exa:
            exa_intel["home"] = self.exa.get_team_intelligence(home, away)
            exa_intel["away"] = self.exa.get_team_intelligence(away, home)

            if "home" in exa_intel:
                self.features.injury.set_injury_news(
                    home, exa_intel["home"].get("injuries", {}).get("results", [])
                )
                self.features.sentiment.set_exa_results(
                    home, exa_intel["home"].get("sentiment", {})
                )
            if "away" in exa_intel:
                self.features.injury.set_injury_news(
                    away, exa_intel["away"].get("injuries", {}).get("results", [])
                )
                self.features.sentiment.set_exa_results(
                    away, exa_intel["away"].get("sentiment", {})
                )

            feature_vector = self.features.compute_features_for_match(
                home, away, match_date, match_location, prev_home_date, prev_away_date,
            )

        outcome, confidence, proba = self.ensemble.predict(home, away, feature_vector)

        if home_odds is None or draw_odds is None or away_odds is None:
            odds_data = self.odds_fetcher.get_odds(home, away, match_date)
            if odds_data:
                home_odds = odds_data["home_odds"]
                draw_odds = odds_data["draw_odds"]
                away_odds = odds_data["away_odds"]

        bet_eval = self.bet_selector.evaluate(
            proba, home_odds, draw_odds, away_odds, self.bankroll.balance
        )

        feature_dict = dict(zip(FEATURE_NAMES, feature_vector))

        result = {
            "match": f"{home} vs {away}",
            "date": match_date,
            "home": home,
            "away": away,
            "predicted_outcome": bet_eval["predicted_outcome"],
            "predicted_index": bet_eval["predicted_index"],
            "confidence": confidence,
            "probabilities": bet_eval["probabilities"],
            "confidence_level": self.bet_selector.confidence_summary(proba),
            "bet_decision": bet_eval,
            "features": feature_dict,
            "exa_intel": exa_intel,
            "home_odds": home_odds,
            "draw_odds": draw_odds,
            "away_odds": away_odds,
            "model_probas": {
                "elo": self.ensemble.predict_base_probas(home, away, feature_vector)[0].tolist(),
                "poisson": self.ensemble.predict_base_probas(home, away, feature_vector)[1].tolist(),
                "xgb": self.ensemble.predict_base_probas(home, away, feature_vector)[2].tolist(),
            },
        }

        self.tracker.log_prediction(result)
        return result
