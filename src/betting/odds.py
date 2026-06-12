"""Fetches match odds from various sources."""

import requests
from typing import Optional
from src.utils.cache import TTLCache


class OddsFetcher:
    def __init__(self):
        self.cache = TTLCache(ttl_hours=6)

    def get_odds(self, home: str, away: str, date: str = "") -> Optional[dict]:
        cache_key = f"odds:{home}:{away}:{date}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        return None

    def inject_odds(self, home: str, away: str, date: str,
                    home_odds: float, draw_odds: float, away_odds: float):
        cache_key = f"odds:{home}:{away}:{date}"
        self.cache.set(cache_key, {
            "home_odds": home_odds,
            "draw_odds": draw_odds,
            "away_odds": away_odds,
        })

    def inject_2022_wc_odds(self, odds_df):
        """Load 2022 WC archived odds for backtesting."""
        for _, row in odds_df.iterrows():
            self.inject_odds(
                row["home_team"], row["away_team"], row["date"],
                row.get("home_odds", 2.0), row.get("draw_odds", 3.5),
                row.get("away_odds", 3.0),
            )
