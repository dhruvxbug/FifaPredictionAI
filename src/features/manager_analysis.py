from src.data_collection.squad_data import SquadDataCollector


class ManagerAnalyzer:
    def __init__(self):
        self.squad = SquadDataCollector()

    def compute_all(self, team: str) -> dict:
        data = self.squad.get_team_data(team)
        mgr = data.get("manager", {})
        if not mgr:
            return self._default()

        return {
            "manager_win_rate": mgr.get("win_rate", 0.4),
            "manager_experience_years": mgr.get("experience_years", 3),
            "manager_tournament_exp": mgr.get("tournament_experience", 0),
            "manager_tenure_days": mgr.get("tenure_days", 0),
        }

    def _default(self) -> dict:
        return {
            "manager_win_rate": 0.4,
            "manager_experience_years": 3,
            "manager_tournament_exp": 0,
            "manager_tenure_days": 0,
        }
