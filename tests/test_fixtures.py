import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.data_collection.fixtures import WC_2026_TEAMS, WC_2026_GROUPS, WC_2026_FIXTURES


def test_teams_count():
    assert len(WC_2026_TEAMS) == 48


def test_groups_count():
    assert len(WC_2026_GROUPS) == 12


def test_group_team_count():
    for group, teams in WC_2026_GROUPS.items():
        assert len(teams) == 4, f"Group {group} has {len(teams)} teams"


def test_fixtures_count():
    group_matches = sum(1 for f in WC_2026_FIXTURES if f["stage"] == "group")
    assert group_matches >= 72


def test_all_teams_in_groups():
    all_group_teams = set()
    for teams in WC_2026_GROUPS.values():
        all_group_teams.update(teams)
    for team in WC_2026_TEAMS:
        assert team in all_group_teams, f"{team} not in any group"
