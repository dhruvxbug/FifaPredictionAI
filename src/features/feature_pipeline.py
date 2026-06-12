import pandas as pd
import numpy as np

from src.features.team_strength import TeamStrengthFeatures
from src.features.form_analysis import FormAnalysis
from src.features.h2h import H2HAnalysis
from src.features.injury_impact import InjuryImpactAnalyzer
from src.features.manager_analysis import ManagerAnalyzer
from src.features.sentiment import SentimentAnalyzer
from src.features.fatigue import FatigueAnalyzer
from src.data_collection.historical import HistoricalDataFetcher


FEATURE_NAMES = [
    "home_fifa_rank", "away_fifa_rank", "rank_diff", "rank_log_ratio",
    "home_market_value", "away_market_value", "market_value_ratio",
    "home_wc_appearances", "away_wc_appearances", "wc_exp_diff",
    "home_avg_age", "away_avg_age", "age_diff",
    "home_form_points", "away_form_points",
    "home_form_goals_scored_avg", "away_form_goals_scored_avg",
    "home_form_goals_conceded_avg", "away_form_goals_conceded_avg",
    "home_form_win_rate", "away_form_win_rate",
    "home_form_streak", "away_form_streak",
    "h2h_team1_wins", "h2h_team2_wins", "h2h_draws",
    "h2h_team1_goals_avg", "h2h_team2_goals_avg",
    "h2h_games_played",
    "home_injury_impact", "away_injury_impact",
    "home_key_players_missing", "away_key_players_missing",
    "manager_home_win_rate", "manager_away_win_rate",
    "manager_home_exp", "manager_away_exp",
    "home_fan_confidence", "away_fan_confidence",
    "home_rest_days", "away_rest_days",
    "home_travel_km", "away_travel_km",
    "home_fatigue", "away_fatigue",
]


class FeaturePipeline:
    def __init__(self):
        self.team_strength = TeamStrengthFeatures()
        self.form = FormAnalysis()
        self.h2h = H2HAnalysis()
        self.injury = InjuryImpactAnalyzer()
        self.manager = ManagerAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.fatigue = FatigueAnalyzer()
        self.fetcher = HistoricalDataFetcher()
        self._historical_df = None

    def ensure_historical_data(self):
        if self._historical_df is None:
            self._historical_df = self.fetcher.fetch_all()

    def compute_features_for_match(
        self, home: str, away: str, match_date: str = "",
        match_location: str = "New York",
        prev_home_date: str = None, prev_away_date: str = None,
    ) -> np.ndarray:
        self.ensure_historical_data()
        df = self._historical_df

        strength = self.team_strength.compute_all(home, away)
        home_form = self.form.compute_all(home, away, df)
        away_form = self.form.compute_all(away, home, df)
        h2h = self.h2h.compute_all(home, away, df)
        home_injury = self.injury.compute_all(home)
        away_injury = self.injury.compute_all(away)
        home_mgr = self.manager.compute_all(home)
        away_mgr = self.manager.compute_all(away)
        home_sent = self.sentiment.compute_all(home)
        away_sent = self.sentiment.compute_all(away)
        home_fat = self.fatigue.compute_all(home, match_date, match_location, prev_home_date)
        away_fat = self.fatigue.compute_all(away, match_date, match_location, prev_away_date)

        feature_dict = {
            **strength,
            "home_form_points": home_form["form_points"],
            "away_form_points": away_form["form_points"],
            "home_form_goals_scored_avg": home_form["form_goals_scored_avg"],
            "away_form_goals_scored_avg": away_form["form_goals_scored_avg"],
            "home_form_goals_conceded_avg": home_form["form_goals_conceded_avg"],
            "away_form_goals_conceded_avg": away_form["form_goals_conceded_avg"],
            "home_form_win_rate": home_form["form_win_rate"],
            "away_form_win_rate": away_form["form_win_rate"],
            "home_form_streak": home_form["form_streak"],
            "away_form_streak": away_form["form_streak"],
            **{k: v for k, v in h2h.items()},
            "home_injury_impact": home_injury["injury_impact_score"],
            "away_injury_impact": away_injury["injury_impact_score"],
            "home_key_players_missing": home_injury["key_players_missing"],
            "away_key_players_missing": away_injury["key_players_missing"],
            "manager_home_win_rate": home_mgr["manager_win_rate"],
            "manager_away_win_rate": away_mgr["manager_win_rate"],
            "manager_home_exp": home_mgr["manager_experience_years"],
            "manager_away_exp": away_mgr["manager_experience_years"],
            "home_fan_confidence": home_sent["fan_confidence_index"],
            "away_fan_confidence": away_sent["fan_confidence_index"],
            "home_rest_days": home_fat["rest_days"],
            "away_rest_days": away_fat["rest_days"],
            "home_travel_km": home_fat["travel_distance_km"],
            "away_travel_km": away_fat["travel_distance_km"],
            "home_fatigue": home_fat["fatigue_index"],
            "away_fatigue": away_fat["fatigue_index"],
        }

        return np.array([feature_dict.get(name, 0.0) for name in FEATURE_NAMES])

    def compute_features_bulk(self, match_list: list[dict]) -> np.ndarray:
        return np.array([
            self.compute_features_for_match(
                m["home"], m["away"], m.get("date", ""),
                m.get("location", "New York"),
                m.get("prev_home_date"), m.get("prev_away_date"),
            )
            for m in match_list
        ])

    def get_feature_dict_for_match(self, home: str, away: str, **kwargs) -> dict:
        self.ensure_historical_data()
        arr = self.compute_features_for_match(home, away, **kwargs)
        return dict(zip(FEATURE_NAMES, arr))
