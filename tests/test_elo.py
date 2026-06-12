import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from src.models.elo_model import EloModel


def test_initial_rating():
    model = EloModel()
    assert model.get_rating("Brazil") == 1500
    assert model.get_rating("Unknown") == 1500


def test_expected_score():
    model = EloModel()
    e = model.expected_score(1500, 1500)
    assert abs(e - 0.5) < 0.01
    higher = model.expected_score(1700, 1500)
    assert higher > 0.5
    lower = model.expected_score(1500, 1700)
    assert lower < 0.5


def test_update():
    model = EloModel()
    r_before = model.get_rating("Brazil")
    model.update("Brazil", "Argentina", 3, 0)
    r_after = model.get_rating("Brazil")
    assert r_after > r_before


def test_predict_proba():
    model = EloModel()
    model.update("Brazil", "Argentina", 2, 0)
    model.update("France", "England", 1, 1)
    proba = model.predict_proba("Brazil", "France")
    assert len(proba) == 3
    assert abs(proba.sum() - 1.0) < 0.01
    assert proba[0] >= 0


def test_reset():
    model = EloModel()
    model.update("Brazil", "Argentina", 1, 0)
    model.reset()
    assert model.get_rating("Brazil") == 1500
    assert len(model.ratings) == 0


def test_goal_diff_weight():
    model = EloModel()
    w1 = model.goal_diff_weight(1, 0)
    w2 = model.goal_diff_weight(5, 0)
    assert w2 > w1
    assert w1 > 0
