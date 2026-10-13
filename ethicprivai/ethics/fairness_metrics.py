"""
Algorithmic Fairness & Ethical Decision-Making Metrics
=======================================================
Implements comprehensive group fairness & individual fairness audits:
- Disparate Impact (80% / Four-Fifths Rule)
- Demographic Parity
- Equalized Odds
- Equal Opportunity
- Predictive Parity
- Theil Index (Individual Fairness / Inequality Metric)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, Union


class FairnessAudit:
    """
    Audits binary predictions for algorithmic bias across protected attributes.
    """

    @staticmethod
    def audit(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        protected_attr: np.ndarray,
        privileged_val: Any = 1,
        unprivileged_val: Any = 0
    ) -> Dict[str, Any]:
        """
        Calculates group fairness metrics given ground truth, predictions, and sensitive group labels.
        """
        y_t = np.asarray(y_true, dtype=int)
        y_p = np.asarray(y_pred, dtype=int)
        prot = np.asarray(protected_attr)

        # Masks
        priv_mask = (prot == privileged_val)
        unpriv_mask = (prot == unprivileged_val)

        n_priv = int(np.sum(priv_mask))
        n_unpriv = int(np.sum(unpriv_mask))

        if n_priv == 0 or n_unpriv == 0:
            return {"error": "Both privileged and unprivileged groups must have samples."}

        # Selection rates: P(Y_hat = 1 | Group)
        sel_priv = float(np.mean(y_p[priv_mask]))
        sel_unpriv = float(np.mean(y_p[unpriv_mask]))

        # Disparate Impact Ratio = P(Y_hat=1 | unpriv) / P(Y_hat=1 | priv)
        disparate_impact = (sel_unpriv / sel_priv) if sel_priv > 1e-6 else 1.0

        # Demographic Parity Difference = |P(Y_hat=1 | unpriv) - P(Y_hat=1 | priv)|
        demographic_parity_diff = abs(sel_unpriv - sel_priv)

        # True Positive Rate (Recall) per group: TPR = TP / (TP + FN) = P(Y_hat=1 | Y=1, Group)
        pos_priv = (y_t[priv_mask] == 1)
        pos_unpriv = (y_t[unpriv_mask] == 1)

        tpr_priv = float(np.mean(y_p[priv_mask][pos_priv])) if np.sum(pos_priv) > 0 else 0.0
        tpr_unpriv = float(np.mean(y_p[unpriv_mask][pos_unpriv])) if np.sum(pos_unpriv) > 0 else 0.0
        equal_opportunity_diff = abs(tpr_unpriv - tpr_priv)

        # False Positive Rate per group: FPR = FP / (FP + TN) = P(Y_hat=1 | Y=0, Group)
        neg_priv = (y_t[priv_mask] == 0)
        neg_unpriv = (y_t[unpriv_mask] == 0)

        fpr_priv = float(np.mean(y_p[priv_mask][neg_priv])) if np.sum(neg_priv) > 0 else 0.0
        fpr_unpriv = float(np.mean(y_p[unpriv_mask][neg_unpriv])) if np.sum(neg_unpriv) > 0 else 0.0
        fpr_diff = abs(fpr_unpriv - fpr_priv)

        # Equalized Odds Difference = max(TPR_diff, FPR_diff)
        equalized_odds_diff = max(equal_opportunity_diff, fpr_diff)

        # Positive Predictive Value (Precision) per group
        pred_pos_priv = (y_p[priv_mask] == 1)
        pred_pos_unpriv = (y_p[unpriv_mask] == 1)

        ppv_priv = float(np.mean(y_t[priv_mask][pred_pos_priv])) if np.sum(pred_pos_priv) > 0 else 0.0
        ppv_unpriv = float(np.mean(y_t[unpriv_mask][pred_pos_unpriv])) if np.sum(pred_pos_unpriv) > 0 else 0.0
        predictive_parity_diff = abs(ppv_unpriv - ppv_priv)

        # Theil Index (Individual Fairness / Inequality): measures dispersion of benefit
        # b_i = y_pred_i - y_true_i + 1
        benefits = (y_p - y_t + 1.0)
        mean_b = float(np.mean(benefits))
        if mean_b > 1e-6:
            ratios = benefits / mean_b
            theil_index = float(np.mean([r * np.log(max(1e-6, r)) for r in ratios]))
        else:
            theil_index = 0.0

        # Compliance with EEOC 80% Four-Fifths Rule
        # 0.8 <= Disparate Impact <= 1.25 is legally compliant
        four_fifths_compliant = bool(0.80 <= disparate_impact <= 1.25)

        # Ethical Fairness Score (0 to 100):
        # 100 when Disparate Impact is 1.0 and Demographic Parity diff is 0
        di_penalty = min(1.0, abs(1.0 - disparate_impact))
        fairness_score = max(0.0, 100.0 * (1.0 - 0.5 * di_penalty - 0.5 * demographic_parity_diff))

        return {
            "disparate_impact_ratio": round(disparate_impact, 3),
            "four_fifths_compliant": four_fifths_compliant,
            "demographic_parity_diff": round(demographic_parity_diff, 4),
            "equal_opportunity_diff": round(equal_opportunity_diff, 4),
            "equalized_odds_diff": round(equalized_odds_diff, 4),
            "predictive_parity_diff": round(predictive_parity_diff, 4),
            "theil_index_individual_fairness": round(theil_index, 4),
            "fairness_score_pct": round(fairness_score, 1),
            "group_breakdown": {
                "privileged": {
                    "count": n_priv,
                    "selection_rate": round(sel_priv, 4),
                    "true_positive_rate": round(tpr_priv, 4),
                    "false_positive_rate": round(fpr_priv, 4),
                    "precision": round(ppv_priv, 4)
                },
                "unprivileged": {
                    "count": n_unpriv,
                    "selection_rate": round(sel_unpriv, 4),
                    "true_positive_rate": round(tpr_unpriv, 4),
                    "false_positive_rate": round(fpr_unpriv, 4),
                    "precision": round(ppv_unpriv, 4)
                }
            }
        }
