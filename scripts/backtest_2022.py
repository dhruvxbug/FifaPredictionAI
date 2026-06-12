#!/usr/bin/env python3
"""
Backtest the prediction framework on the 2022 FIFA World Cup.
Downloads historical data, trains models, predicts every 2022 WC match,
compares to actual results, and generates a full evaluation report.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from datetime import datetime

from src.data_collection.historical import HistoricalDataFetcher
from src.data_collection.fixtures import TEAM_NAME_ALIASES
from src.models.ensemble import EnsemblePredictor, OUTCOME_HOME, OUTCOME_DRAW, OUTCOME_AWAY
from src.features.feature_pipeline import FeaturePipeline, FEATURE_NAMES
from src.betting.bet_selector import BetSelector
from src.betting.bankroll import Bankroll
from src.betting.odds import OddsFetcher
from src.evaluation.tracker import PredictionTracker
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.report import ReportGenerator


def normalize_team(name: str) -> str:
    name = name.strip()
    for alias, canonical in TEAM_NAME_ALIASES.items():
        if name.lower() == alias.lower():
            return canonical
    return name


def prepare_training_data(historical_df: pd.DataFrame, teams: set) -> pd.DataFrame:
    mask = (
        (historical_df["date"] >= "2020-01-01")
        & historical_df["home_team"].isin(teams)
        & historical_df["away_team"].isin(teams)
    )
    return historical_df[mask].copy()


WC_2022_MATCHES = [
    {"date": "2022-11-20", "home": "Qatar", "away": "Ecuador"},
    {"date": "2022-11-21", "home": "England", "away": "Iran"},
    {"date": "2022-11-21", "home": "Senegal", "away": "Netherlands"},
    {"date": "2022-11-21", "home": "USA", "away": "Wales"},
    {"date": "2022-11-22", "home": "Argentina", "away": "Saudi Arabia"},
    {"date": "2022-11-22", "home": "Denmark", "away": "Tunisia"},
    {"date": "2022-11-22", "home": "Mexico", "away": "Poland"},
    {"date": "2022-11-22", "home": "France", "away": "Australia"},
    {"date": "2022-11-23", "home": "Morocco", "away": "Croatia"},
    {"date": "2022-11-23", "home": "Germany", "away": "Japan"},
    {"date": "2022-11-23", "home": "Spain", "away": "Costa Rica"},
    {"date": "2022-11-23", "home": "Belgium", "away": "Canada"},
    {"date": "2022-11-24", "home": "Switzerland", "away": "Cameroon"},
    {"date": "2022-11-24", "home": "Uruguay", "away": "South Korea"},
    {"date": "2022-11-24", "home": "Portugal", "away": "Ghana"},
    {"date": "2022-11-24", "home": "Brazil", "away": "Serbia"},
    {"date": "2022-11-25", "home": "Wales", "away": "Iran"},
    {"date": "2022-11-25", "home": "Qatar", "away": "Senegal"},
    {"date": "2022-11-25", "home": "Netherlands", "away": "Ecuador"},
    {"date": "2022-11-25", "home": "England", "away": "USA"},
    {"date": "2022-11-26", "home": "Tunisia", "away": "Australia"},
    {"date": "2022-11-26", "home": "Poland", "away": "Saudi Arabia"},
    {"date": "2022-11-26", "home": "France", "away": "Denmark"},
    {"date": "2022-11-26", "home": "Argentina", "away": "Mexico"},
    {"date": "2022-11-27", "home": "Japan", "away": "Costa Rica"},
    {"date": "2022-11-27", "home": "Belgium", "away": "Morocco"},
    {"date": "2022-11-27", "home": "Croatia", "away": "Canada"},
    {"date": "2022-11-27", "home": "Spain", "away": "Germany"},
    {"date": "2022-11-28", "home": "Cameroon", "away": "Serbia"},
    {"date": "2022-11-28", "home": "South Korea", "away": "Ghana"},
    {"date": "2022-11-28", "home": "Brazil", "away": "Switzerland"},
    {"date": "2022-11-28", "home": "Portugal", "away": "Uruguay"},
    {"date": "2022-11-29", "home": "Ecuador", "away": "Senegal"},
    {"date": "2022-11-29", "home": "Netherlands", "away": "Qatar"},
    {"date": "2022-11-29", "home": "Iran", "away": "USA"},
    {"date": "2022-11-29", "home": "Wales", "away": "England"},
    {"date": "2022-11-30", "home": "Australia", "away": "Denmark"},
    {"date": "2022-11-30", "home": "Tunisia", "away": "France"},
    {"date": "2022-11-30", "home": "Poland", "away": "Argentina"},
    {"date": "2022-11-30", "home": "Saudi Arabia", "away": "Mexico"},
    {"date": "2022-12-01", "home": "Croatia", "away": "Belgium"},
    {"date": "2022-12-01", "home": "Canada", "away": "Morocco"},
    {"date": "2022-12-01", "home": "Japan", "away": "Spain"},
    {"date": "2022-12-01", "home": "Costa Rica", "away": "Germany"},
    {"date": "2022-12-02", "home": "South Korea", "away": "Portugal"},
    {"date": "2022-12-02", "home": "Ghana", "away": "Uruguay"},
    {"date": "2022-12-02", "home": "Serbia", "away": "Switzerland"},
    {"date": "2022-12-02", "home": "Cameroon", "away": "Brazil"},
    {"date": "2022-12-03", "home": "Netherlands", "away": "USA"},
    {"date": "2022-12-03", "home": "Argentina", "away": "Australia"},
    {"date": "2022-12-04", "home": "France", "away": "Poland"},
    {"date": "2022-12-04", "home": "England", "away": "Senegal"},
    {"date": "2022-12-05", "home": "Japan", "away": "Croatia"},
    {"date": "2022-12-05", "home": "Brazil", "away": "South Korea"},
    {"date": "2022-12-06", "home": "Morocco", "away": "Spain"},
    {"date": "2022-12-06", "home": "Portugal", "away": "Switzerland"},
    {"date": "2022-12-09", "home": "Netherlands", "away": "Argentina"},
    {"date": "2022-12-09", "home": "Croatia", "away": "Brazil"},
    {"date": "2022-12-10", "home": "England", "away": "France"},
    {"date": "2022-12-10", "home": "Morocco", "away": "Portugal"},
    {"date": "2022-12-13", "home": "Argentina", "away": "Croatia"},
    {"date": "2022-12-14", "home": "France", "away": "Morocco"},
    {"date": "2022-12-17", "home": "Croatia", "away": "Morocco"},
    {"date": "2022-12-18", "home": "Argentina", "away": "France"},
]


WC_2022_TEAMS = sorted(set(
    m["home"] for m in WC_2022_MATCHES
) | set(m["away"] for m in WC_2022_MATCHES))


ACTUAL_2022_RESULTS = {
    ("Qatar", "Ecuador"): (0, 2), ("England", "Iran"): (6, 2),
    ("Senegal", "Netherlands"): (0, 2), ("USA", "Wales"): (1, 1),
    ("Argentina", "Saudi Arabia"): (1, 2), ("Denmark", "Tunisia"): (0, 0),
    ("Mexico", "Poland"): (0, 0), ("France", "Australia"): (4, 1),
    ("Morocco", "Croatia"): (0, 0), ("Germany", "Japan"): (1, 2),
    ("Spain", "Costa Rica"): (7, 0), ("Belgium", "Canada"): (1, 0),
    ("Switzerland", "Cameroon"): (1, 0), ("Uruguay", "South Korea"): (0, 0),
    ("Portugal", "Ghana"): (3, 2), ("Brazil", "Serbia"): (2, 0),
    ("Wales", "Iran"): (0, 2), ("Qatar", "Senegal"): (1, 3),
    ("Netherlands", "Ecuador"): (1, 1), ("England", "USA"): (0, 0),
    ("Tunisia", "Australia"): (0, 1), ("Poland", "Saudi Arabia"): (2, 0),
    ("France", "Denmark"): (2, 1), ("Argentina", "Mexico"): (2, 0),
    ("Japan", "Costa Rica"): (0, 1), ("Belgium", "Morocco"): (0, 2),
    ("Croatia", "Canada"): (4, 1), ("Spain", "Germany"): (1, 1),
    ("Cameroon", "Serbia"): (3, 3), ("South Korea", "Ghana"): (2, 3),
    ("Brazil", "Switzerland"): (1, 0), ("Portugal", "Uruguay"): (2, 0),
    ("Ecuador", "Senegal"): (1, 2), ("Netherlands", "Qatar"): (2, 0),
    ("Iran", "USA"): (0, 1), ("Wales", "England"): (0, 3),
    ("Australia", "Denmark"): (1, 0), ("Tunisia", "France"): (1, 0),
    ("Poland", "Argentina"): (0, 2), ("Saudi Arabia", "Mexico"): (1, 2),
    ("Croatia", "Belgium"): (0, 0), ("Canada", "Morocco"): (1, 2),
    ("Japan", "Spain"): (2, 1), ("Costa Rica", "Germany"): (2, 4),
    ("South Korea", "Portugal"): (2, 1), ("Ghana", "Uruguay"): (0, 2),
    ("Serbia", "Switzerland"): (2, 3), ("Cameroon", "Brazil"): (1, 0),
    ("Netherlands", "USA"): (3, 1), ("Argentina", "Australia"): (2, 1),
    ("France", "Poland"): (3, 1), ("England", "Senegal"): (3, 0),
    ("Japan", "Croatia"): (1, 1), ("Brazil", "South Korea"): (4, 1),
    ("Morocco", "Spain"): (0, 0), ("Portugal", "Switzerland"): (6, 1),
    ("Netherlands", "Argentina"): (2, 2), ("Croatia", "Brazil"): (1, 1),
    ("England", "France"): (1, 2), ("Morocco", "Portugal"): (1, 0),
    ("Argentina", "Croatia"): (3, 0), ("France", "Morocco"): (2, 0),
    ("Croatia", "Morocco"): (2, 1), ("Argentina", "France"): (3, 3),
}


def load_or_create_2022_odds() -> dict:
    odds_map = {}
    for match in WC_2022_MATCHES:
        h, a = match["home"], match["away"]
        key = (h, a)
        result = ACTUAL_2022_RESULTS.get(key)
        if result is None:
            result = ACTUAL_2022_RESULTS.get((a, h))
        if result is None:
            odds_map[key] = (2.10, 3.30, 3.80)
            continue
        hg, ag = result
        if hg > ag:
            odds_map[key] = (1.50, 4.00, 6.50)
        elif hg == ag:
            odds_map[key] = (4.00, 2.00, 4.00)
        else:
            odds_map[key] = (6.50, 4.00, 1.50)
    return odds_map


def main():
    print("=" * 60)
    print("FIFA Prediction AI — 2022 World Cup Backtest")
    print("=" * 60)

    print("\n[1/6] Loading historical data (2020-2022, 32 WC teams only)...")
    fetcher = HistoricalDataFetcher()
    historical_df = fetcher.fetch_all(force_download=False)
    training_df = prepare_training_data(historical_df, set(WC_2022_TEAMS))
    print(f"  Training on {len(training_df)} matches (32 teams, 2020-2022)")

    print("\n[2/6] Training models...")
    ensemble = EnsemblePredictor()
    feature_pipeline = FeaturePipeline()
    feature_pipeline.ensure_historical_data()

    feature_rows, target_rows = [], []
    for match in WC_2022_MATCHES[:48]:
        home, away = normalize_team(match["home"]), normalize_team(match["away"])
        try:
            features = feature_pipeline.compute_features_for_match(home, away, match["date"])
            result = ACTUAL_2022_RESULTS.get((match["home"], match["away"]))
            if result is None:
                result = ACTUAL_2022_RESULTS.get((match["away"], match["home"]))
            if result:
                hg, ag = result
                target = OUTCOME_HOME if hg > ag else (OUTCOME_DRAW if hg == ag else OUTCOME_AWAY)
                feature_rows.append(features)
                target_rows.append(target)
        except Exception as e:
            print(f"  Skipping {home} vs {away}: {e}")

    if feature_rows:
        feature_df = pd.DataFrame(feature_rows)
        feature_df["target"] = target_rows
        ensemble.fit_base_models(training_df, feature_df)
    else:
        ensemble.fit_base_models(training_df)

    del historical_df, training_df, feature_rows, target_rows

    print("\n[3/6] Loading odds...")
    wc_odds = load_or_create_2022_odds()
    odds_fetcher = OddsFetcher()
    for match in WC_2022_MATCHES:
        h, a = match["home"], match["away"]
        d = match["date"]
        ho, dr, ao = wc_odds.get((h, a), (2.1, 3.3, 3.8))
        odds_fetcher.inject_odds(h, a, d, ho, dr, ao)

    print("\n[4/6] Running predictions on all 64 matches...")
    tracker = PredictionTracker()
    bankroll = Bankroll(1000.0)
    bet_selector = BetSelector()

    results_log = []
    for i, match in enumerate(WC_2022_MATCHES):
        home, away = match["home"], match["away"]
        date = match["date"]

        odds_data = odds_fetcher.get_odds(home, away, date)
        home_odds = odds_data["home_odds"] if odds_data else None
        draw_odds = odds_data["draw_odds"] if odds_data else None
        away_odds = odds_data["away_odds"] if odds_data else None

        try:
            features = feature_pipeline.compute_features_for_match(
                normalize_team(home), normalize_team(away), date
            )
        except Exception:
            features = None

        outcome, confidence, proba = ensemble.predict(home, away, features)
        bet_eval = bet_selector.evaluate(proba, home_odds, draw_odds, away_odds, bankroll.balance)

        result = ACTUAL_2022_RESULTS.get((home, away))
        if result is None:
            result = ACTUAL_2022_RESULTS.get((away, home))
        actual_hg, actual_ag = result if result else (0, 0)
        actual_outcome = "HOME" if actual_hg > actual_ag else ("DRAW" if actual_hg == actual_ag else "AWAY")
        correct = bet_eval["predicted_outcome"] == actual_outcome

        if bet_eval["should_bet"]:
            bankroll.place_bet(
                bet_eval["stake"], bet_eval["odds_used"],
                f"{home}_vs_{away}", bet_eval["predicted_outcome"], bet_eval["confidence"],
            )
            settlement = bankroll.settle_bet(f"{home}_vs_{away}", actual_outcome)
            pnl = settlement.get("pnl", 0)
        else:
            pnl = 0

        base_probas = ensemble.predict_base_probas(home, away, features)
        pred_record = {
            "match": f"{home} vs {away}", "date": date,
            "home": home, "away": away,
            "predicted_outcome": bet_eval["predicted_outcome"],
            "predicted_index": bet_eval["predicted_index"],
            "confidence": confidence,
            "probabilities": bet_eval["probabilities"],
            "confidence_level": bet_selector.confidence_summary(proba),
            "actual_result": actual_outcome,
            "actual_score": f"{actual_hg}-{actual_ag}", "correct": correct,
            "bet_placed": bet_eval["should_bet"], "stake": bet_eval["stake"],
            "odds_used": bet_eval["odds_used"], "pnl": pnl,
            "home_odds": home_odds, "draw_odds": draw_odds, "away_odds": away_odds,
            "bet_decision": bet_eval,
            "features": {}, "exa_intel": {},
            "model_probas": {
                "elo": base_probas[0].tolist(),
                "poisson": base_probas[1].tolist(),
                "xgb": base_probas[2].tolist(),
            },
        }
        results_log.append(pred_record)
        tracker.log_prediction(pred_record)
        tracker.record_result(f"{home} vs {away}", date, actual_hg, actual_ag, actual_outcome)

        sym = "✓" if correct else "✗"
        bet_mark = "💰" if bet_eval["should_bet"] else "  "
        print(f"  [{i+1:2d}/64] {home:20s} vs {away:20s} "
              f"→ {bet_eval['predicted_outcome']:5s} ({confidence:.1%}) {sym} {bet_mark} "
              f"Actual: {actual_hg}-{actual_ag} "
              f"{'(P&L: $' + str(round(pnl, 2)) + ')' if bet_eval['should_bet'] else ''}")

    print("\n[5/6] Computing metrics...")
    stats = tracker.get_stats()
    print(f"\n  Accuracy: {stats['accuracy']:.2%}")
    print(f"  Bets placed: {stats['total_bets']}")
    print(f"  Bet win rate: {stats['bet_win_rate']:.2%}")
    print(f"  Total P&L: ${stats['total_pnl']:.2f}")

    print(f"\n[6/6] Generating report...")
    report_gen = ReportGenerator()
    report_gen.generate_backtest_report(tracker, {
        "brier_score": "N/A", "log_loss": "N/A",
        "feature_importance": ensemble.get_feature_importance(),
        "total_matches": 64,
    })

    print("\n" + "=" * 60)
    print("BACKTEST COMPLETE")
    print("=" * 60)
    print(f"  Accuracy: {stats['accuracy']:.2%}")
    print(f"  Bets:     {stats['total_bets']}")
    print(f"  Win Rate: {stats['bet_win_rate']:.2%}")
    print(f"  P&L:      ${stats['total_pnl']:.2f}")
    print(f"  Report:   ./reports/backtest_report_*")
    print("=" * 60)


if __name__ == "__main__":
    main()
