import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.features.feature_pipeline import FEATURE_NAMES


def test_feature_names_count():
    assert len(FEATURE_NAMES) == 45


def test_feature_names_unique():
    assert len(set(FEATURE_NAMES)) == len(FEATURE_NAMES)


def test_feature_names_content():
    required = ["home_fifa_rank", "away_fifa_rank", "rank_diff",
                 "home_form_points", "away_form_points",
                 "h2h_team1_wins", "h2h_team2_wins",
                 "home_injury_impact", "away_injury_impact",
                 "manager_home_win_rate", "manager_away_win_rate",
                 "home_fan_confidence", "away_fan_confidence",
                 "home_rest_days", "away_rest_days"]
    for feat in required:
        assert feat in FEATURE_NAMES, f"Missing feature: {feat}"
