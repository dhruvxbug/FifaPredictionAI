import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src.utils.config import config


class PredictionTracker:
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or config["data"]["db_path"])
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match TEXT NOT NULL,
                    date TEXT,
                    home TEXT NOT NULL,
                    away TEXT NOT NULL,
                    predicted_outcome TEXT NOT NULL,
                    predicted_index INTEGER,
                    confidence REAL,
                    prob_home REAL,
                    prob_draw REAL,
                    prob_away REAL,
                    confidence_level TEXT,
                    home_odds REAL,
                    draw_odds REAL,
                    away_odds REAL,
                    bet_placed INTEGER DEFAULT 0,
                    bet_stake REAL DEFAULT 0,
                    bet_odds REAL,
                    bet_outcome TEXT,
                    actual_result TEXT,
                    actual_home_goals INTEGER,
                    actual_away_goals INTEGER,
                    pnl REAL DEFAULT 0,
                    features_snapshot TEXT,
                    model_probas_snapshot TEXT,
                    exa_intel_snapshot TEXT,
                    prediction_timestamp TEXT,
                    settled INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def log_prediction(self, prediction: dict):
        with sqlite3.connect(str(self.db_path)) as conn:
            bet = prediction.get("bet_decision", {})
            prob = prediction.get("probabilities", {})
            conn.execute("""
                INSERT INTO predictions (
                    match, date, home, away,
                    predicted_outcome, predicted_index, confidence,
                    prob_home, prob_draw, prob_away,
                    confidence_level,
                    home_odds, draw_odds, away_odds,
                    bet_placed, bet_stake, bet_odds,
                    features_snapshot, model_probas_snapshot,
                    exa_intel_snapshot, prediction_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction["match"],
                prediction.get("date", ""),
                prediction["home"],
                prediction["away"],
                bet.get("predicted_outcome", ""),
                bet.get("predicted_index", -1),
                prediction.get("confidence", 0.0),
                prob.get("home", 0.0),
                prob.get("draw", 0.0),
                prob.get("away", 0.0),
                prediction.get("confidence_level", ""),
                prediction.get("home_odds"),
                prediction.get("draw_odds"),
                prediction.get("away_odds"),
                1 if bet.get("should_bet") else 0,
                bet.get("stake", 0.0),
                bet.get("odds_used"),
                json.dumps(prediction.get("features", {})),
                json.dumps(prediction.get("model_probas", {})),
                json.dumps(prediction.get("exa_intel", {})),
                datetime.now().isoformat(),
            ))
            conn.commit()

    def record_result(self, match: str, date: str, home_goals: int,
                      away_goals: int, actual_result: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                UPDATE predictions
                SET actual_home_goals = ?,
                    actual_away_goals = ?,
                    actual_result = ?,
                    settled = 1,
                    bet_outcome = CASE
                        WHEN predicted_outcome = ? THEN 1
                        ELSE 0
                    END,
                    pnl = CASE
                        WHEN bet_placed = 1 AND predicted_outcome = ?
                            THEN bet_stake * (bet_odds - 1)
                        WHEN bet_placed = 1 THEN -bet_stake
                        ELSE 0
                    END
                WHERE match = ? AND date = ? AND settled = 0
            """, (
                home_goals, away_goals, actual_result,
                actual_result, actual_result,
                match, date,
            ))
            conn.commit()

    def get_all_predictions(self) -> list[dict]:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM predictions ORDER BY date").fetchall()
            return [dict(r) for r in rows]

    def prediction_exists(self, home: str, away: str, date: str) -> bool:
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT 1 FROM predictions WHERE home = ? AND away = ? AND date = ?",
                (home, away, date),
            ).fetchone()
            return row is not None

    def get_prediction(self, home: str, away: str, date: str) -> dict | None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM predictions WHERE home = ? AND away = ? AND date = ?",
                (home, away, date),
            ).fetchone()
            return dict(row) if row else None

    def get_unsettled(self) -> list[dict]:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM predictions WHERE settled = 0 ORDER BY date"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_bets(self) -> list[dict]:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM predictions WHERE bet_placed = 1 ORDER BY date"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        with sqlite3.connect(str(self.db_path)) as conn:
            total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
            settled = conn.execute("SELECT COUNT(*) FROM predictions WHERE settled = 1").fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM predictions WHERE settled = 1 AND predicted_outcome = actual_result"
            ).fetchone()[0]
            bets = conn.execute("SELECT COUNT(*) FROM predictions WHERE bet_placed = 1").fetchone()[0]
            bets_won = conn.execute(
                "SELECT COUNT(*) FROM predictions WHERE bet_placed = 1 AND predicted_outcome = actual_result"
            ).fetchone()[0]
            total_pnl = conn.execute(
                "SELECT COALESCE(SUM(pnl), 0) FROM predictions"
            ).fetchone()[0]

            return {
                "total_predictions": total,
                "settled": settled,
                "correct": correct,
                "accuracy": round(correct / max(settled, 1), 4),
                "total_bets": bets,
                "bets_won": bets_won,
                "bet_win_rate": round(bets_won / max(bets, 1), 4),
                "total_pnl": round(total_pnl, 2),
            }
