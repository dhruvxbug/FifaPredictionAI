import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = self._load_config()

    def _load_config(self):
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        with open(config_path) as f:
            cfg = yaml.safe_load(f)

        cfg["exa"]["api_key"] = os.getenv("EXA_API_KEY", "")
        cfg["data"]["data_dir"] = Path(
            os.getenv("DATA_DIR", cfg["data"].get("data_dir", "./data"))
        )
        cfg["data"]["reports_dir"] = Path(
            os.getenv("REPORTS_DIR", cfg["data"].get("reports_dir", "./reports"))
        )
        cfg["data"]["db_path"] = Path(
            os.getenv("DB_PATH", cfg["data"].get("db_path", "./data/fifa_predictions.db"))
        )

        return cfg

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        return self._config.get(key, default)


config = Config()
