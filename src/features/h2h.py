import numpy as np
import pandas as pd

from src.data_collection.historical import HistoricalDataFetcher


class H2HAnalysis:
    def __init__(self, max_matches: int = 5, decay_factor: float = 0.85):
        self.fetcher = HistoricalDataFetcher()
        self.max_matches = max_matches
        self.decay = decay_factor

    def compute_all(self, team1: str, team2: str, df: pd.DataFrame = None) -> dict:
        if df is None:
            df = self.fetcher.fetch_all()
        h2h = self.fetcher.get_head_to_head(team1, team2, df, self.max_matches)
        return self._analyze_h2h(team1, team2, h2h)

    def _analyze_h2h(self, team1: str, team2: str, h2h: pd.DataFrame) -> dict:
        if h2h.empty:
            return {
                "h2h_team1_wins": 0,
                "h2h_team2_wins": 0,
                "h2h_draws": 0,
                "h2h_team1_goals_avg": 0.0,
                "h2h_team2_goals_avg": 0.0,
                "h2h_games_played": 0,
                "h2h_team1_unbeaten_streak": 0,
            }

        t1_wins = 0
        t2_wins = 0
        draws = 0
        t1_goals = []
        t2_goals = []
        last_winner = None
        streak = 0

        for _, match in h2h.iterrows():
            if match["home_team"] == team1:
                hg, ag = match["home_score"], match["away_score"]
            else:
                hg, ag = match["away_score"], match["home_score"]

            t1_goals.append(hg)
            t2_goals.append(ag)

            if hg > ag:
                t1_wins += 1
                winner = 1
            elif hg < ag:
                t2_wins += 1
                winner = 2
            else:
                draws += 1
                winner = 0

            if last_winner is None:
                streak = 1 if winner == 1 else (-1 if winner == 2 else 0)
            elif winner != 0:
                if winner == last_winner:
                    streak += 1 if winner == 1 else -1
                else:
                    streak = 1 if winner == 1 else -1
            last_winner = winner if winner != 0 else last_winner

        return {
            "h2h_team1_wins": t1_wins,
            "h2h_team2_wins": t2_wins,
            "h2h_draws": draws,
            "h2h_team1_goals_avg": round(np.mean(t1_goals), 3) if t1_goals else 0.0,
            "h2h_team2_goals_avg": round(np.mean(t2_goals), 3) if t2_goals else 0.0,
            "h2h_games_played": len(h2h),
            "h2h_team1_unbeaten_streak": streak,
        }
