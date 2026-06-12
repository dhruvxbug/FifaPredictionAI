import time
from typing import Optional

from src.utils.config import config
from src.utils.cache import TTLCache


class ExaSearchAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config["exa"].get("api_key", "")
        self.search_type = config["exa"]["search_type"]
        self.num_results = config["exa"]["num_results"]
        self.rate_limit = config["exa"]["rate_limit_per_minute"]
        self.cache = TTLCache(ttl_hours=12)
        self._last_call = 0.0
        self._exa = None

    def _init_client(self):
        if self._exa is not None:
            return
        if not self.api_key:
            raise ValueError(
                "Exa API key not set. Set EXA_API_KEY in .env or pass api_key."
            )
        try:
            from exa_py import Exa
            self._exa = Exa(api_key=self.api_key)
        except ImportError:
            raise ImportError("exa-py not installed. Run: pip install exa-py")

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_call = time.time()

    def search_injuries(self, team_name: str, days_before_match: int = 2) -> dict:
        query = (
            f"{team_name} football team injuries squad news "
            f"{days_before_match} days before match 2026"
        )
        return self._search_with_cache(f"injuries:{team_name}", query)

    def search_sentiment(self, team_name: str, opponent: str = "") -> dict:
        opp = f" vs {opponent}" if opponent else ""
        query = (
            f"{team_name}{opp} World Cup 2026 fan confidence form "
            f"preview prediction"
        )
        return self._search_with_cache(f"sentiment:{team_name}:{opponent}", query)

    def search_lineup_news(self, team_name: str, opponent: str = "") -> dict:
        opp = f" vs {opponent}" if opponent else ""
        query = (
            f"{team_name}{opp} World Cup 2026 expected lineup "
            f"predicted XI starting eleven"
        )
        return self._search_with_cache(f"lineup:{team_name}:{opponent}", query)

    def search_manager_press(self, team_name: str) -> dict:
        query = (
            f"{team_name} manager press conference World Cup 2026 "
            f"team news tactics"
        )
        return self._search_with_cache(f"manager:{team_name}", query)

    def search_team_preview(self, team_name: str, opponent: str = "") -> dict:
        opp = f" vs {opponent}" if opponent else ""
        query = (
            f"{team_name}{opp} World Cup 2026 match preview "
            f"prediction odds analysis"
        )
        return self._search_with_cache(f"preview:{team_name}:{opponent}", query)

    def _search_with_cache(self, cache_key: str, query: str) -> dict:
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        self._rate_limit()
        self._init_client()

        try:
            results = self._exa.search(
                query,
                type=self.search_type,
                num_results=self.num_results,
                contents={"highlights": True},
            )
            parsed = self._parse_results(results)
            self.cache.set(cache_key, parsed)
            return parsed
        except Exception as e:
            return {"error": str(e), "results": []}

    def _parse_results(self, results) -> dict:
        parsed = {"results": [], "summary": ""}
        if hasattr(results, "results"):
            for r in results.results[: self.num_results]:
                entry = {"title": r.title, "url": r.url}
                if hasattr(r, "highlights") and r.highlights:
                    entry["highlights"] = r.highlights[:3]
                parsed["results"].append(entry)
        if hasattr(results, "output") and hasattr(results.output, "content"):
            parsed["summary"] = results.output.content
        return parsed

    def get_team_intelligence(self, team: str, opponent: str = "") -> dict:
        return {
            "injuries": self.search_injuries(team),
            "sentiment": self.search_sentiment(team, opponent),
            "lineup_news": self.search_lineup_news(team, opponent),
            "manager_news": self.search_manager_press(team),
            "match_preview": self.search_team_preview(team, opponent),
        }
