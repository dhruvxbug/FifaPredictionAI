import json
from pathlib import Path

from src.utils.config import config


class Bankroll:
    def __init__(self, initial: float = None):
        self.initial = initial if initial is not None else config["betting"]["bankroll_initial"]
        self.balance = self.initial
        self.total_bets = 0
        self.won_bets = 0
        self.lost_bets = 0
        self.total_staked = 0.0
        self.total_winnings = 0.0
        self.history: list[dict] = []

    def place_bet(self, stake: float, odds: float, match_id: str,
                  predicted_outcome: str, confidence: float) -> dict:
        if stake > self.balance:
            stake = self.balance
        potential_return = round(stake * odds, 2)
        bet = {
            "match_id": match_id,
            "stake": stake,
            "odds": odds,
            "predicted_outcome": predicted_outcome,
            "confidence": confidence,
            "potential_return": potential_return,
            "actual_outcome": None,
            "pnl": 0.0,
            "settled": False,
        }
        self.history.append(bet)
        self.balance -= stake
        self.total_staked += stake
        self.total_bets += 1
        return bet

    def settle_bet(self, match_id: str, actual_outcome: str) -> dict:
        for bet in reversed(self.history):
            if bet["match_id"] == match_id and not bet["settled"]:
                won = bet["predicted_outcome"] == actual_outcome
                if won:
                    payout = bet["stake"] * bet["odds"]
                    self.balance += payout
                    bet["pnl"] = round(payout - bet["stake"], 2)
                    bet["actual_outcome"] = actual_outcome
                    self.won_bets += 1
                    self.total_winnings += payout
                else:
                    bet["pnl"] = -bet["stake"]
                    bet["actual_outcome"] = actual_outcome
                    self.lost_bets += 1
                bet["settled"] = True
                return bet
        return {}

    def win_rate(self) -> float:
        if self.total_bets == 0:
            return 0.0
        return self.won_bets / self.total_bets

    def roi(self) -> float:
        if self.total_staked == 0:
            return 0.0
        net = (self.total_winnings - self.total_staked)
        return net / self.total_staked

    def profit_loss(self) -> float:
        return self.total_winnings - self.total_staked

    def get_summary(self) -> dict:
        return {
            "initial_bankroll": self.initial,
            "current_balance": round(self.balance, 2),
            "total_bets": self.total_bets,
            "won_bets": self.won_bets,
            "lost_bets": self.lost_bets,
            "win_rate": round(self.win_rate(), 4),
            "total_staked": round(self.total_staked, 2),
            "total_winnings": round(self.total_winnings, 2),
            "profit_loss": round(self.profit_loss(), 2),
            "roi": round(self.roi(), 4),
        }

    def get_bet_history(self) -> list[dict]:
        return self.history
