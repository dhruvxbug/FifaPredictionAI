import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.features.team_strength import TeamStrengthFeatures
from src.features.injury_impact import InjuryImpactAnalyzer
from src.features.manager_analysis import ManagerAnalyzer
from src.features.sentiment import SentimentAnalyzer
from src.features.fatigue import FatigueAnalyzer


def test_team_strength():
    ts = TeamStrengthFeatures()
    result = ts.compute_all("Brazil", "Argentina")
    assert "home_fifa_rank" in result
    assert "rank_diff" in result
    assert "market_value_ratio" in result


def test_injury_impact_default():
    inj = InjuryImpactAnalyzer()
    result = inj.compute_all("Brazil")
    assert result["injury_impact_score"] == 0
    assert result["key_players_missing"] == 0


def test_injury_impact_with_data():
    inj = InjuryImpactAnalyzer()
    inj.set_injury_news("Brazil", [
        {"is_key_player": True, "position": "forward", "severity": 0.95},
        {"is_key_player": True, "position": "goalkeeper", "severity": 0.9},
        {"is_key_player": False, "position": "defender", "severity": 0.5},
    ])
    result = inj.compute_all("Brazil")
    assert result["injury_impact_score"] > 0
    assert result["key_players_missing"] == 2
    assert result["has_major_injuries"]


def test_manager_analysis():
    mgr = ManagerAnalyzer()
    result = mgr.compute_all("Brazil")
    assert "manager_win_rate" in result
    assert "manager_experience_years" in result


def test_sentiment_default():
    sent = SentimentAnalyzer()
    result = sent.compute_all("Brazil")
    assert result["fan_confidence_index"] == 0.5


def test_fatigue():
    fat = FatigueAnalyzer()
    result = fat.compute_all("Brazil", "2026-06-20", "New York", "2026-06-15")
    assert "rest_days" in result
    assert "travel_distance_km" in result
    assert "fatigue_index" in result
    assert result["rest_days"] == 5
