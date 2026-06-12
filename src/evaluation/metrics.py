import numpy as np
import pandas as pd


class EvaluationMetrics:
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.mean(y_true == y_pred))

    @staticmethod
    def brier_score(y_true: np.ndarray, y_proba: np.ndarray) -> float:
        n = len(y_true)
        if n == 0:
            return 0.0
        y_onehot = np.zeros((n, 3))
        y_onehot[np.arange(n), y_true] = 1
        return float(np.mean(np.sum((y_proba - y_onehot) ** 2, axis=1)))

    @staticmethod
    def log_loss(y_true: np.ndarray, y_proba: np.ndarray) -> float:
        n = len(y_true)
        if n == 0:
            return 0.0
        eps = 1e-15
        y_proba = np.clip(y_proba, eps, 1 - eps)
        ll = 0.0
        for i in range(n):
            ll += np.log(y_proba[i, int(y_true[i])])
        return float(-ll / n)

    @staticmethod
    def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        mat = np.zeros((3, 3), dtype=int)
        for t, p in zip(y_true, y_pred):
            mat[int(t), int(p)] += 1
        return mat

    @staticmethod
    def accuracy_by_confidence(y_true: np.ndarray, y_pred: np.ndarray,
                               y_proba: np.ndarray, buckets: list = None) -> dict:
        if buckets is None:
            buckets = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        results = {}
        for i, low in enumerate(buckets[:-1]):
            high = buckets[i + 1]
            confs = np.max(y_proba, axis=1)
            mask = (confs >= low) & (confs < high)
            if mask.sum() == 0:
                continue
            acc = np.mean(y_true[mask] == y_pred[mask])
            results[f"{low:.0%}-{high:.0%}"] = {
                "count": int(mask.sum()),
                "accuracy": round(float(acc), 4),
                "avg_confidence": round(float(np.mean(confs[mask])), 4),
            }
        return results

    @staticmethod
    def betting_metrics(bankroll_history: list[dict]) -> dict:
        if not bankroll_history:
            return {}
        df = pd.DataFrame(bankroll_history)
        return {
            "total_bets": len(df),
            "win_rate": round(float(df["won"].mean()), 4) if "won" in df else 0,
            "total_profit": round(float(df["pnl"].sum()), 2),
            "avg_stake": round(float(df["stake"].mean()), 2),
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
        }

    @staticmethod
    def calibration_curve(y_true: np.ndarray, y_proba: np.ndarray,
                          buckets: list = None) -> list[dict]:
        if buckets is None:
            buckets = np.linspace(0, 1, 11)
        confs = np.max(y_proba, axis=1)
        preds = np.argmax(y_proba, axis=1)
        curve = []
        for i in range(len(buckets) - 1):
            low, high = buckets[i], buckets[i + 1]
            mask = (confs >= low) & (confs < high)
            if mask.sum() == 0:
                continue
            accuracy = np.mean(y_true[mask] == preds[mask])
            curve.append({
                "bucket_low": round(low, 2),
                "bucket_high": round(high, 2),
                "count": int(mask.sum()),
                "mean_predicted": round(float(np.mean(confs[mask])), 4),
                "observed_accuracy": round(float(accuracy), 4),
            })
        return curve
