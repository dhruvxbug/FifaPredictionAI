from typing import Optional


class InjuryImpactAnalyzer:
    POSITION_WEIGHTS = {
        "goalkeeper": 1.0,
        "defender": 0.8,
        "midfielder": 0.7,
        "forward": 0.9,
    }

    def __init__(self):
        self.injury_news: dict[str, list[dict]] = {}

    def set_injury_news(self, team: str, injuries: list[dict]):
        self.injury_news[team] = injuries

    def compute_all(self, team: str) -> dict:
        injuries = self.injury_news.get(team, [])
        if not injuries:
            return self._default()

        total_impact = 0.0
        key_players_missing = 0
        positions_missing = set()

        for inj in injuries:
            is_key = inj.get("is_key_player", False)
            position = inj.get("position", "forward")
            severity = inj.get("severity", 0.5)
            weight = self.POSITION_WEIGHTS.get(position, 0.7)

            impact = weight * severity * (1.5 if is_key else 1.0)
            total_impact += impact

            if is_key:
                key_players_missing += 1
            if severity > 0.7:
                positions_missing.add(position)

        return {
            "injury_impact_score": round(min(total_impact, 5.0), 3),
            "key_players_missing": key_players_missing,
            "positions_affected": len(positions_missing),
            "has_major_injuries": total_impact > 2.0,
        }

    def _default(self) -> dict:
        return {
            "injury_impact_score": 0.0,
            "key_players_missing": 0,
            "positions_affected": 0,
            "has_major_injuries": False,
        }
