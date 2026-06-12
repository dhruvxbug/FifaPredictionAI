#!/usr/bin/env python3
"""
Post-match evaluation script. Records actual results and generates
updated performance reports.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import argparse
from src.evaluation.tracker import PredictionTracker
from src.evaluation.report import ReportGenerator


def record_result(match: str, date: str, home_goals: int, away_goals: int):
    if home_goals > away_goals:
        result = "HOME"
    elif home_goals == away_goals:
        result = "DRAW"
    else:
        result = "AWAY"

    tracker = PredictionTracker()
    tracker.record_result(match, date, home_goals, away_goals, result)
    stats = tracker.get_stats()
    print(f"Recorded: {match} → {result} ({home_goals}-{away_goals})")
    print(f"Running accuracy: {stats['accuracy']:.2%} "
          f"({stats['correct']}/{stats['settled']})")
    print(f"Bet P&L: ${stats['total_pnl']:.2f}")


def show_summary():
    tracker = PredictionTracker()
    stats = tracker.get_stats()
    unsettled = tracker.get_unsettled()

    print("\n" + "=" * 50)
    print("PREDICTION TRACKER SUMMARY")
    print("=" * 50)
    print(f"Total Predictions: {stats['total_predictions']}")
    print(f"Settled:           {stats['settled']}")
    print(f"Correct:           {stats['correct']}")
    print(f"Accuracy:          {stats['accuracy']:.2%}")
    print(f"Total Bets:        {stats['total_bets']}")
    print(f"Bets Won:          {stats['bets_won']}")
    print(f"Bet Win Rate:      {stats['bet_win_rate']:.2%}")
    print(f"Total P&L:         ${stats['total_pnl']:.2f}")
    print(f"\nUnsettled predictions: {len(unsettled)}")
    for p in unsettled[:10]:
        print(f"  - {p['match']} ({p['date']}): {p['predicted_outcome']} "
              f"({p['confidence']:.1%})")
    print("=" * 50)


def generate_report():
    tracker = PredictionTracker()
    report = ReportGenerator()
    stats = tracker.get_stats()
    report.generate_backtest_report(tracker, {
        "feature_importance": {},
        "total_matches": stats["settled"],
    })


def main():
    parser = argparse.ArgumentParser(description="Evaluate match results")
    parser.add_argument("command", nargs="?", default="summary",
                        choices=["record", "summary", "report"],
                        help="Command")
    parser.add_argument("--match", help="Match string (e.g., 'England vs France')")
    parser.add_argument("--date", help="Match date (YYYY-MM-DD)")
    parser.add_argument("--home-goals", type=int, help="Home goals")
    parser.add_argument("--away-goals", type=int, help="Away goals")
    args = parser.parse_args()

    if args.command == "record":
        if not all([args.match, args.date,
                    args.home_goals is not None, args.away_goals is not None]):
            print("Usage: python evaluate_results.py record "
                  "--match 'Home vs Away' --date YYYY-MM-DD "
                  "--home-goals X --away-goals Y")
            return
        record_result(args.match, args.date, args.home_goals, args.away_goals)
    elif args.command == "report":
        generate_report()
    else:
        show_summary()


if __name__ == "__main__":
    main()
