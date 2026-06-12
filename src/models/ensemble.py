import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

from src.models.elo_model import EloModel
from src.models.poisson_model import DixonColesModel
from src.models.xgboost_model import XGBoostModel
from src.utils.config import config


OUTCOME_HOME = 0
OUTCOME_DRAW = 1
OUTCOME_AWAY = 2


class EnsemblePredictor:
    def __init__(self):
        self.elo = EloModel()
        self.poisson = DixonColesModel()
        self.xgb = XGBoostModel()
        self.meta_model = None
        self.use_calibration = config["models"]["ensemble"]["use_calibration"]
        self.calibration_method = config["models"]["ensemble"]["calibration_method"]
        self._fitted = False
        self._model_weights = np.array([0.2, 0.2, 0.6])

    def fit_base_models(self, df, feature_df=None):
        """Train base models on historical data."""
        print("Training Elo model...")
        self.elo.train_on_historical(df)

        print("Training Dixon-Coles model...")
        ref_date = df["date"].max() if "date" in df.columns else None
        self.poisson.fit(df, ref_date)

        if feature_df is not None and not feature_df.empty:
            print("Training XGBoost model...")
            feature_cols = [c for c in feature_df.columns if c != "target"]
            y = feature_df["target"].values
            split = int(len(feature_df) * 0.8)
            X_train = feature_df[feature_cols].iloc[:split].values
            y_train = y[:split]
            X_val = feature_df[feature_cols].iloc[split:].values
            y_val = y[split:]
            self.xgb.fit(X_train, y_train, X_val, y_val)
        else:
            print("No feature data for XGBoost. Will use Elo + Poisson only.")

        self._fitted = True

    def predict_base_probas(self, home: str, away: str, features: np.ndarray = None) -> np.ndarray:
        elo_proba = self.elo.predict_proba(home, away)
        poi_proba = self.poisson.predict_proba(home, away)
        if features is not None and self.xgb._fitted:
            xgb_proba = self.xgb.predict_proba(features)[0]
        else:
            xgb_proba = np.array([0.4, 0.2, 0.4])
        return np.vstack([elo_proba, poi_proba, xgb_proba])

    def predict_proba(self, home: str, away: str, features: np.ndarray = None) -> np.ndarray:
        base = self.predict_base_probas(home, away, features)
        weighted = np.dot(self._model_weights, base)
        weighted = weighted / weighted.sum()

        if self.meta_model is not None:
            meta_input = base.flatten().reshape(1, -1)
            calibrated = self.meta_model.predict_proba(meta_input)[0]
            return calibrated / calibrated.sum()

        return weighted

    def predict(self, home: str, away: str, features: np.ndarray = None) -> tuple:
        proba = self.predict_proba(home, away, features)
        outcome = int(np.argmax(proba))
        confidence = float(proba[outcome])
        return outcome, confidence, proba

    def calibrate_ensemble(self, X_meta: np.ndarray, y_meta: np.ndarray):
        """Train a calibration layer (Logistic Regression) on meta features."""
        lr = LogisticRegression(multi_class="multinomial", max_iter=1000)
        calibrated = CalibratedClassifierCV(lr, method=self.calibration_method, cv=5)
        calibrated.fit(X_meta, y_meta)
        self.meta_model = calibrated

    def set_model_weights(self, w_elo: float, w_poisson: float, w_xgb: float):
        self._model_weights = np.array([w_elo, w_poisson, w_xgb])

    def get_feature_importance(self) -> dict:
        return self.xgb.feature_importance()

    def reset(self):
        self.elo.reset()
        self.poisson.reset()
        self.xgb.reset()
        self.meta_model = None
        self._fitted = False
