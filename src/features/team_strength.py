import math
import pandas as pd
import numpy as np

from src.data_collection.squad_data import SquadDataCollector


class TeamStrengthFeatures:
    def __init__(self):
        self.squad = SquadDataCollector()

    def compute_all(self, home_team: str, away_team: str) -> dict:
        home_data = self.squad.get_team_data(home_team)
        away_data = self.squad.get_team_data(away_team)

        home_rank = home_data.get("fifa_ranking", 50)
        away_rank = away_data.get("fifa_ranking", 50)
        home_value = home_data.get("market_value", 100_000_000)
        away_value = away_data.get("market_value", 100_000_000)

        return {
            "home_fifa_rank": home_rank,
            "away_fifa_rank": away_rank,
            "rank_diff": away_rank - home_rank,
            "rank_log_ratio": math.log(max(away_rank, 1)) - math.log(max(home_rank, 1)),
            "home_market_value": home_value,
            "away_market_value": away_value,
            "market_value_ratio": (home_value + 1) / (away_value + 1),
            "home_wc_appearances": home_data.get("wc_appearances", 0),
            "away_wc_appearances": away_data.get("wc_appearances", 0),
            "wc_exp_diff": home_data.get("wc_appearances", 0) - away_data.get("wc_appearances", 0),
            "home_avg_age": home_data.get("avg_age", 27),
            "away_avg_age": away_data.get("avg_age", 27),
            "age_diff": home_data.get("avg_age", 27) - away_data.get("avg_age", 27),
        }
