"""
Model Explainability & Transparency Engine
===========================================
Provides transparent surrogate attribution, feature importance rankings,
and individual decision explanations to uphold ethical AI transparency principles.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class ModelExplainer:
    """
    Computes global and local model transparency attributions.
    """

    @staticmethod
    def explain_global(
        feature_names: List[str],
        weights: np.ndarray,
        bias: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates global feature importance and directional influence (positive/negative).
        """
        w = np.asarray(weights).flatten()
        abs_w = np.abs(w)
        total_imp = np.sum(abs_w) if np.sum(abs_w) > 0 else 1.0
        normalized_imp = abs_w / total_imp

        features_ranked = []
        for name, weight, imp in zip(feature_names, w, normalized_imp):
            features_ranked.append({
                "feature": name,
                "weight": round(float(weight), 4),
                "importance_pct": round(float(imp * 100), 2),
                "influence": "Promotes Positive Class" if weight > 0 else "Demotes Positive Class"
            })

        features_ranked.sort(key=lambda x: x["importance_pct"], reverse=True)

        return {
            "bias_term": round(float(bias), 4),
            "features_ranked": features_ranked,
            "top_drivers": [f["feature"] for f in features_ranked[:3]]
        }

    @staticmethod
    def explain_instance(
        feature_names: List[str],
        instance_values: np.ndarray,
        weights: np.ndarray,
        bias: float = 0.0
    ) -> Dict[str, Any]:
        """
        Explains an individual prediction by decomposing the logit contribution of each feature.
        """
        x = np.asarray(instance_values).flatten()
        w = np.asarray(weights).flatten()
        contributions = x * w

        factors = []
        for name, val, c in zip(feature_names, x, contributions):
            factors.append({
                "feature": name,
                "value": round(float(val), 2),
                "contribution": round(float(c), 4),
                "effect": "Positive Push" if c > 0 else "Negative Push"
            })

        factors.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        logit = float(np.sum(contributions) + bias)
        prob = 1.0 / (1.0 + np.exp(-np.clip(logit, -30, 30)))

        return {
            "prediction_probability": round(float(prob), 4),
            "predicted_class": int(prob >= 0.5),
            "logit": round(logit, 4),
            "feature_contributions": factors
        }
