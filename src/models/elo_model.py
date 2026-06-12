import math
import numpy as np
import pandas as pd

from src.utils.config import config


class EloModel:
    def __init__(self):
        self.k = config["models"]["elo"]["k_factor"]
        self.home_adv = config["models"]["elo"]["home_advantage"]
        self.initial_rating = config["models"]["elo"]["initial_rating"]
        self.use_gd = config["models"]["elo"]["goal_difference_weight"]
        self.regression_power = config["models"]["elo"]["regression_power"]
        self.ratings: dict[str, float] = {}

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, self.initial_rating)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    def goal_diff_weight(self, home_goals: int, away_goals: int) -> float:
        gd = abs(home_goals - away_goals)
        return math.log(max(gd, 1) + 1) * (2.2 / (2.2 + 0.001))

    def update(self, home: str, away: str, home_goals: int, away_goals: int):
        r_home = self.get_rating(home) + self.home_adv
        r_away = self.get_rating(away)

        e_home = self.expected_score(r_home, r_away)
        e_away = 1.0 - e_home

        s_home = 1.0 if home_goals > away_goals else (0.5 if home_goals == away_goals else 0.0)
        s_away = 1.0 - s_home

        gd_weight = self.goal_diff_weight(home_goals, away_goals) if self.use_gd else 1.0

        k_home = self.k * gd_weight
        k_away = self.k * gd_weight

        self.ratings[home] = self.get_rating(home) + k_home * (s_home - e_home)
        self.ratings[away] = self.get_rating(away) + k_away * (s_away - e_away)

    def train_on_historical(self, df: pd.DataFrame):
        df_sorted = df.sort_values("date")
        for _, match in df_sorted.iterrows():
            home = match["home_team"]
            away = match["away_team"]
            try:
                hg = int(match["home_score"])
                ag = int(match["away_score"])
                self.update(home, away, hg, ag)
            except (ValueError, TypeError):
                continue

        self._apply_regression()

    def _apply_regression(self):
        mean_rating = np.mean(list(self.ratings.values()))
        for team in self.ratings:
            self.ratings[team] = (
                self.regression_power * mean_rating
                + (1 - self.regression_power) * self.ratings[team]
            )

    def predict_proba(self, home: str, away: str) -> np.ndarray:
        r_home = self.get_rating(home) + self.home_adv
        r_away = self.get_rating(away)
        e_home = self.expected_score(r_home, r_away)
        e_away = 1.0 - e_home
        e_draw = 1.0 - abs(e_home - e_away)
        total = e_home + e_draw + e_away
        return np.array([e_home / total, e_draw / total, e_away / total])

    def reset(self):
        self.ratings = {}
