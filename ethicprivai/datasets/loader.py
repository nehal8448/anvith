"""
Benchmark Datasets Loader & Generator for EthicPrivAI
======================================================
Provides standard ethical AI & privacy benchmark datasets:
1. Adult Census Income (Demographic fairness & income privacy)
2. Healthcare Clinical Outcome (Medical privacy & treatment fairness)
3. Credit Risk Assessment (Financial fairness & privacy)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional


class BenchmarkDatasets:
    """
    Supplies curated realistic datasets designed for privacy-preserving data mining
    and ethical algorithmic fairness benchmarking.
    """

    @staticmethod
    def load_adult_census(n_samples: int = 2000, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Generates Adult Census Income benchmark dataset with realistic demographic correlations,
        quasi-identifiers, sensitive attributes (Sex, Race), and target (High_Income >$50K).
        """
        np.random.seed(seed)
        age = np.random.normal(38.5, 13.0, n_samples).clip(18, 75).astype(int)
        education_num = np.random.choice([9, 10, 12, 13, 14, 16], size=n_samples, p=[0.32, 0.22, 0.15, 0.20, 0.08, 0.03])
        hours_per_week = np.random.normal(40, 10, n_samples).clip(15, 80).astype(int)
        capital_gain = np.random.choice([0, 1000, 3000, 7500, 15000], size=n_samples, p=[0.85, 0.05, 0.04, 0.04, 0.02])
        
        # Sensitive attributes: Sex (0: Female, 1: Male) & Race (0: Minority, 1: Majority)
        sex = np.random.choice([0, 1], size=n_samples, p=[0.33, 0.67])
        race = np.random.choice([0, 1], size=n_samples, p=[0.14, 0.86])

        # Latent logit with systemic demographic wage disparity
        # (reflecting historical bias present in the real Adult Census dataset)
        logit = (
            -5.2
            + 0.045 * (age - 35)
            + 0.28 * (education_num - 10)
            + 0.04 * (hours_per_week - 40)
            + 0.00015 * capital_gain
            + 0.85 * sex      # Historical gender wage disparity
            + 0.45 * race     # Historical racial disparity
            + np.random.normal(0, 0.5, n_samples)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        high_income = (np.random.rand(n_samples) < prob).astype(int)

        df = pd.DataFrame({
            "age": age,
            "education_num": education_num,
            "hours_per_week": hours_per_week,
            "capital_gain": capital_gain,
            "sex": sex,
            "race": race,
            "high_income": high_income
        })

        meta = {
            "name": "Adult Census Income Benchmark",
            "description": "Standard benchmark for differential privacy & algorithmic fairness auditing.",
            "target_column": "high_income",
            "sensitive_attribute": "sex",
            "privileged_group": 1,   # Male
            "unprivileged_group": 0, # Female
            "quasi_identifiers": ["age", "education_num", "hours_per_week"],
            "numeric_columns": ["age", "education_num", "hours_per_week", "capital_gain"],
            "categorical_columns": ["sex", "race"],
            "sample_count": n_samples,
            "positive_label_rate": round(float(np.mean(high_income)), 3)
        }
        return df, meta

    @staticmethod
    def load_healthcare(n_samples: int = 1800, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Generates Healthcare Clinical Patient benchmark for medical privacy & treatment fairness.
        """
        np.random.seed(seed)
        age = np.random.normal(54, 15, n_samples).clip(20, 88).astype(int)
        glucose = np.random.normal(120, 30, n_samples).clip(70, 240).astype(int)
        blood_pressure = np.random.normal(80, 12, n_samples).clip(55, 125).astype(int)
        bmi = np.random.normal(28.5, 6.0, n_samples).clip(18.0, 48.0).round(1)
        prior_visits = np.random.poisson(1.8, n_samples).clip(0, 10)
        gender = np.random.choice([0, 1], size=n_samples, p=[0.52, 0.48]) # 0: Female, 1: Male

        logit = (
            -4.0
            + 0.035 * (age - 50)
            + 0.015 * (glucose - 100)
            + 0.02 * (blood_pressure - 75)
            + 0.04 * (bmi - 25)
            + 0.35 * prior_visits
            - 0.30 * gender # Gender treatment gap
            + np.random.normal(0, 0.4, n_samples)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        readmitted = (np.random.rand(n_samples) < prob).astype(int)

        df = pd.DataFrame({
            "age": age,
            "glucose": glucose,
            "blood_pressure": blood_pressure,
            "bmi": bmi,
            "prior_visits": prior_visits,
            "gender": gender,
            "readmitted": readmitted
        })

        meta = {
            "name": "Healthcare Clinical Risk Benchmark",
            "description": "Evaluates patient data confidentiality and fair clinical outcome predictions.",
            "target_column": "readmitted",
            "sensitive_attribute": "gender",
            "privileged_group": 1,
            "unprivileged_group": 0,
            "quasi_identifiers": ["age", "blood_pressure", "bmi"],
            "numeric_columns": ["age", "glucose", "blood_pressure", "bmi", "prior_visits"],
            "categorical_columns": ["gender"],
            "sample_count": n_samples,
            "positive_label_rate": round(float(np.mean(readmitted)), 3)
        }
        return df, meta

    @staticmethod
    def load_credit_risk(n_samples: int = 1800, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Generates Credit Risk & Loan Approval benchmark for financial privacy and fairness.
        """
        np.random.seed(seed)
        age = np.random.normal(42, 11, n_samples).clip(21, 72).astype(int)
        income_k = np.random.normal(65, 25, n_samples).clip(18, 180).round(1)
        credit_score = np.random.normal(680, 70, n_samples).clip(450, 850).astype(int)
        debt_ratio = np.random.normal(0.32, 0.12, n_samples).clip(0.05, 0.85).round(2)
        gender = np.random.choice([0, 1], size=n_samples, p=[0.45, 0.55])

        logit = (
            -4.5
            + 0.03 * (age - 35)
            + 0.025 * (income_k - 50)
            + 0.012 * (credit_score - 600)
            - 2.5 * (debt_ratio - 0.3)
            + 0.65 * gender # Historical financial credit disparity
            + np.random.normal(0, 0.4, n_samples)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        approved = (np.random.rand(n_samples) < prob).astype(int)

        df = pd.DataFrame({
            "age": age,
            "income_k": income_k,
            "credit_score": credit_score,
            "debt_ratio": debt_ratio,
            "gender": gender,
            "approved": approved
        })

        meta = {
            "name": "Financial Credit Approval Benchmark",
            "description": "Financial ethics, loan approval equity, and differential privacy protection.",
            "target_column": "approved",
            "sensitive_attribute": "gender",
            "privileged_group": 1,
            "unprivileged_group": 0,
            "quasi_identifiers": ["age", "credit_score", "debt_ratio"],
            "numeric_columns": ["age", "income_k", "credit_score", "debt_ratio"],
            "categorical_columns": ["gender"],
            "sample_count": n_samples,
            "positive_label_rate": round(float(np.mean(approved)), 3)
        }
        return df, meta
