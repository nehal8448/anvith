"""
Comprehensive Test Suite for EthicPrivAI
=========================================
Tests Differential Privacy noise calibration, budget composition,
k-anonymity checks, fairness audits, and bias mitigation algorithms.
"""

import unittest
import numpy as np
import pandas as pd
from ethicprivai.privacy.differential_privacy import (
    LaplaceMechanism,
    GaussianMechanism,
    RandomizedResponse,
    PrivacyBudgetTracker,
    DPLogisticRegression
)
from ethicprivai.privacy.anonymization import AnonymizationEngine
from ethicprivai.privacy.attacks import MembershipInferenceAttack
from ethicprivai.ethics.fairness_metrics import FairnessAudit
from ethicprivai.ethics.bias_mitigation import FairReweighing
from ethicprivai.datasets.loader import BenchmarkDatasets


class TestEthicPrivAI(unittest.TestCase):

    def test_laplace_mechanism_scale(self):
        mech = LaplaceMechanism(epsilon=1.0, sensitivity=2.0)
        self.assertAlmostEqual(mech.scale, 2.0)
        samples = mech.sample_noise(size=100)
        self.assertEqual(len(samples), 100)

    def test_gaussian_mechanism(self):
        mech = GaussianMechanism(epsilon=1.0, delta=1e-5, sensitivity=1.0)
        self.assertGreater(mech.sigma, 0.0)
        val = 10.0
        noisy = mech.perturb(val)
        self.assertIsInstance(noisy, float)

    def test_randomized_response(self):
        rr = RandomizedResponse(epsilon=2.0)
        self.assertGreater(rr.p, 0.5)
        # Test unbiased estimator on 1000 simulated true bits
        true_bits = np.ones(1000, dtype=int)
        noisy_bits = rr.perturb_binary(true_bits)
        est = rr.estimate_true_proportion(noisy_bits)
        self.assertGreater(est, 0.7)  # should estimate high probability

    def test_privacy_budget_tracker(self):
        tracker = PrivacyBudgetTracker(total_epsilon=5.0)
        self.assertTrue(tracker.can_spend(2.0))
        rec = tracker.spend(2.0, tag="Test Query 1")
        self.assertEqual(rec["remaining_epsilon"], 3.0)
        self.assertFalse(tracker.can_spend(4.0))

    def test_fairness_audit(self):
        y_true = np.array([1, 1, 0, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 1, 0, 0, 0, 0, 1, 0])
        prot =   np.array([1, 1, 1, 1, 0, 0, 0, 0])
        audit = FairnessAudit.audit(y_true, y_pred, prot, privileged_val=1, unprivileged_val=0)
        self.assertIn("disparate_impact_ratio", audit)
        self.assertIn("demographic_parity_diff", audit)
        self.assertIn("fairness_score_pct", audit)

    def test_fair_reweighing(self):
        prot = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        y =    np.array([1, 1, 1, 0, 0, 0, 1, 0])
        weights = FairReweighing.compute_weights(prot, y, privileged_val=1, unprivileged_val=0)
        self.assertEqual(len(weights), len(y))
        self.assertAlmostEqual(float(np.mean(weights)), 1.0, places=4)

    def test_k_anonymity(self):
        df = pd.DataFrame({
            "age": [25, 25, 30, 30, 45],
            "gender": ["M", "M", "F", "F", "M"],
            "disease": ["Flu", "Cold", "Flu", "Flu", "Cancer"]
        })
        stats = AnonymizationEngine.evaluate_k_anonymity(df, ["age", "gender"])
        self.assertEqual(stats["current_k"], 1)  # age 45 is singleton

    def test_dp_logistic_regression(self):
        X = np.random.randn(200, 3)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        model = DPLogisticRegression(epsilon=2.0, max_iter=50)
        model.fit(X, y)
        preds = model.predict(X)
        self.assertEqual(len(preds), 200)
        self.assertTrue(set(preds).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
