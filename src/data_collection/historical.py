import pandas as pd
import requests
from pathlib import Path
from io import StringIO

from src.utils.config import config


class HistoricalDataFetcher:
    SOURCE_URL = "https://github.com/martj42/international_results/raw/master/results.csv"

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or config["data"]["data_dir"] / "historical")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def fetch_all(self, force_download: bool = False) -> pd.DataFrame:
        local_path = self.data_dir / "international_results.csv"
        if local_path.exists() and not force_download:
            return pd.read_csv(local_path)

        print(f"Downloading historical data from {self.SOURCE_URL}...")
        resp = requests.get(self.SOURCE_URL, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        df.to_csv(local_path, index=False)
        print(f"Saved {len(df)} matches to {local_path}")
        return df

    def fetch_2022_world_cup(self, df: pd.DataFrame = None) -> pd.DataFrame:
        if df is None:
            df = self.fetch_all()
        wc_2022 = df[
            (df["tournament"].str.contains("FIFA World Cup", case=False, na=False))
            & (df["date"] >= "2022-11-01")
            & (df["date"] <= "2022-12-31")
        ].copy()
        return wc_2022

    def get_head_to_head(
        self, team1: str, team2: str, df: pd.DataFrame = None, max_matches: int = 5
    ) -> pd.DataFrame:
        if df is None:
            df = self.fetch_all()
        mask = ((df["home_team"] == team1) & (df["away_team"] == team2)) | (
            (df["home_team"] == team2) & (df["away_team"] == team1)
        )
        h2h = df[mask].sort_values("date", ascending=False).head(max_matches)
        return h2h

    def get_recent_form(
        self, team: str, df: pd.DataFrame = None, max_matches: int = 10
    ) -> pd.DataFrame:
        if df is None:
            df = self.fetch_all()
        mask = (df["home_team"] == team) | (df["away_team"] == team)
        matches = df[mask].sort_values("date", ascending=False).head(max_matches)
        return matches
