import hashlib
import json
import time
from pathlib import Path
from src.utils.config import config


class TTLCache:
    def __init__(self, cache_dir: str = None, ttl_hours: int = None):
        self.cache_dir = Path(cache_dir or config["data"]["data_dir"] / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = (ttl_hours or config["data"]["cache_ttl_hours"]) * 3600

    def _key_to_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()[:32]
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str):
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            with open(path) as f:
                entry = json.load(f)
            if time.time() - entry["timestamp"] > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            return entry["data"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def set(self, key: str, data):
        path = self._key_to_path(key)
        entry = {"timestamp": time.time(), "data": data}
        with open(path, "w") as f:
            json.dump(entry, f)

    def invalidate(self, key: str):
        path = self._key_to_path(key)
        path.unlink(missing_ok=True)

    def clear_expired(self):
        now = time.time()
        for path in self.cache_dir.glob("*.json"):
            try:
                with open(path) as f:
                    entry = json.load(f)
                if now - entry["timestamp"] > self.ttl_seconds:
                    path.unlink()
            except (json.JSONDecodeError, KeyError, OSError):
                path.unlink(missing_ok=True)
