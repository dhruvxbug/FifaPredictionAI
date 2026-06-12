import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from src.betting.kelly_criterion import KellyCriterion
from src.betting.bet_selector import BetSelector
from src.betting.bankroll import Bankroll


def test_kelly():
    kelly = KellyCriterion(fraction=1.0)
    stake = kelly.compute_stake(0.6, 2.0, 1000)
    assert stake > 0
    stake2 = kelly.compute_stake(0.3, 2.0, 1000)
    assert stake2 == 0


def test_kelly_fractional():
    kelly = KellyCriterion(fraction=0.25)
    full = KellyCriterion(fraction=1.0)
    stake_partial = kelly.compute_stake(0.6, 2.0, 1000)
    stake_full = full.compute_stake(0.6, 2.0, 1000)
    assert stake_partial < stake_full


def test_bet_selector_high_confidence():
    selector = BetSelector()
    proba = np.array([0.85, 0.10, 0.05])
    result = selector.evaluate(proba, 1.5, 4.0, 6.0, 1000)
    assert result["should_bet"]
    assert result["predicted_outcome"] == "HOME"
    assert result["confidence"] > 0.7


def test_bet_selector_low_confidence():
    selector = BetSelector()
    proba = np.array([0.50, 0.25, 0.25])
    result = selector.evaluate(proba, 2.0, 3.5, 3.5, 1000)
    assert not result["should_bet"]


def test_bankroll_place_bet():
    bankroll = Bankroll(1000)
    bet = bankroll.place_bet(100, 2.0, "match1", "HOME", 0.8)
    assert bet["stake"] == 100
    assert bankroll.balance == 900
    assert bankroll.total_bets == 1


def test_bankroll_settle_win():
    bankroll = Bankroll(1000)
    bankroll.place_bet(100, 2.0, "match1", "HOME", 0.8)
    settled = bankroll.settle_bet("match1", "HOME")
    assert settled["pnl"] == 100
    assert bankroll.balance == 1100
    assert bankroll.won_bets == 1


def test_bankroll_settle_loss():
    bankroll = Bankroll(1000)
    bankroll.place_bet(100, 2.0, "match1", "HOME", 0.8)
    settled = bankroll.settle_bet("match1", "AWAY")
    assert settled["pnl"] == -100
    assert bankroll.balance == 900
    assert bankroll.lost_bets == 1


def test_bankroll_summary():
    bankroll = Bankroll(1000)
    bankroll.place_bet(100, 2.0, "m1", "HOME", 0.8)
    bankroll.settle_bet("m1", "HOME")
    summary = bankroll.get_summary()
    assert summary["total_bets"] == 1
    assert summary["won_bets"] == 1
    assert summary["profit_loss"] == 100
