import re
from typing import Optional


class SentimentAnalyzer:
    def __init__(self):
        self.exa_results: dict[str, dict] = {}

    def set_exa_results(self, team: str, exa_data: dict):
        self.exa_results[team] = exa_data

    def compute_all(self, team: str) -> dict:
        data = self.exa_results.get(team, {})
        if not data:
            return self._default()

        highlights = self._extract_highlights(data)
        confidence = self._estimate_confidence(highlights, team)
        return {
            "fan_confidence_index": confidence,
            "positive_mentions": highlights.get("positive", 0),
            "negative_mentions": highlights.get("negative", 0),
            "sentiment_summary": highlights.get("summary", ""),
        }

    def _extract_highlights(self, data: dict) -> dict:
        result = {"positive": 0, "negative": 0, "summary": ""}
        pos_words = {"confident", "strong", "win", "favorite", "impressive",
                     "brilliant", "excellent", "form", "quality", "depth"}
        neg_words = {"injury", "struggling", "weak", "crisis", "poor",
                     "worried", "doubt", "unlikely", "suspend", "ban"}

        for item in data.get("results", []):
            text = f"{item.get('title', '')} {' '.join(item.get('highlights', []))}"
            text_lower = text.lower()
            result["positive"] += sum(1 for w in pos_words if w in text_lower)
            result["negative"] += sum(1 for w in neg_words if w in text_lower)

        result["summary"] = data.get("summary", "")
        return result

    def _estimate_confidence(self, highlights: dict, team: str) -> float:
        total = highlights["positive"] + highlights["negative"] + 1
        ratio = (highlights["positive"] + 1) / total
        return round(ratio, 3)

    def _default(self) -> dict:
        return {
            "fan_confidence_index": 0.5,
            "positive_mentions": 0,
            "negative_mentions": 0,
            "sentiment_summary": "",
        }
