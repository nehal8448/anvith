"""
Bias Mitigation Engine for Ethical AI
======================================
Implements pre-processing fair reweighing (Kamiran & Calders 2012)
and post-processing threshold tuning to mitigate demographic bias.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional


class FairReweighing:
    """
    Kamiran & Calders Fair Reweighing Pre-processing Algorithm.
    Computes sample weights W(S, Y) = (P(S) * P(Y)) / P(S, Y)
    to neutralize statistical dependence between protected attributes and outcomes
    without modifying underlying feature values.
    """

    @staticmethod
    def compute_weights(
        protected_attr: np.ndarray,
        labels: np.ndarray,
        privileged_val: Any = 1,
        unprivileged_val: Any = 0
    ) -> np.ndarray:
        """
        Returns array of sample weights W matching the size of protected_attr and labels.
        """
        prot = np.asarray(protected_attr)
        y = np.asarray(labels, dtype=int)
        n = len(prot)

        priv_mask = (prot == privileged_val)
        unpriv_mask = (prot == unprivileged_val)
        pos_mask = (y == 1)
        neg_mask = (y == 0)

        # Probabilities
        p_priv = np.mean(priv_mask)
        p_unpriv = np.mean(unpriv_mask)
        p_pos = np.mean(pos_mask)
        p_neg = np.mean(neg_mask)

        # Joint probabilities
        p_priv_pos = np.mean(priv_mask & pos_mask)
        p_priv_neg = np.mean(priv_mask & neg_mask)
        p_unpriv_pos = np.mean(unpriv_mask & pos_mask)
        p_unpriv_neg = np.mean(unpriv_mask & neg_mask)

        # Theoretical weights
        w_priv_pos = (p_priv * p_pos) / max(1e-7, p_priv_pos)
        w_priv_neg = (p_priv * p_neg) / max(1e-7, p_priv_neg)
        w_unpriv_pos = (p_unpriv * p_pos) / max(1e-7, p_unpriv_pos)
        w_unpriv_neg = (p_unpriv * p_neg) / max(1e-7, p_unpriv_neg)

        weights = np.ones(n, dtype=float)
        weights[priv_mask & pos_mask] = w_priv_pos
        weights[priv_mask & neg_mask] = w_priv_neg
        weights[unpriv_mask & pos_mask] = w_unpriv_pos
        weights[unpriv_mask & neg_mask] = w_unpriv_neg

        # Normalize weights so mean is 1.0
        weights = weights / np.mean(weights)
        return weights


class FairThresholdOptimizer:
    """
    Post-processing Equalized Odds / Demographic Parity threshold optimizer.
    Finds separate decision thresholds (tau_priv, tau_unpriv) that minimize
    fairness disparity while maximizing utility.
    """

    @staticmethod
    def optimize_thresholds(
        y_true: np.ndarray,
        y_proba: np.ndarray,
        protected_attr: np.ndarray,
        privileged_val: Any = 1,
        unprivileged_val: Any = 0,
        objective: str = "equalized_odds"
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Grid search for optimal (tau_priv, tau_unpriv) thresholds.
        """
        y_t = np.asarray(y_true, dtype=int)
        y_p = np.asarray(y_proba, dtype=float)
        prot = np.asarray(protected_attr)

        priv_mask = (prot == privileged_val)
        unpriv_mask = (prot == unprivileged_val)

        best_score = float("inf")
        best_tau_priv = 0.5
        best_tau_unpriv = 0.5

        threshold_candidates = np.linspace(0.2, 0.8, 25)

        for tau_priv in threshold_candidates:
            for tau_unpriv in threshold_candidates:
                # Generate predictions
                preds = np.zeros(len(y_t), dtype=int)
                preds[priv_mask] = (y_p[priv_mask] >= tau_priv).astype(int)
                preds[unpriv_mask] = (y_p[unpriv_mask] >= tau_unpriv).astype(int)

                # Accuracy loss penalty
                acc = np.mean(preds == y_t)
                acc_loss = 1.0 - acc

                # Selection rates
                sel_priv = np.mean(preds[priv_mask]) if np.sum(priv_mask) > 0 else 0
                sel_unpriv = np.mean(preds[unpriv_mask]) if np.sum(unpriv_mask) > 0 else 0
                dp_diff = abs(sel_unpriv - sel_priv)

                # TPR rates
                pos_priv = (y_t[priv_mask] == 1)
                pos_unpriv = (y_t[unpriv_mask] == 1)
                tpr_priv = np.mean(preds[priv_mask][pos_priv]) if np.sum(pos_priv) > 0 else 0
                tpr_unpriv = np.mean(preds[unpriv_mask][pos_unpriv]) if np.sum(pos_unpriv) > 0 else 0
                eo_diff = abs(tpr_unpriv - tpr_priv)

                fairness_penalty = eo_diff if objective == "equalized_odds" else dp_diff
                total_loss = fairness_penalty * 0.7 + acc_loss * 0.3

                if total_loss < best_score:
                    best_score = total_loss
                    best_tau_priv = float(tau_priv)
                    best_tau_unpriv = float(tau_unpriv)

        return best_tau_priv, best_tau_unpriv, {
            "tau_privileged": round(best_tau_priv, 3),
            "tau_unprivileged": round(best_tau_unpriv, 3),
            "objective": objective
        }
