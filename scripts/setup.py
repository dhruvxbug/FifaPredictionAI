#!/usr/bin/env python3
"""
One-time setup script for FifaPredictionAI.
Downloads historical data, creates database, and pre-computes base data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from pathlib import Path

from src.data_collection.historical import HistoricalDataFetcher
from src.utils.config import config


def create_directories():
    dirs = [
        config["data"]["data_dir"],
        config["data"]["data_dir"] / "raw",
        config["data"]["data_dir"] / "processed",
        config["data"]["data_dir"] / "historical",
        config["data"]["data_dir"] / "external",
        config["data"]["data_dir"] / "cache",
        config["data"]["reports_dir"],
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d}/")
    print(f"  ✓ {config['data']['db_path'].parent}/")


def download_historical_data():
    print("\n[2/4] Downloading historical international match data...")
    fetcher = HistoricalDataFetcher()
    df = fetcher.fetch_all(force_download=True)
    print(f"  Downloaded {len(df)} matches")

    wc_2022 = fetcher.fetch_2022_world_cup(df)
    print(f"  Found {len(wc_2022)} 2022 World Cup matches")

    team_count = df["home_team"].nunique()
    print(f"  Unique teams in dataset: {team_count}")
    return df


def initialize_database():
    print("\n[3/4] Initializing prediction database...")
    from src.evaluation.tracker import PredictionTracker
    tracker = PredictionTracker()
    print(f"  Database created at: {config['data']['db_path']}")

    stats = tracker.get_stats()
    print(f"  Ready: {stats['total_predictions']} existing predictions")
    return tracker


def create_env_file():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("\n[4/4] Creating .env file from template...")
        example = Path(__file__).parent.parent / ".env.example"
        if example.exists():
            env_path.write_text(example.read_text())
            print(f"  Created {env_path}")
            print("  ⚠  Edit it to add your EXA_API_KEY")
        else:
            print("  ⚠  .env.example not found, skipping")
    else:
        print("\n[4/4] .env already exists, skipping")


def main():
    print("=" * 60)
    print("FIFA Prediction AI — Setup")
    print("=" * 60)

    print("\n[1/4] Creating directory structure...")
    create_directories()

    download_historical_data()
    initialize_database()
    create_env_file()

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Add your EXA_API_KEY to .env (or skip for local-only mode)")
    print("  2. Run the 2022 backtest:  python scripts/backtest_2022.py")
    print("  3. Predict matches:        python scripts/predict_live.py upcoming")
    print("  4. Record results:         python scripts/evaluate_results.py record")
    print("  5. View summary:           python scripts/evaluate_results.py summary")
    print("=" * 60)


if __name__ == "__main__":
    main()
