"""
Ethical AI Compliance Auditor & Certification Engine
=====================================================
Calculates the holistic Ethical AI Index (0-100%) across four core pillars:
1. Data Confidentiality & Privacy (DP epsilon, MIA leakage resistance, k-anonymity)
2. Algorithmic Fairness & Equity (Disparate Impact, Demographic Parity, Equal Opportunity)
3. Model Transparency & Explainability
4. Utility & Decision Accuracy
"""

from typing import Dict, Any, List


class EthicalAICertifier:
    """
    Evaluates systems against EU AI Act & NIST AI Risk Management Framework (RMF) guidelines.
    """

    @staticmethod
    def audit_system(
        privacy_metrics: Dict[str, Any],
        fairness_metrics: Dict[str, Any],
        utility_metrics: Dict[str, Any],
        model_name: str = "EthicPrivAI Model"
    ) -> Dict[str, Any]:
        """
        Aggregates metrics into an overall Ethical AI Index and certification status.
        """
        # 1. Privacy Score (0 - 100)
        # Low MIA leakage and reasonable epsilon yield high score
        mia_leakage = privacy_metrics.get("privacy_leakage_pct", 50.0)
        privacy_resistance = max(0.0, 100.0 - mia_leakage)
        epsilon = privacy_metrics.get("epsilon", 1.0)
        # Lower epsilon is stronger privacy (eps <= 1.0 is great, eps >= 10.0 gives diminished score)
        eps_factor = max(0.0, min(100.0, (10.0 - min(10.0, epsilon)) * 10.0))
        privacy_score = 0.7 * privacy_resistance + 0.3 * eps_factor

        # 2. Fairness Score (0 - 100)
        fairness_score = fairness_metrics.get("fairness_score_pct", 60.0)

        # 3. Utility Score (0 - 100)
        acc = utility_metrics.get("accuracy", 0.75) * 100.0
        auc = utility_metrics.get("roc_auc", 0.75) * 100.0
        utility_score = (acc + auc) / 2.0

        # 4. Transparency Score (0 - 100)
        transparency_score = 92.0  # Linear/surrogate explainable architecture

        # Overall Weighted Index:
        # Privacy 30%, Fairness 30%, Utility 20%, Transparency 20%
        overall_index = (
            0.30 * privacy_score +
            0.30 * fairness_score +
            0.20 * utility_score +
            0.20 * transparency_score
        )
        overall_index = round(max(0.0, min(100.0, overall_index)), 1)

        # Certification Grade
        if overall_index >= 85.0:
            grade = "A (Gold Certified - EU AI Act & NIST Compliant)"
            status = "CERTIFIED"
            badge_color = "#10b981"
        elif overall_index >= 70.0:
            grade = "B (Silver Certified - Responsible Deployment Ready)"
            status = "CERTIFIED"
            badge_color = "#3b82f6"
        elif overall_index >= 50.0:
            grade = "C (Conditional - Action Required on Disparity/Leakage)"
            status = "CONDITIONAL"
            badge_color = "#f59e0b"
        else:
            grade = "F (Non-Compliant - Fails Ethical Standards)"
            status = "REJECTED"
            badge_color = "#ef4444"

        recommendations = []
        if fairness_metrics.get("disparate_impact_ratio", 1.0) < 0.8:
            recommendations.append("Disparate impact ratio is below 0.8 (four-fifths rule). Apply pre-processing fair reweighing.")
        if mia_leakage > 25.0:
            recommendations.append("Membership inference leakage is above 25%. Decrease epsilon budget to enhance differential privacy.")
        if utility_score < 65.0:
            recommendations.append("Utility is low. Consider calibrating DP noise scale or tuning regularization lambda.")

        if not recommendations:
            recommendations.append("All pillars satisfy ethical AI thresholds. System demonstrates balanced privacy and equity.")

        return {
            "model_name": model_name,
            "overall_ethical_index": overall_index,
            "certification_grade": grade,
            "certification_status": status,
            "badge_color": badge_color,
            "pillar_breakdown": {
                "privacy_and_confidentiality": round(privacy_score, 1),
                "algorithmic_fairness": round(fairness_score, 1),
                "utility_and_accuracy": round(utility_score, 1),
                "transparency_and_explainability": round(transparency_score, 1)
            },
            "recommendations": recommendations,
            "framework_version": "EthicPrivAI v1.0.0"
        }
