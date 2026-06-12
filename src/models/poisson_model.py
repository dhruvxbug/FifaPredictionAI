import numpy as np
import pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize
from datetime import datetime, timedelta

from src.utils.config import config


class DixonColesModel:
    def __init__(self):
        self.half_life_days = config["models"]["poisson"]["time_decay_half_life_days"]
        self.low_score_correction = config["models"]["poisson"]["low_score_correction"]
        self.max_iter = config["models"]["poisson"].get("max_iter", 500)
        self.attack: dict[str, float] = {}
        self.defense: dict[str, float] = {}
        self.home_advantage: float = 0.0
        self.rho: float = 0.0
        self._fitted = False

    def _time_weight(self, match_date: str, ref_date: str = None) -> float:
        if ref_date is None:
            ref_date = datetime.now().strftime("%Y-%m-%d")
        md = datetime.strptime(match_date, "%Y-%m-%d")
        rd = datetime.strptime(ref_date, "%Y-%m-%d")
        days = (rd - md).days
        if days <= 0:
            return 1.0
        return 2.0 ** (-days / self.half_life_days)

    def fit(self, df: pd.DataFrame, ref_date: str = None):
        valid = df.dropna(subset=["home_score", "away_score"])
        valid = valid[(valid["home_score"] >= 0) & (valid["away_score"] >= 0)]
        valid = valid.reset_index(drop=True)
        if len(valid) < 10:
            return

        teams = sorted(set(valid["home_team"].unique()) | set(valid["away_team"].unique()))
        n_teams = len(teams)
        team_to_idx = {t: i for i, t in enumerate(teams)}

        home_idx = np.array([team_to_idx[t] for t in valid["home_team"]])
        away_idx = np.array([team_to_idx[t] for t in valid["away_team"]])
        home_goals = valid["home_score"].values.astype(int)
        away_goals = valid["away_score"].values.astype(int)
        time_weights = np.array([self._time_weight(d, ref_date) for d in valid["date"]])

        def neg_log_likelihood(params):
            attack_p = params[:n_teams]
            defense_p = params[n_teams : 2 * n_teams]
            home_p = params[2 * n_teams]
            rho_p = params[2 * n_teams + 1] if self.low_score_correction else 0.0

            lam = np.exp(attack_p[home_idx] + defense_p[away_idx] + home_p)
            mu = np.exp(attack_p[away_idx] + defense_p[home_idx])

            log_probs = np.zeros(len(valid))

            if self.low_score_correction:
                tau = np.ones(len(valid))
                z0 = (home_goals == 0) & (away_goals == 0)
                z1 = (home_goals == 0) & (away_goals == 1)
                z2 = (home_goals == 1) & (away_goals == 0)
                z3 = (home_goals == 1) & (away_goals == 1)
                tau[z0] = np.maximum(1 - rho_p * lam[z0] * mu[z0], 1e-10)
                tau[z1] = np.maximum(1 + rho_p * lam[z1], 1e-10)
                tau[z2] = np.maximum(1 + rho_p * mu[z2], 1e-10)
                tau[z3] = np.maximum(1 - rho_p, 1e-10)
                probs = tau * poisson.pmf(home_goals, lam) * poisson.pmf(away_goals, mu)
            else:
                probs = poisson.pmf(home_goals, lam) * poisson.pmf(away_goals, mu)

            mask = probs > 0
            log_probs[mask] = time_weights[mask] * np.log(probs[mask])
            return -np.sum(log_probs)

        initial = np.zeros(2 * n_teams + 2)
        initial[2 * n_teams] = 0.2

        bounds = [(None, None)] * (2 * n_teams) + [(0.0, None), (-1.0, 1.0)]
        if not self.low_score_correction:
            bounds = bounds[:-1]
            initial = initial[:-1]

        result = minimize(
            neg_log_likelihood, initial, method="L-BFGS-B",
            bounds=bounds, options={"maxiter": self.max_iter}
        )

        for i, team in enumerate(teams):
            self.attack[team] = result.x[i]
            self.defense[team] = result.x[n_teams + i]

        self.home_advantage = result.x[2 * n_teams]
        if self.low_score_correction:
            self.rho = result.x[2 * n_teams + 1]

        self._teams = teams
        self._fitted = True

    def predict_proba(self, home: str, away: str, max_goals: int = 10) -> np.ndarray:
        if not self._fitted:
            return np.array([0.4, 0.2, 0.4])

        home_att = self.attack.get(home, 0.0)
        home_def = self.defense.get(home, 0.0)
        away_att = self.attack.get(away, 0.0)
        away_def = self.defense.get(away, 0.0)

        lam = np.exp(home_att + away_def + self.home_advantage)
        mu = np.exp(away_att + home_def)

        prob_home = 0.0
        prob_draw = 0.0
        prob_away = 0.0

        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                if self.low_score_correction:
                    if i == 0 and j == 0:
                        tau = 1 - self.rho * lam * mu
                    elif i == 0 and j == 1:
                        tau = 1 + self.rho * lam
                    elif i == 1 and j == 0:
                        tau = 1 + self.rho * mu
                    elif i == 1 and j == 1:
                        tau = 1 - self.rho
                    else:
                        tau = 1.0
                    if tau <= 0:
                        tau = 1e-10
                    prob = tau * poisson.pmf(i, lam) * poisson.pmf(j, mu)
                else:
                    prob = poisson.pmf(i, lam) * poisson.pmf(j, mu)

                if i > j:
                    prob_home += prob
                elif i == j:
                    prob_draw += prob
                else:
                    prob_away += prob

        total = prob_home + prob_draw + prob_away
        return np.array([prob_home / total, prob_draw / total, prob_away / total])

    def reset(self):
        self.attack = {}
        self.defense = {}
        self.home_advantage = 0.0
        self.rho = 0.0
        self._fitted = False
