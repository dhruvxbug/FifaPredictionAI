#!/usr/bin/env python3
"""
Predict all FIFA World Cup 2026 group stage matches (72 fixtures, 12 groups).
Skips already-predicted matches using SQLite cache.
Uses Exa AI for web intelligence (injuries, sentiment) if available.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_collection.historical import HistoricalDataFetcher
from src.data_collection.fixtures import WC_2026_FIXTURES, WC_2026_GROUPS, TEAM_NAME_ALIASES
from src.models.ensemble import EnsemblePredictor, OUTCOME_HOME, OUTCOME_DRAW, OUTCOME_AWAY
from src.features.feature_pipeline import FeaturePipeline, FEATURE_NAMES
from src.prediction.match_predictor import MatchPredictor
from src.evaluation.tracker import PredictionTracker


GROUP_STAGE = [f for f in WC_2026_FIXTURES if f["stage"] == "group"]
OUTCOME_EMOJI = {0: "🟢", 1: "🟡", 2: "🔴"}
CONFIDENCE_BAR = {0: "⬜", 1: "🟨", 2: "🟩", 3: "🟦"}


def normalize_team(name: str) -> str:
    name = name.strip()
    for alias, canonical in TEAM_NAME_ALIASES.items():
        if name.lower() == alias.lower():
            return canonical
    return name


def train_models():
    print("=" * 70)
    print("  Training Phase")
    print("=" * 70)

    print("\n[1/3] Loading historical match data (2000-present)...")
    fetcher = HistoricalDataFetcher()
    historical_df = fetcher.fetch_all(force_download=False)
    all_teams = set(
        t for fix in GROUP_STAGE for t in [normalize_team(fix["home"]), normalize_team(fix["away"])]
    )

    mask = historical_df["home_team"].isin(all_teams) & historical_df["away_team"].isin(all_teams)
    training_df = historical_df[mask].copy()
    print(f"  Training on {len(training_df)} matches involving 2026 WC teams")

    print("\n[2/3] Building feature matrix from historical data and training ensemble...")
    ensemble = EnsemblePredictor()
    feature_pipeline = FeaturePipeline()
    feature_pipeline.ensure_historical_data()

    hist_mask = (
        (historical_df["date"] >= "2018-01-01")
        & (historical_df["date"] <= "2025-12-31")
        & historical_df["home_team"].isin(all_teams)
        & historical_df["away_team"].isin(all_teams)
    )
    hist_recent = historical_df[hist_mask].head(2000)

    feature_rows, target_rows = [], []
    for _, row in hist_recent.iterrows():
        home, away = normalize_team(row["home_team"]), normalize_team(row["away_team"])
        date_str = str(row["date"])[:10]
        try:
            features = feature_pipeline.compute_features_for_match(home, away, date_str)
            hg, ag = int(row["home_score"]), int(row["away_score"])
            target = OUTCOME_HOME if hg > ag else (OUTCOME_DRAW if hg == ag else OUTCOME_AWAY)
            feature_rows.append(features)
            target_rows.append(target)
        except Exception:
            pass

    print(f"  Training XGBoost on {len(feature_rows)} historical matches with actual results")

    if feature_rows:
        feature_df = pd.DataFrame(feature_rows)
        feature_df["target"] = target_rows
        ensemble.fit_base_models(training_df, feature_df)
    else:
        ensemble.fit_base_models(training_df)

    print("  Models trained: Elo ✓ | Dixon-Coles ✓ | XGBoost ✓")

    print("\n[3/3] Initializing MatchPredictor...")
    predictor = MatchPredictor(use_exa=True)
    predictor.ensemble = ensemble
    predictor.features = feature_pipeline

    return predictor, feature_pipeline


def print_match_card(result: dict, idx: int, total: int, elapsed: float):
    group = result.get("group", "?")
    home, away = result["home"], result["away"]
    date = result.get("date", "")
    outcome = result["predicted_outcome"]
    conf = result["confidence"]
    probs = result["probabilities"]
    level = result["confidence_level"]
    bet = result["bet_decision"]
    cached = result.get("_cached", False)

    cache_tag = " [CACHED]" if cached else ""
    status = OUTCOME_EMOJI.get(result["predicted_index"], "⚪")

    prob_str = f"H={probs['home']:.0%} D={probs['draw']:.0%} A={probs['away']:.0%}"

    conf_levels = {"HIGH_CONFIDENCE": "🟦 HIGH", "GOOD_VALUE": "🟩 GOOD", "SPECULATIVE": "🟨 SPEC", "NO_BET": "⬜ LOW"}
    level_str = conf_levels.get(level, level)

    bet_str = ""
    if bet.get("should_bet"):
        bet_str = f" | 💰 ${bet['stake']:.0f} on {bet['predicted_outcome']} @ {bet['odds_used']:.2f}"

    print(f"  [{idx:2d}/{total}]{cache_tag} {status} {home:22s} vs {away:22s} "
          f"({date}) [{group}]")
    print(f"       → {outcome:5s}  {conf:.1%}  |  {prob_str}  |  {level_str}{bet_str}")
    if elapsed > 1:
        print(f"       ⏱  {elapsed:.1f}s")
    print()


def main():
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + "  FIFA World Cup 2026 — Group Stage Predictions".center(68) + "║")
    print("║" + f"  {len(GROUP_STAGE)} matches across {len(WC_2026_GROUPS)} groups".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    predictor, feature_pipeline = train_models()

    tracker = PredictionTracker()

    already_done = sum(1 for f in GROUP_STAGE
                       if tracker.prediction_exists(normalize_team(f["home"]),
                                                     normalize_team(f["away"]), f["date"]))
    total_new = len(GROUP_STAGE) - already_done

    print()
    print("=" * 70)
    print(f"  Prediction Phase — {already_done} cached, {total_new} new")
    print("=" * 70)
    print()

    results = []
    start_all = time.time()

    for idx, fix in enumerate(GROUP_STAGE, 1):
        home, away = normalize_team(fix["home"]), normalize_team(fix["away"])
        date = fix["date"]
        group = fix["group"]
        match_loc = "New York"

        if tracker.prediction_exists(home, away, date):
            cached = tracker.get_prediction(home, away, date)
            cached["_cached"] = True
            cached["group"] = group
            results.append(cached)
            print_match_card(cached, idx, len(GROUP_STAGE), 0)
            continue

        start = time.time()
        try:
            result = predictor.predict_match(
                home, away, date,
                match_location=match_loc,
                use_exa=True,
                skip_cached=True,
            )
            result["group"] = group
            result["_cached"] = False
            elapsed = time.time() - start
            results.append(result)
            print_match_card(result, idx, len(GROUP_STAGE), elapsed)
        except Exception as e:
            print(f"  [{idx:2d}/{len(GROUP_STAGE)}] ❌ {home:22s} vs {away:22s} — ERROR: {e}")
            print()

    total_time = time.time() - start_all

    stats = tracker.get_stats()

    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Total matches processed: {len(results)}")
    print(f"  New predictions:         {total_new}")
    print(f"  From cache:              {already_done}")
    print(f"  Total time:              {total_time:.1f}s")
    print(f"  Avg per new match:       {total_time / max(total_new, 1):.1f}s")
    print(f"  Predictions in DB:       {stats['total_predictions']}")
    print()
    print("  Top predictions by confidence:")
    print()

    sorted_results = sorted(results, key=lambda r: r["confidence"], reverse=True)
    for i, r in enumerate(sorted_results[:10], 1):
        outcome = r["predicted_outcome"]
        conf = r["confidence"]
        home, away = r["home"], r["away"]
        date = r.get("date", "")
        emoji = OUTCOME_EMOJI.get(r["predicted_index"], "⚪")
        print(f"  {i}. {emoji} {home} vs {away} ({date}) → {outcome} @ {conf:.1%}")

    print()
    print("=" * 70)

    report_path = Path("data/predictions_group_stage.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_matches": len(results),
        "new_predictions": total_new,
        "from_cache": already_done,
        "total_time_seconds": round(total_time, 1),
        "results": [
            {
                "home": r["home"],
                "away": r["away"],
                "date": r.get("date", ""),
                "group": r.get("group", ""),
                "predicted_outcome": r["predicted_outcome"],
                "confidence": round(r["confidence"], 4),
                "probabilities": r["probabilities"],
                "confidence_level": r["confidence_level"],
                "bet_decision": {
                    "should_bet": r["bet_decision"]["should_bet"],
                    "stake": r["bet_decision"]["stake"],
                    "odds_used": r["bet_decision"]["odds_used"],
                },
            }
            for r in results
        ],
    }

    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Full results saved to: {report_path}")
    print()

    return results


if __name__ == "__main__":
    main()
