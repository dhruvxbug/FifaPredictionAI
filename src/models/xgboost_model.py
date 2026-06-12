import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.utils.config import config


class XGBoostModel:
    def __init__(self):
        self.params = config["models"]["xgboost"]
        self.model = None
        self.scaler = StandardScaler()
        self._fitted = False

    def _build_model(self):
        try:
            from xgboost import XGBClassifier
            return XGBClassifier(
                n_estimators=self.params["n_estimators"],
                max_depth=self.params["max_depth"],
                learning_rate=self.params["learning_rate"],
                subsample=self.params["subsample"],
                colsample_bytree=self.params["colsample_bytree"],
                objective=self.params["objective"],
                num_class=self.params["num_class"],
                early_stopping_rounds=self.params["early_stopping_rounds"],
                eval_metric="mlogloss",
                random_state=42,
                n_jobs=-1,
            )
        except ImportError:
            raise ImportError("xgboost not installed. Run: pip install xgboost")

    def fit(self, X: np.ndarray, y: np.ndarray, X_val=None, y_val=None):
        self.model = self._build_model()
        X_scaled = self.scaler.fit_transform(X)

        eval_set = None
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            eval_set = [(X_val_scaled, y_val)]

        self.model.fit(
            X_scaled, y,
            eval_set=eval_set,
            verbose=False,
        )
        self._fitted = True

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted or self.model is None:
            return np.array([[0.4, 0.2, 0.4]])
        X_scaled = self.scaler.transform(X.reshape(1, -1) if X.ndim == 1 else X)
        return self.model.predict_proba(X_scaled)

    def feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importances_
        return {f"f{i}": v for i, v in enumerate(importance)}

    def reset(self):
        self.model = None
        self._fitted = False
