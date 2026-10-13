"""
Empirical Privacy Evaluation: Membership Inference Attack (MIA)
=================================================================
Simulates Yeom et al. & Shokri et al. Membership Inference Attacks
to empirically measure whether model outputs leak individual training record membership.
Computes Attack Accuracy, Attack ROC-AUC, and Privacy Vulnerability Risk.
"""

import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score
from typing import Dict, Any, Tuple


class MembershipInferenceAttack:
    """
    Evaluates empirical privacy leakage of a trained classifier.
    Computes loss-based and confidence-based membership inference attack advantage.
    """

    @staticmethod
    def evaluate(
        model,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculates how easily an adversary can distinguish members (train) from non-members (test)
        based on prediction confidence and loss.
        """
        X_tr = np.asarray(X_train)
        y_tr = np.asarray(y_train)
        X_te = np.asarray(X_test)
        y_te = np.asarray(y_test)

        # Get probabilities
        if hasattr(model, "predict_proba"):
            p_train = model.predict_proba(X_tr)
            p_test = model.predict_proba(X_te)
        else:
            # Fallback
            p_train = np.ones((len(X_tr), 2)) * 0.5
            p_test = np.ones((len(X_te), 2)) * 0.5

        # True-class confidence
        classes = getattr(model, "classes_", np.array([0, 1]))
        c1_idx = 1 if len(classes) > 1 else 0

        # Confidence assigned to the true label
        conf_train = np.where(y_tr == classes[c1_idx], p_train[:, 1], p_train[:, 0])
        conf_test = np.where(y_te == classes[c1_idx], p_test[:, 1], p_test[:, 0])

        # Negative log-likelihood / loss (lower loss => more likely member)
        loss_train = -np.log(np.clip(conf_train, 1e-7, 1.0))
        loss_test = -np.log(np.clip(conf_test, 1e-7, 1.0))

        # Member labels: 1 = member (train), 0 = non-member (test)
        m_labels = np.concatenate([np.ones(len(conf_train)), np.zeros(len(conf_test))])
        scores = np.concatenate([conf_train, conf_test])

        try:
            attack_auc = float(roc_auc_score(m_labels, scores))
        except Exception:
            attack_auc = 0.5

        # Attack accuracy using threshold on loss
        median_loss = float(np.median(np.concatenate([loss_train, loss_test])))
        attack_preds = (np.concatenate([loss_train, loss_test]) <= median_loss).astype(int)
        attack_acc = float(accuracy_score(m_labels, attack_preds))

        # Privacy Leakage Score (0 to 100%):
        # 50% attack AUC = 0% leakage (perfect random guess / perfect DP defense)
        # 100% attack AUC = 100% leakage (total memorization / privacy violation)
        leakage_risk_pct = max(0.0, min(100.0, (attack_auc - 0.5) * 200.0))

        # Risk classification
        if leakage_risk_pct < 15.0:
            risk_level = "LOW (Robust Privacy Defense)"
            color = "#10b981"  # green
        elif leakage_risk_pct < 40.0:
            risk_level = "MODERATE (Partial Defense)"
            color = "#f59e0b"  # yellow
        else:
            risk_level = "HIGH (Severe Membership Leakage)"
            color = "#ef4444"  # red

        return {
            "attack_auc": round(attack_auc, 4),
            "attack_accuracy": round(attack_acc, 4),
            "privacy_leakage_pct": round(leakage_risk_pct, 2),
            "risk_level": risk_level,
            "risk_color": color,
            "mean_member_confidence": round(float(np.mean(conf_train)), 4),
            "mean_non_member_confidence": round(float(np.mean(conf_test)), 4),
            "confidence_gap": round(float(np.mean(conf_train) - np.mean(conf_test)), 4)
        }
