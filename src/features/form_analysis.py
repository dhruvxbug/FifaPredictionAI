import numpy as np
import pandas as pd

from src.data_collection.historical import HistoricalDataFetcher


class FormAnalysis:
    def __init__(self, max_matches: int = 10, decay_factor: float = 0.9):
        self.fetcher = HistoricalDataFetcher()
        self.max_matches = max_matches
        self.decay = decay_factor

    def compute_all(self, team: str, opponent: str = "", df: pd.DataFrame = None) -> dict:
        if df is None:
            df = self.fetcher.fetch_all()
        matches = self.fetcher.get_recent_form(team, df, self.max_matches)
        return self._analyze_form(team, matches)

    def _analyze_form(self, team: str, matches: pd.DataFrame) -> dict:
        if matches.empty:
            return {
                "form_points": 1.5,
                "form_goals_scored_avg": 1.0,
                "form_goals_conceded_avg": 1.0,
                "form_games_played": 0,
                "form_win_rate": 0.0,
                "form_streak": 0,
                "form_weighted_points": 0.0,
            }

        weights = np.array([self.decay ** i for i in range(len(matches))])
        weights = weights / weights.sum()

        total_points = 0.0
        total_goals_for = 0.0
        total_goals_against = 0.0
        streak = 0
        last_result = None

        for i, (_, match) in enumerate(matches.iterrows()):
            w = weights[i]
            is_home = match["home_team"] == team
            gf = match["home_score"] if is_home else match["away_score"]
            ga = match["away_score"] if is_home else match["home_score"]

            total_goals_for += gf * w
            total_goals_against += ga * w

            if gf > ga:
                total_points += 3 * w
                result = "W"
            elif gf == ga:
                total_points += 1 * w
                result = "D"
            else:
                result = "L"

            if i == 0:
                streak = 1 if result in ("W", "D") else -1
                last_result = result
            else:
                if result == "W" and last_result == "W":
                    streak += 1
                elif result == "L" and last_result == "L":
                    streak -= 1
                else:
                    streak = 0
                last_result = result

        return {
            "form_points": round(total_points, 2),
            "form_goals_scored_avg": round(total_goals_for, 3),
            "form_goals_conceded_avg": round(total_goals_against, 3),
            "form_games_played": len(matches),
            "form_win_rate": round((matches.apply(
                lambda r: (r["home_team"] == team and r["home_score"] > r["away_score"])
                          or (r["away_team"] == team and r["away_score"] > r["home_score"]),
                axis=1
            ).sum()) / max(len(matches), 1), 3),
            "form_streak": streak,
            "form_weighted_points": round(total_points, 2),
        }
