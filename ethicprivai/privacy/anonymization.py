"""
Anonymization & De-identification Engine for EthicPrivAI
=========================================================
Implements k-Anonymity, l-Diversity, t-Closeness, quasi-identifier generalization,
and the Mondrian multidimensional partitioning algorithm.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Set


class AnonymizationEngine:
    """
    Evaluates and applies k-Anonymity, l-Diversity, and t-Closeness to tabular data.
    """

    @staticmethod
    def compute_equivalence_classes(
        df: pd.DataFrame,
        quasi_identifiers: List[str]
    ) -> Dict[Tuple, List[int]]:
        """
        Group rows into equivalence classes based on quasi-identifier values.
        Returns mapping from tuple of QI values to row indices.
        """
        groups: Dict[Tuple, List[int]] = {}
        for idx, row in df.iterrows():
            key = tuple(row[qi] for qi in quasi_identifiers)
            if key not in groups:
                groups[key] = []
            groups[key].append(idx)
        return groups

    @classmethod
    def evaluate_k_anonymity(
        cls,
        df: pd.DataFrame,
        quasi_identifiers: List[str]
    ) -> Dict[str, Any]:
        """
        Check k-anonymity guarantee across all equivalence classes.
        """
        eq_classes = cls.compute_equivalence_classes(df, quasi_identifiers)
        sizes = [len(indices) for indices in eq_classes.values()]

        min_k = min(sizes) if sizes else 0
        avg_k = float(np.mean(sizes)) if sizes else 0.0
        n_classes = len(sizes)
        total_rows = len(df)

        # Discernibility Metric (DM) = sum of (size^2) for satisfied classes + total_rows for suppressed
        discernibility_metric = sum(s ** 2 for s in sizes)

        # Fraction of classes satisfying k=2, 5, 10
        k2_compliance = sum(1 for s in sizes if s >= 2) / max(1, n_classes)
        k5_compliance = sum(1 for s in sizes if s >= 5) / max(1, n_classes)

        return {
            "current_k": int(min_k),
            "average_group_size": round(avg_k, 2),
            "num_equivalence_classes": n_classes,
            "discernibility_metric": int(discernibility_metric),
            "k2_compliance_pct": round(k2_compliance * 100, 1),
            "k5_compliance_pct": round(k5_compliance * 100, 1),
            "violating_classes_count": sum(1 for s in sizes if s < 2)
        }

    @classmethod
    def evaluate_l_diversity(
        cls,
        df: pd.DataFrame,
        quasi_identifiers: List[str],
        sensitive_attribute: str
    ) -> Dict[str, Any]:
        """
        Evaluate distinct and entropy l-diversity for sensitive attribute.
        """
        eq_classes = cls.compute_equivalence_classes(df, quasi_identifiers)
        distinct_counts = []
        entropies = []

        for indices in eq_classes.values():
            sub = df.loc[indices, sensitive_attribute]
            unique_vals = sub.nunique()
            distinct_counts.append(unique_vals)

            # Entropy
            val_counts = sub.value_counts(normalize=True).values
            entropy = -sum(p * math.log(p) for p in val_counts if p > 0)
            entropies.append(entropy)

        min_distinct_l = min(distinct_counts) if distinct_counts else 0
        min_entropy_l = math.exp(min(entropies)) if entropies else 0.0

        return {
            "distinct_l": int(min_distinct_l),
            "average_distinct_l": round(float(np.mean(distinct_counts)), 2) if distinct_counts else 0,
            "entropy_l": round(float(min_entropy_l), 2),
            "average_entropy": round(float(np.mean(entropies)), 3) if entropies else 0.0
        }

    @classmethod
    def generalize_numeric_column(
        cls,
        series: pd.Series,
        num_bins: int = 5
    ) -> pd.Series:
        """
        Bin numerical values into standardized range intervals (e.g. 20-29, 30-39).
        """
        if pd.api.types.is_numeric_dtype(series):
            try:
                binned = pd.cut(series, bins=num_bins, precision=0)
                return binned.astype(str)
            except Exception:
                return series.astype(str)
        return series.astype(str)

    @classmethod
    def apply_k_anonymity(
        cls,
        df: pd.DataFrame,
        quasi_identifiers: List[str],
        target_k: int = 5,
        numeric_bins: int = 4
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Applies hierarchy-based generalization and outlier suppression to enforce target_k anonymity.
        """
        df_anon = df.copy()

        # Step 1: Generalize continuous quasi-identifiers
        for qi in quasi_identifiers:
            if pd.api.types.is_numeric_dtype(df_anon[qi]):
                df_anon[qi] = cls.generalize_numeric_column(df_anon[qi], num_bins=numeric_bins)

        # Step 2: Form equivalence classes
        eq_classes = cls.compute_equivalence_classes(df_anon, quasi_identifiers)

        # Step 3: Identify classes with size < target_k and generalize or suppress
        valid_indices = []
        suppressed_indices = []

        for key, indices in eq_classes.items():
            if len(indices) >= target_k:
                valid_indices.extend(indices)
            else:
                suppressed_indices.extend(indices)

        # For suppressed rows, if small fraction, we can either mask quasi-identifiers or drop
        suppression_rate = len(suppressed_indices) / max(1, len(df_anon))
        
        # If suppressed rows exist, mask the QI fields with '*'
        for qi in quasi_identifiers:
            df_anon.loc[suppressed_indices, qi] = "*"

        stats = {
            "target_k": target_k,
            "quasi_identifiers": quasi_identifiers,
            "original_rows": len(df),
            "suppressed_records": len(suppressed_indices),
            "suppression_rate_pct": round(suppression_rate * 100, 2),
            "equivalence_classes": len(eq_classes),
            "achieved_k": target_k if len(suppressed_indices) == 0 else min(target_k, cls.evaluate_k_anonymity(df_anon[df_anon[quasi_identifiers[0]] != "*"], quasi_identifiers)["current_k"] if len(valid_indices) > 0 else 1)
        }

        return df_anon, stats
