"""
Privacy-Preserving Data Mining (PPDM) Algorithms
=================================================
Includes Differentially Private k-Means Clustering and
Differentially Private Frequent Itemset & Association Rule Mining.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Set


class DPKMeans:
    """
    Differentially Private k-Means Clustering with noisy centroid updates.
    Enforces privacy by splitting total epsilon across iterations and dimensions.
    """
    def __init__(
        self,
        n_clusters: int = 3,
        epsilon: float = 1.0,
        max_iter: int = 10,
        bounds: Optional[Tuple[float, float]] = None
    ):
        self.n_clusters = int(n_clusters)
        self.epsilon = float(epsilon)
        self.max_iter = int(max_iter)
        self.bounds = bounds  # (min_val, max_val) to bound coordinate sensitivity
        self.cluster_centers_: Optional[np.ndarray] = None
        self.labels_: Optional[np.ndarray] = None
        self.inertia_: float = 0.0

    def fit(self, X: np.ndarray) -> "DPKMeans":
        X = np.asarray(X, dtype=float)
        n_samples, n_features = X.shape

        # Bound coordinates to clip sensitivity
        if self.bounds is not None:
            min_val, max_val = self.bounds
        else:
            min_val = float(np.percentile(X, 1))
            max_val = float(np.percentile(X, 99))
        X_clipped = np.clip(X, min_val, max_val)
        coord_range = max(1e-3, max_val - min_val)

        # Initialize centroids randomly within bounds
        np.random.seed(42)
        idx = np.random.choice(n_samples, self.n_clusters, replace=False)
        centroids = X_clipped[idx].copy()

        # Epsilon budget per iteration: split between sum perturbation and count perturbation
        eps_per_iter = self.epsilon / self.max_iter
        eps_sum = eps_per_iter * 0.7 / n_features
        eps_count = eps_per_iter * 0.3

        labels = np.zeros(n_samples, dtype=int)

        for _ in range(self.max_iter):
            # Step 1: Assign clusters
            dists = np.linalg.norm(X_clipped[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
            labels = np.argmin(dists, axis=1)

            # Step 2: Compute noisy centroids
            new_centroids = np.zeros_like(centroids)
            for k in range(self.n_clusters):
                mask = (labels == k)
                pts = X_clipped[mask]
                true_count = len(pts)

                # Laplace noise for count (sensitivity = 1)
                noisy_count = true_count + np.random.laplace(0.0, 1.0 / eps_count)
                noisy_count = max(1.0, noisy_count)

                # Laplace noise for coordinate sum (sensitivity = coord_range)
                if true_count > 0:
                    true_sum = np.sum(pts, axis=0)
                else:
                    true_sum = centroids[k] * 1.0
                noise_sum = np.random.laplace(0.0, coord_range / eps_sum, size=n_features)
                noisy_sum = true_sum + noise_sum

                new_centroids[k] = np.clip(noisy_sum / noisy_count, min_val, max_val)

            centroids = new_centroids

        self.cluster_centers_ = centroids
        self.labels_ = labels

        # Compute inertia
        dists = np.linalg.norm(X_clipped - centroids[labels], axis=1)
        self.inertia_ = float(np.sum(dists ** 2))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.cluster_centers_ is None:
            raise ValueError("DPKMeans model is not fitted yet.")
        X = np.asarray(X, dtype=float)
        dists = np.linalg.norm(X[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :], axis=2)
        return np.argmin(dists, axis=1)


class DPAssociationRuleMiner:
    """
    Privacy-Preserving Frequent Itemset & Association Rule Mining with Differential Privacy.
    Adds Laplace perturbation to itemset supports to protect individual presence in transactions.
    """
    def __init__(self, epsilon: float = 1.0, min_support: float = 0.05, min_confidence: float = 0.2):
        self.epsilon = float(epsilon)
        self.min_support = float(min_support)
        self.min_confidence = float(min_confidence)

    def extract_transactions(self, df: pd.DataFrame, categorical_cols: Optional[List[str]] = None) -> List[Set[str]]:
        """Converts dataframe rows into transaction itemsets e.g. {age=30-39, sex=Female, income=>50K}."""
        if categorical_cols is None:
            categorical_cols = list(df.columns)
        transactions = []
        for _, row in df[categorical_cols].iterrows():
            itemset = {f"{col}={row[col]}" for col in categorical_cols if pd.notna(row[col])}
            transactions.append(itemset)
        return transactions

    def mine_rules(self, transactions: List[Set[str]]) -> Dict[str, Any]:
        """
        Mines frequent itemsets with Laplace noise and derives association rules:
        Rule: Antecedent -> Consequent [Support, Confidence, Lift]
        """
        n_trans = len(transactions)
        if n_trans == 0:
            return {"rules": [], "frequent_itemsets": []}

        # Sensitivity of counting query is 1 transaction
        noise_scale = 1.0 / self.epsilon

        # 1-itemset frequencies
        item_counts: Dict[str, int] = {}
        for t in transactions:
            for item in t:
                item_counts[item] = item_counts.get(item, 0) + 1

        frequent_1: Dict[str, float] = {}
        for item, count in item_counts.items():
            # Add DP Laplace noise
            noisy_count = max(0.0, count + np.random.laplace(0.0, noise_scale))
            noisy_sup = noisy_count / n_trans
            if noisy_sup >= self.min_support:
                frequent_1[item] = noisy_sup

        # 2-itemsets
        pair_counts: Dict[Tuple[str, str], int] = {}
        items_list = list(frequent_1.keys())
        for t in transactions:
            t_items = [i for i in items_list if i in t]
            for i in range(len(t_items)):
                for j in range(i + 1, len(t_items)):
                    pair = (t_items[i], t_items[j])
                    pair_counts[pair] = pair_counts.get(pair, 0) + 1

        frequent_2: Dict[Tuple[str, str], float] = {}
        for pair, count in pair_counts.items():
            noisy_count = max(0.0, count + np.random.laplace(0.0, noise_scale))
            noisy_sup = noisy_count / n_trans
            if noisy_sup >= self.min_support:
                frequent_2[pair] = noisy_sup

        # Generate rules
        rules = []
        for (item_a, item_b), pair_sup in frequent_2.items():
            sup_a = frequent_1.get(item_a, 0.0)
            sup_b = frequent_1.get(item_b, 0.0)

            # Rule: A -> B
            if sup_a > 0:
                conf_ab = min(1.0, pair_sup / sup_a)
                lift_ab = conf_ab / sup_b if sup_b > 0 else 1.0
                if conf_ab >= self.min_confidence:
                    rules.append({
                        "antecedent": item_a,
                        "consequent": item_b,
                        "support": round(pair_sup, 4),
                        "confidence": round(conf_ab, 4),
                        "lift": round(lift_ab, 3)
                    })

            # Rule: B -> A
            if sup_b > 0:
                conf_ba = min(1.0, pair_sup / sup_b)
                lift_ba = conf_ba / sup_a if sup_a > 0 else 1.0
                if conf_ba >= self.min_confidence:
                    rules.append({
                        "antecedent": item_b,
                        "consequent": item_a,
                        "support": round(pair_sup, 4),
                        "confidence": round(conf_ba, 4),
                        "lift": round(lift_ba, 3)
                    })

        # Sort rules by confidence descending
        rules.sort(key=lambda r: r["confidence"], reverse=True)

        return {
            "epsilon_used": self.epsilon,
            "min_support_threshold": self.min_support,
            "min_confidence_threshold": self.min_confidence,
            "frequent_single_items_count": len(frequent_1),
            "frequent_pairs_count": len(frequent_2),
            "rules_count": len(rules),
            "top_rules": rules[:15]
        }
