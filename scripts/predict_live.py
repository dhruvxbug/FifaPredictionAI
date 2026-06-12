#!/usr/bin/env python3
"""
Predict live/upcoming FIFA World Cup 2026 matches.
Useful for running before each matchday during the tournament.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import argparse
from datetime import datetime, date

from src.prediction.match_predictor import MatchPredictor
from src.data_collection.fixtures import WC_2026_FIXTURES, WC_2026_GROUPS
from src.evaluation.tracker import PredictionTracker


def filter_upcoming_matches(max_results: int = 10) -> list[dict]:
    today = date.today()
    upcoming = []
    for fix in WC_2026_FIXTURES:
        fix_date = datetime.strptime(fix["date"], "%Y-%m-%d").date()
        if fix_date >= today and "1" not in fix.get("home", "") and "3" not in fix.get("home", ""):
            if fix["stage"] == "group":
                upcoming.append(fix)
            elif fix["stage"] in ("round_of_32", "round_of_16", "quarter_final",
                                  "semi_final", "final", "third_place"):
                if not fix["home"].startswith(("W", "L")) and not fix["away"].startswith(("W", "L")):
                    upcoming.append(fix)
    return upcoming[:max_results]


def predict_single(home: str, away: str, date_str: str = "",
                   use_exa: bool = False):
    predictor = MatchPredictor(use_exa=use_exa)
    result = predictor.predict_match(home, away, date_str)
    _print_prediction(result)
    return result


def predict_upcoming(use_exa: bool = False):
    predictor = MatchPredictor(use_exa=use_exa)
    matches = filter_upcoming_matches(20)
    if not matches:
        print("No upcoming matches found.")
        return

    print(f"\n{'='*70}")
    print(f"FIFA World Cup 2026 — Upcoming Match Predictions")
    print(f"{'='*70}\n")

    for i, fix in enumerate(matches, 1):
        result = predictor.predict_match(fix["home"], fix["away"], fix["date"])
        _print_prediction(result, i)

    print(f"\n{'='*70}")
    stats = predictor.tracker.get_stats()
    print(f"Total predictions logged: {stats['total_predictions']}")
    print(f"{'='*70}\n")


def _print_prediction(result: dict, idx: int = None):
    prefix = f"[{idx}] " if idx else ""
    print(f"{prefix}{result['match']} ({result.get('date', 'TBD')})")
    print(f"   Predicted: {result['predicted_outcome']:5s} "
          f"(Confidence: {result['confidence']:.1%})")
    print(f"   Probs: H={result['probabilities']['home']:.1%} "
          f"D={result['probabilities']['draw']:.1%} "
          f"A={result['probabilities']['away']:.1%}")
    print(f"   Level: {result['confidence_level']}")
    if result["bet_decision"]["should_bet"]:
        print(f"   💰 BET: ${result['bet_decision']['stake']:.2f} "
              f"on {result['bet_decision']['predicted_outcome']} "
              f"@ {result['bet_decision']['odds_used']:.2f}")
    else:
        print(f"   No bet (below {result['bet_decision']['confidence']:.1%} threshold)")
    print()


def main():
    parser = argparse.ArgumentParser(description="FIFA 2026 Match Predictor")
    parser.add_argument("command", nargs="?", default="upcoming",
                        choices=["upcoming", "match"],
                        help="Command: 'upcoming' or 'match'")
    parser.add_argument("--home", help="Home team name")
    parser.add_argument("--away", help="Away team name")
    parser.add_argument("--date", default="", help="Match date (YYYY-MM-DD)")
    parser.add_argument("--exa", action="store_true", help="Use Exa AI for web intelligence")
    args = parser.parse_args()

    if args.command == "match":
        if not args.home or not args.away:
            print("Usage: python predict_live.py match --home <team> --away <team> [--date YYYY-MM-DD] [--exa]")
            return
        predict_single(args.home, args.away, args.date, args.exa)
    else:
        predict_upcoming(args.exa)


if __name__ == "__main__":
    main()
