import copy
import numpy as np
from collections import defaultdict

from src.data_collection.fixtures import WC_2026_FIXTURES, WC_2026_GROUPS


class TournamentSimulator:
    def __init__(self, match_predictor):
        self.predictor = match_predictor
        self.group_standings = {}
        self.knockout_results = {}
        self.champion = None

    def simulate_group_stage(self) -> dict:
        groups = defaultdict(lambda: defaultdict(lambda: {"pts": 0, "gd": 0, "gf": 0, "ga": 0, "played": 0}))

        for fix in WC_2026_FIXTURES:
            if fix["stage"] != "group":
                continue
            home, away = fix["home"], fix["away"]
            grp = fix["group"]
            prediction = self.predictor.predict_match(home, away, fix["date"])
            outcome = prediction["predicted_index"]

            if outcome == 0:
                groups[grp][home]["pts"] += 3
                groups[grp][home]["gd"] += 1
                groups[grp][away]["gd"] -= 1
                groups[grp][home]["gf"] += 1
                groups[grp][away]["ga"] += 1
            elif outcome == 1:
                groups[grp][home]["pts"] += 1
                groups[grp][away]["pts"] += 1
            else:
                groups[grp][away]["pts"] += 3
                groups[grp][away]["gd"] += 1
                groups[grp][home]["gd"] -= 1
                groups[grp][away]["gf"] += 1
                groups[grp][home]["ga"] += 1

            groups[grp][home]["played"] += 1
            groups[grp][away]["played"] += 1

        self.group_standings = {}
        for grp, teams in groups.items():
            sorted_teams = sorted(
                teams.items(),
                key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]),
                reverse=True,
            )
            self.group_standings[grp] = [
                {"team": t, **s} for t, s in sorted_teams
            ]

        return self.group_standings

    def _get_knockout_winner(self, home: str, away: str, date: str) -> str:
        prediction = self.predictor.predict_match(home, away, date)
        outcome = prediction["predicted_index"]
        return home if outcome == 0 else away

    def simulate_knockout(self, round_of_32_matchups: list[tuple] = None):
        if round_of_32_matchups:
            matchups = round_of_32_matchups
        else:
            top_teams = []
            third_placed = []
            for grp in sorted(self.group_standings.keys()):
                standings = self.group_standings[grp]
                top_teams.append(standings[0]["team"])
                top_teams.append(standings[1]["team"])
                if len(standings) > 2:
                    third_placed.append((grp, standings[2]))

            third_placed.sort(key=lambda x: x[1]["pts"], reverse=True)
            best_third = [t[1]["team"] for t in third_placed[:8]]

            all_qualifiers = top_teams + best_third
            matchups = [
                (all_qualifiers[i], all_qualifiers[len(all_qualifiers) - 1 - i])
                for i in range(len(all_qualifiers) // 2)
            ]

        round_names = ["round_of_32", "round_of_16", "quarter_final", "semi_final", "final"]
        current = matchups
        for round_name in round_names:
            if not current:
                break
            winners = []
            for home, away in current:
                fix_date = self._find_date_for_round(round_name, home, away)
                winner = self._get_knockout_winner(home, away, fix_date)
                winners.append(winner)
                self.knockout_results[f"{round_name}:{home}v{away}"] = winner
            current = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]

            if round_name == "final" and len(winners) == 1:
                self.champion = winners[0]

        return self.knockout_results

    def _find_date_for_round(self, round_name: str, home: str, away: str) -> str:
        for fix in WC_2026_FIXTURES:
            if fix["stage"] == round_name:
                if (fix["home"] == home and fix["away"] == away) or \
                   (fix["home"] == away and fix["away"] == home):
                    return fix["date"]
        return "2026-07-19"

    def run_monte_carlo(self, n_simulations: int = 1000) -> dict:
        champion_wins = defaultdict(int)
        for _ in range(n_simulations):
            self.predictor.ensemble.reset()
            self.simulate_group_stage()
            self.simulate_knockout()
            if self.champion:
                champion_wins[self.champion] += 1
        return {
            "champion_probs": {
                team: count / n_simulations
                for team, count in sorted(
                    champion_wins.items(), key=lambda x: x[1], reverse=True
                )[:10]
            },
            "n_simulations": n_simulations,
        }
