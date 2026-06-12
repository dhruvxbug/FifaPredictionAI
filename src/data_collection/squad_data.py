import json
from pathlib import Path
from typing import Optional

import requests

from src.utils.config import config


class SquadDataCollector:
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or config["data"]["data_dir"] / "raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._squad_cache: dict = {}

    def get_squad_value(self, team: str) -> Optional[float]:
        return self._get_team_data(team, "market_value")

    def get_fifa_ranking(self, team: str) -> Optional[int]:
        return self._get_team_data(team, "fifa_ranking")

    def get_manager(self, team: str) -> Optional[dict]:
        return self._get_team_data(team, "manager")

    def get_team_data(self, team: str) -> dict:
        """Return full team data dict, fetching if needed."""
        if team not in self._squad_cache:
            self._squad_cache[team] = self._load_team_data(team)
        return self._squad_cache[team]

    def _get_team_data(self, team: str, key: str):
        data = self.get_team_data(team)
        return data.get(key) if data else None

    def _load_team_data(self, team: str) -> dict:
        local_path = self.data_dir / f"team_{team.lower().replace(' ', '_')}.json"
        if local_path.exists():
            with open(local_path) as f:
                return json.load(f)
        base = {
            "name": team,
            "fifa_ranking": 50,
            "market_value": 100_000_000,
            "manager": {"name": "Unknown", "win_rate": 0.4, "experience_years": 3},
            "key_players": [],
            "avg_age": 27.0,
            "wc_appearances": 0,
        }
        return base

    def save_team_data(self, team: str, data: dict):
        local_path = self.data_dir / f"team_{team.lower().replace(' ', '_')}.json"
        with open(local_path, "w") as f:
            json.dump(data, f, indent=2)
        self._squad_cache[team] = data

    def fetch_fifa_rankings(self) -> dict:
        try:
            url = "https://api.fifa.com/api/v3/ranking/men"
            resp = requests.get(url, timeout=30, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                rankings = {}
                data = resp.json()
                for entry in data.get("results", []):
                    rankings[entry["name"]] = entry["rank"]
                return rankings
        except Exception:
            pass
        return {}
