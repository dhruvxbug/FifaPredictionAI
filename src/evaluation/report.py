import json
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

from src.utils.config import config


class ReportGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or config["data"]["reports_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_backtest_report(self, tracker, backtest_results: dict):
        stats = tracker.get_stats()
        predictions = tracker.get_all_predictions()
        df = pd.DataFrame(predictions)

        report_path = self.output_dir / f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_path.mkdir(parents=True, exist_ok=True)

        self._plot_accuracy_by_confidence(df, report_path)
        self._plot_confusion_matrix(df, report_path)
        self._plot_cumulative_pnl(df, report_path)
        self._plot_win_rate_over_time(df, report_path)
        self._plot_feature_importance(backtest_results.get("feature_importance", {}), report_path)

        report_md = self._generate_markdown(stats, backtest_results, df)
        with open(report_path / "report.md", "w") as f:
            f.write(report_md)

        with open(report_path / "summary.json", "w") as f:
            json.dump({
                "stats": stats,
                "results": backtest_results,
            }, f, indent=2, cls=NpEncoder)

        print(f"Report generated at {report_path}")
        return report_path

    def _plot_accuracy_by_confidence(self, df: pd.DataFrame, output_dir: Path):
        if df.empty or "confidence" not in df.columns:
            return
        bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        labels = ["<50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
        df["conf_bin"] = pd.cut(df["confidence"], bins=bins, labels=labels, right=False)
        df["correct"] = df["predicted_outcome"] == df["actual_result"]

        grouped = df[df["settled"] == 1].groupby("conf_bin", observed=False).agg(
            accuracy=("correct", "mean"),
            count=("correct", "count"),
        ).reset_index()

        if grouped.empty:
            return
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(grouped["conf_bin"], grouped["accuracy"], color="steelblue", alpha=0.8)
        for bar, count in zip(bars, grouped["count"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"n={count}", ha="center", fontsize=9)
        ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.5, label="Random (50%)")
        ax.set_xlabel("Confidence Bucket")
        ax.set_ylabel("Accuracy")
        ax.set_title("Accuracy by Confidence Bucket")
        ax.set_ylim(0, 1)
        ax.legend()
        plt.tight_layout()
        fig.savefig(output_dir / "accuracy_by_confidence.png", dpi=150)
        plt.close(fig)

    def _plot_confusion_matrix(self, df: pd.DataFrame, output_dir: Path):
        settled = df[df["settled"] == 1]
        if settled.empty:
            return
        labels = ["Home Win", "Draw", "Away Win"]
        cm = np.zeros((3, 3), dtype=int)
        for _, row in settled.iterrows():
            true_idx = labels.index(row["actual_result"]) if row["actual_result"] in labels else -1
            pred_idx = row["predicted_index"]
            if true_idx >= 0 and pred_idx >= 0:
                cm[true_idx, pred_idx] += 1

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=labels, yticklabels=labels, ax=ax)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title("Confusion Matrix")
        plt.tight_layout()
        fig.savefig(output_dir / "confusion_matrix.png", dpi=150)
        plt.close(fig)

    def _plot_cumulative_pnl(self, df: pd.DataFrame, output_dir: Path):
        bets = df[df["bet_placed"] == 1].sort_values("date")
        if bets.empty:
            return
        bets["cumulative_pnl"] = bets["pnl"].cumsum()
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(range(len(bets)), bets["cumulative_pnl"].values,
                color="green", linewidth=2)
        ax.fill_between(range(len(bets)), 0, bets["cumulative_pnl"].values,
                        alpha=0.2, color="green" if bets["cumulative_pnl"].iloc[-1] >= 0 else "red")
        ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)
        ax.set_xlabel("Bet Number")
        ax.set_ylabel("Cumulative P&L ($)")
        ax.set_title("Cumulative Profit/Loss Over Time")
        plt.tight_layout()
        fig.savefig(output_dir / "cumulative_pnl.png", dpi=150)
        plt.close(fig)

    def _plot_win_rate_over_time(self, df: pd.DataFrame, output_dir: Path):
        bets = df[df["bet_placed"] == 1].sort_values("date")
        if bets.empty or len(bets) < 10:
            return
        bets["correct"] = (bets["predicted_outcome"] == bets["actual_result"]).astype(int)
        bets["rolling_win_rate"] = bets["correct"].rolling(window=min(20, len(bets))).mean()
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(range(len(bets)), bets["rolling_win_rate"].values * 100,
                color="blue", linewidth=2)
        ax.axhline(y=50, color="red", linestyle="--", alpha=0.5)
        ax.set_xlabel("Bet Number")
        ax.set_ylabel("Rolling Win Rate (%)")
        ax.set_title("Rolling Win Rate (last 20 bets)")
        ax.set_ylim(0, 100)
        plt.tight_layout()
        fig.savefig(output_dir / "win_rate_over_time.png", dpi=150)
        plt.close(fig)

    def _plot_feature_importance(self, importance: dict, output_dir: Path):
        if not importance:
            return
        sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15]
        names, values = zip(*sorted_imp)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(names)), values, color="teal")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.set_xlabel("Importance")
        ax.set_title("Top 15 Feature Importances (XGBoost)")
        ax.invert_yaxis()
        plt.tight_layout()
        fig.savefig(output_dir / "feature_importance.png", dpi=150)
        plt.close(fig)

    def _generate_markdown(self, stats: dict, results: dict, df: pd.DataFrame) -> str:
        lines = [
            "# FIFA Prediction AI — Backtest Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overall Statistics",
            f"| Metric | Value |",
            "|--------|-------|",
            f"| Total Predictions | {stats.get('total_predictions', 0)} |",
            f"| Settled | {stats.get('settled', 0)} |",
            f"| Correct | {stats.get('correct', 0)} |",
            f"| **Accuracy** | **{stats.get('accuracy', 0):.2%}** |",
            f"| Total Bets | {stats.get('total_bets', 0)} |",
            f"| Bets Won | {stats.get('bets_won', 0)} |",
            f"| **Bet Win Rate** | **{stats.get('bet_win_rate', 0):.2%}** |",
            f"| **Total P&L** | **${stats.get('total_pnl', 0):.2f}** |",
            "",
            "## Model Performance",
            f"| Model | Metric | Value |",
            "|-------|--------|-------|",
            f"| Overall | Brier Score | {results.get('brier_score', 'N/A')} |",
            f"| Overall | Log Loss | {results.get('log_loss', 'N/A')} |",
        ]

        if not df.empty and "conf_bin" in df.columns:
            lines.extend([
                "",
                "## Accuracy by Confidence Bucket",
                "| Bucket | Count | Accuracy |",
                "|--------|-------|----------|",
            ])
            bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            labels = ["<50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
            settled = df[df["settled"] == 1]
            for i, low in enumerate(bins[:-1]):
                high = bins[i + 1]
                mask = (settled["confidence"] >= low) & (settled["confidence"] < high)
                subset = settled[mask]
                if subset.empty:
                    continue
                acc = (subset["predicted_outcome"] == subset["actual_result"]).mean()
                lines.append(f"| {labels[i]} | {len(subset)} | {acc:.2%} |")

        lines.extend([
            "",
            "## Charts Generated",
            "- `accuracy_by_confidence.png`",
            "- `confusion_matrix.png`",
            "- `cumulative_pnl.png`",
            "- `win_rate_over_time.png`",
            "- `feature_importance.png`",
        ])
        return "\n".join(lines)
