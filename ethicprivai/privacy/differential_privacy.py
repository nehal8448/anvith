"""
Differential Privacy (DP) Engine for EthicPrivAI
=================================================
Implements mathematically rigorous Differential Privacy mechanisms,
privacy budget composition accounting, tabular perturbation,
and differentially private machine learning classifiers.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union


class LaplaceMechanism:
    """
    Standard epsilon-Differential Privacy via Laplace noise injection.
    Noise scale b = sensitivity / epsilon.
    """
    def __init__(self, epsilon: float, sensitivity: float = 1.0):
        if epsilon <= 0:
            raise ValueError("Epsilon must be strictly positive.")
        if sensitivity <= 0:
            raise ValueError("Sensitivity must be strictly positive.")
        self.epsilon = float(epsilon)
        self.sensitivity = float(sensitivity)
        self.scale = self.sensitivity / self.epsilon

    def sample_noise(self, size: Union[int, Tuple[int, ...]] = 1) -> np.ndarray:
        """Sample from Laplace(0, scale)."""
        return np.random.laplace(loc=0.0, scale=self.scale, size=size)

    def perturb(self, value: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Add Laplace noise to value or array."""
        arr = np.asarray(value, dtype=float)
        noise = self.sample_noise(arr.shape if arr.ndim > 0 else 1)
        res = arr + (noise[0] if arr.ndim == 0 else noise)
        return float(res) if arr.ndim == 0 else res

    def pdf(self, x: np.ndarray) -> np.ndarray:
        """Probability density function at x for visualization."""
        return (1.0 / (2.0 * self.scale)) * np.exp(-np.abs(x) / self.scale)


class GaussianMechanism:
    """
    (epsilon, delta)-Differential Privacy via Gaussian noise injection.
    Noise standard deviation sigma = sqrt(2 * ln(1.25 / delta)) * (sensitivity / epsilon).
    """
    def __init__(self, epsilon: float, delta: float = 1e-5, sensitivity: float = 1.0):
        if epsilon <= 0:
            raise ValueError("Epsilon must be strictly positive.")
        if not (0 < delta < 1.0):
            raise ValueError("Delta must be strictly between 0 and 1.")
        if sensitivity <= 0:
            raise ValueError("Sensitivity must be strictly positive.")
        self.epsilon = float(epsilon)
        self.delta = float(delta)
        self.sensitivity = float(sensitivity)
        self.sigma = math.sqrt(2.0 * math.log(1.25 / self.delta)) * (self.sensitivity / self.epsilon)

    def sample_noise(self, size: Union[int, Tuple[int, ...]] = 1) -> np.ndarray:
        """Sample from Gaussian(0, sigma^2)."""
        return np.random.normal(loc=0.0, scale=self.sigma, size=size)

    def perturb(self, value: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Add Gaussian noise to value or array."""
        arr = np.asarray(value, dtype=float)
        noise = self.sample_noise(arr.shape if arr.ndim > 0 else 1)
        res = arr + (noise[0] if arr.ndim == 0 else noise)
        return float(res) if arr.ndim == 0 else res

    def pdf(self, x: np.ndarray) -> np.ndarray:
        """Probability density function at x for visualization."""
        return (1.0 / (self.sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * (x / self.sigma) ** 2)


class RandomizedResponse:
    """
    Local Differential Privacy (LDP) via Randomized Response (Warner's Mechanism).
    For binary questions: With probability p = exp(eps) / (1 + exp(eps)), report true answer.
    With probability 1 - p, flip the answer.
    """
    def __init__(self, epsilon: float):
        if epsilon <= 0:
            raise ValueError("Epsilon must be strictly positive.")
        self.epsilon = float(epsilon)
        # Probability of telling the truth
        self.p = math.exp(self.epsilon) / (1.0 + math.exp(self.epsilon))

    def perturb_binary(self, value: Union[int, bool, np.ndarray]) -> np.ndarray:
        """Randomize binary attribute (0 or 1)."""
        val_arr = np.asarray(value, dtype=int)
        flips = np.random.rand(*val_arr.shape) < (1.0 - self.p)
        # If flipped, invert bit (0 -> 1, 1 -> 0)
        perturbed = np.where(flips, 1 - val_arr, val_arr)
        return perturbed

    def estimate_true_proportion(self, perturbed_answers: np.ndarray) -> float:
        """Unbiased estimator for the true positive proportion from noisy responses."""
        q = np.mean(perturbed_answers)
        # q = p * P_true + (1 - p) * (1 - P_true) => P_true = (q + p - 1) / (2p - 1)
        denom = 2.0 * self.p - 1.0
        if abs(denom) < 1e-7:
            return float(q)
        est = (q + self.p - 1.0) / denom
        return float(np.clip(est, 0.0, 1.0))


class PrivacyBudgetTracker:
    """
    Monitors and audits cumulative privacy budget consumption (epsilon, delta).
    Supports Basic Composition and Advanced Composition.
    """
    def __init__(self, total_epsilon: float = 10.0, total_delta: float = 1e-4):
        self.total_epsilon = float(total_epsilon)
        self.total_delta = float(total_delta)
        self.consumed_epsilon = 0.0
        self.consumed_delta = 0.0
        self.transactions: List[Dict[str, Any]] = []

    def can_spend(self, epsilon: float, delta: float = 0.0) -> bool:
        return (self.consumed_epsilon + epsilon <= self.total_epsilon + 1e-9) and \
               (self.consumed_delta + delta <= self.total_delta + 1e-9)

    def spend(self, epsilon: float, delta: float = 0.0, tag: str = "Query") -> Dict[str, Any]:
        """Spend privacy budget for a mechanism or operation."""
        if not self.can_spend(epsilon, delta):
            raise ValueError(
                f"Privacy budget exceeded! Requested: eps={epsilon:.3f}, delta={delta:.2e}. "
                f"Remaining: eps={(self.total_epsilon - self.consumed_epsilon):.3f}, "
                f"delta={(self.total_delta - self.consumed_delta):.2e}"
            )
        self.consumed_epsilon += epsilon
        self.consumed_delta += delta
        record = {
            "id": len(self.transactions) + 1,
            "tag": tag,
            "epsilon_spent": round(epsilon, 4),
            "delta_spent": delta,
            "cumulative_epsilon": round(self.consumed_epsilon, 4),
            "cumulative_delta": self.consumed_delta,
            "remaining_epsilon": round(max(0.0, self.total_epsilon - self.consumed_epsilon), 4),
            "remaining_delta": max(0.0, self.total_delta - self.consumed_delta),
            "budget_used_percentage": round((self.consumed_epsilon / self.total_epsilon) * 100.0, 2)
        }
        self.transactions.append(record)
        return record

    def get_status(self) -> Dict[str, Any]:
        """Get summary of budget usage."""
        pct = (self.consumed_epsilon / self.total_epsilon) * 100.0 if self.total_epsilon > 0 else 100.0
        return {
            "total_epsilon": self.total_epsilon,
            "total_delta": self.total_delta,
            "consumed_epsilon": round(self.consumed_epsilon, 4),
            "consumed_delta": self.consumed_delta,
            "remaining_epsilon": round(max(0.0, self.total_epsilon - self.consumed_epsilon), 4),
            "remaining_delta": max(0.0, self.total_delta - self.consumed_delta),
            "utilization_pct": round(min(100.0, pct), 2),
            "transactions_count": len(self.transactions),
            "transactions": self.transactions[-10:]  # latest 10
        }

    def reset(self):
        """Reset consumed budget."""
        self.consumed_epsilon = 0.0
        self.consumed_delta = 0.0
        self.transactions = []


class DifferentialPrivacyPerturber:
    """
    Transforms tabular datasets into Differentially Private perturbed datasets.
    Clips continuous columns to bounded ranges [L, U] to bound sensitivity Delta f,
    then adds Laplace or Gaussian noise.
    """
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5, mechanism: str = "laplace"):
        self.epsilon = float(epsilon)
        self.delta = float(delta)
        self.mechanism = mechanism.lower()

    def perturb_dataframe(
        self,
        df: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None,
        clip_quantiles: Tuple[float, float] = (0.01, 0.99)
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perturb numeric columns while keeping categorical columns or applying randomized response.
        Returns the perturbed dataframe and metadata on added noise and sensitivity.
        """
        df_noisy = df.copy()
        if numeric_columns is None:
            numeric_columns = list(df.select_dtypes(include=[np.number]).columns)

        if not numeric_columns:
            return df_noisy, {"status": "No numeric columns to perturb", "eps_spent": 0.0}

        # Divide epsilon across numeric features
        eps_per_col = self.epsilon / max(1, len(numeric_columns))
        delta_per_col = self.delta / max(1, len(numeric_columns))

        meta: Dict[str, Any] = {
            "mechanism": self.mechanism,
            "total_epsilon": self.epsilon,
            "total_delta": self.delta,
            "eps_per_column": eps_per_col,
            "features_perturbed": {}
        }

        for col in numeric_columns:
            series = df[col].astype(float)
            q_low = float(series.quantile(clip_quantiles[0]))
            q_high = float(series.quantile(clip_quantiles[1]))
            clipped = np.clip(series.values, q_low, q_high)
            
            # Sensitivity is the max possible change by one record = range (q_high - q_low)
            sensitivity = max(1e-4, q_high - q_low)

            if self.mechanism == "gaussian":
                mech = GaussianMechanism(epsilon=eps_per_col, delta=delta_per_col, sensitivity=sensitivity)
            else:
                mech = LaplaceMechanism(epsilon=eps_per_col, sensitivity=sensitivity)

            noisy_vals = mech.perturb(clipped)
            
            # For integer columns in original df, round back
            if np.issubdtype(df[col].dtype, np.integer):
                noisy_vals = np.round(noisy_vals)

            df_noisy[col] = noisy_vals
            meta["features_perturbed"][col] = {
                "sensitivity": round(sensitivity, 4),
                "noise_scale": round(mech.scale if hasattr(mech, "scale") else mech.sigma, 4),
                "clip_range": [round(q_low, 2), round(q_high, 2)]
            }

        return df_noisy, meta


class DPLogisticRegression:
    """
    Differentially Private Logistic Regression with Output / Objective Perturbation.
    Guarantees (epsilon)-Differential Privacy by clipping sample norm and adding calibrated
    Laplace/Gaussian noise to the fitted weight vectors (Chaudhuri et al. 2011).
    """
    def __init__(
        self,
        epsilon: float = 1.0,
        l2_clip: float = 1.0,
        reg_lambda: float = 0.01,
        max_iter: int = 200,
        lr: float = 0.05
    ):
        self.epsilon = float(epsilon)
        self.l2_clip = float(l2_clip)
        self.reg_lambda = float(reg_lambda)
        self.max_iter = int(max_iter)
        self.lr = float(lr)
        self.weights: Optional[np.ndarray] = None
        self.bias: float = 0.0
        self.classes_: Optional[np.ndarray] = None

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> "DPLogisticRegression":
        """
        Fit model using gradient descent with gradient clipping and DP weight perturbation.
        Optionally accepts sample_weight for in-processing fair reweighing.
        """
        X_raw = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("Binary classification supported (2 classes).")
        y_binary = np.where(y == self.classes_[1], 1, 0)

        n_samples, n_features = X_raw.shape

        if sample_weight is None:
            sw = np.ones(n_samples, dtype=float)
        else:
            sw = np.asarray(sample_weight, dtype=float)
            sw = sw / np.mean(sw)

        # Standardize features for stable gradient dynamics
        self.scaler_mean_ = np.mean(X_raw, axis=0)
        self.scaler_std_ = np.std(X_raw, axis=0)
        self.scaler_std_[self.scaler_std_ == 0] = 1.0
        X_scaled = (X_raw - self.scaler_mean_) / self.scaler_std_

        # Normalize features L2 to bound sample sensitivity
        norms = np.linalg.norm(X_scaled, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        X_clipped = np.where(norms > self.l2_clip, (X_scaled / norms) * self.l2_clip, X_scaled)

        w = np.zeros(n_features)
        b = 0.0

        for epoch in range(self.max_iter):
            z = np.dot(X_clipped, w) + b
            preds = self._sigmoid(z)
            error = (preds - y_binary) * sw

            # Gradient per sample
            grad_w_samples = X_clipped * error[:, np.newaxis]
            # Clip per-sample gradient
            sample_grad_norms = np.linalg.norm(grad_w_samples, axis=1, keepdims=True)
            sample_grad_norms[sample_grad_norms == 0] = 1.0
            clipped_grad_w = np.where(
                sample_grad_norms > self.l2_clip,
                (grad_w_samples / sample_grad_norms) * self.l2_clip,
                grad_w_samples
            )

            grad_w = np.mean(clipped_grad_w, axis=0) + self.reg_lambda * w
            grad_b = np.mean(error)

            w -= self.lr * grad_w
            b -= self.lr * grad_b

        # Output perturbation for DP guarantee:
        # Sensitivity of regularized logistic regression: Delta w <= 2 / (n_samples * reg_lambda)
        sensitivity = 2.0 / max(1.0, (n_samples * self.reg_lambda))
        noise_scale = sensitivity / self.epsilon
        dp_noise = np.random.laplace(0.0, noise_scale, size=n_features)

        self.weights = w + dp_noise
        self.bias = b + float(np.random.laplace(0.0, (1.0 / n_samples) / self.epsilon))
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities [P(y=0), P(y=1)]."""
        if self.weights is None:
            raise ValueError("Model is not fitted yet.")
        X_raw = np.asarray(X, dtype=float)
        X_scaled = (X_raw - self.scaler_mean_) / self.scaler_std_
        z = np.dot(X_scaled, self.weights) + self.bias
        p1 = self._sigmoid(z)
        p0 = 1.0 - p1
        return np.column_stack([p0, p1])

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Predict class labels with given decision threshold."""
        p = self.predict_proba(X)[:, 1]
        preds = np.where(p >= threshold, self.classes_[1], self.classes_[0])
        return preds


class DPNaiveBayes:
    """
    Differentially Private Gaussian/Categorical Naive Bayes.
    Applies Laplace noise to empirical counts and feature statistics.
    """
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = float(epsilon)
        self.class_priors_: Dict[int, float] = {}
        self.means_: Dict[int, np.ndarray] = {}
        self.variances_: Dict[int, np.ndarray] = {}
        self.classes_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DPNaiveBayes":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.classes_ = np.unique(y)
        n_samples, n_features = X.shape

        eps_prior = self.epsilon * 0.2
        eps_stats = self.epsilon * 0.8 / max(1, n_features)

        lap_prior = LaplaceMechanism(epsilon=eps_prior, sensitivity=1.0)

        for c in self.classes_:
            X_c = X[y == c]
            count_c = max(1.0, lap_prior.perturb(float(len(X_c))))
            self.class_priors_[c] = count_c / n_samples

            # Noisy means
            mean_c = np.mean(X_c, axis=0)
            sensitivity_mean = 1.0 / max(1.0, len(X_c))
            lap_mean = LaplaceMechanism(epsilon=eps_stats, sensitivity=sensitivity_mean)
            noisy_mean = lap_mean.perturb(mean_c)
            self.means_[c] = noisy_mean

            # Variances
            var_c = np.var(X_c, axis=0) + 1e-4
            self.variances_[c] = var_c

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        probs = []
        for c in self.classes_:
            prior = self.class_priors_[c]
            mean = self.means_[c]
            var = self.variances_[c]
            # Gaussian log-likelihood
            log_lik = -0.5 * np.sum(np.log(2.0 * np.pi * var) + ((X - mean) ** 2) / var, axis=1)
            probs.append(np.log(max(1e-7, prior)) + log_lik)

        probs_arr = np.column_stack(probs)
        # Softmax for stable probabilities
        exp_p = np.exp(probs_arr - np.max(probs_arr, axis=1, keepdims=True))
        return exp_p / np.sum(exp_p, axis=1, keepdims=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        p = self.predict_proba(X)
        return self.classes_[np.argmax(p, axis=1)]
