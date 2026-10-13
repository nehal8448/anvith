"""
FastAPI Server for EthicPrivAI Framework
=========================================
Exposes RESTful endpoints for Differential Privacy simulation,
k-anonymity anonymization, secure mining (DP k-means, DP rules),
multi-model training arena, MIA privacy leakage audit, and compliance certification.
"""

import io
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ethicprivai.datasets.loader import BenchmarkDatasets
from ethicprivai.privacy.differential_privacy import (
    LaplaceMechanism,
    GaussianMechanism,
    RandomizedResponse,
    PrivacyBudgetTracker,
    DifferentialPrivacyPerturber,
    DPLogisticRegression,
)
from ethicprivai.privacy.anonymization import AnonymizationEngine
from ethicprivai.privacy.mining import DPKMeans, DPAssociationRuleMiner
from ethicprivai.privacy.attacks import MembershipInferenceAttack
from ethicprivai.ethics.fairness_metrics import FairnessAudit
from ethicprivai.ethics.bias_mitigation import FairReweighing, FairThresholdOptimizer
from ethicprivai.ethics.explainability import ModelExplainer
from ethicprivai.audit.compliance import EthicalAICertifier

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

app = FastAPI(
    title="EthicPrivAI API",
    description="Privacy-Preserving Data Mining & Ethical AI Backend Engine",
    version="1.0.0"
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache for datasets and budget tracker
datasets_cache: Dict[str, Tuple[pd.DataFrame, Dict[str, Any]]] = {}
budget_tracker = PrivacyBudgetTracker(total_epsilon=10.0, total_delta=1e-4)

# Initialize standard benchmark datasets
_adult_df, _adult_meta = BenchmarkDatasets.load_adult_census()
_health_df, _health_meta = BenchmarkDatasets.load_healthcare()
_credit_df, _credit_meta = BenchmarkDatasets.load_credit_risk()
datasets_cache["adult"] = (_adult_df, _adult_meta)
datasets_cache["healthcare"] = (_health_df, _health_meta)
datasets_cache["credit"] = (_credit_df, _credit_meta)


# Request schemas
class SimulateMechanismRequest(BaseModel):
    mechanism: str = "laplace"  # "laplace" or "gaussian"
    epsilon: float = 1.0
    delta: float = 1e-5
    sensitivity: float = 1.0


class PerturbRequest(BaseModel):
    dataset_id: str = "adult"
    epsilon: float = 1.0
    delta: float = 1e-5
    mechanism: str = "laplace"


class AnonymizeRequest(BaseModel):
    dataset_id: str = "adult"
    target_k: int = 5
    quasi_identifiers: Optional[List[str]] = None


class DPKMeansRequest(BaseModel):
    dataset_id: str = "adult"
    n_clusters: int = 3
    epsilon: float = 1.0
    features: Optional[List[str]] = None


class DPRulesRequest(BaseModel):
    dataset_id: str = "adult"
    epsilon: float = 1.0
    min_support: float = 0.05
    min_confidence: float = 0.2


class TrainArenaRequest(BaseModel):
    dataset_id: str = "adult"
    epsilon: float = 1.0
    test_size: float = 0.3
    mitigate_bias: bool = True
    seed: int = 42


class TradeoffRequest(BaseModel):
    dataset_id: str = "adult"
    epsilon_values: List[float] = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    seed: int = 42


@app.get("/api/health")
def get_health():
    return {"status": "ok", "service": "EthicPrivAI Framework", "version": "1.0.0"}


@app.get("/api/datasets")
def list_datasets():
    """List available benchmark datasets."""
    res = []
    for d_id, (df, meta) in datasets_cache.items():
        res.append({
            "id": d_id,
            "name": meta["name"],
            "description": meta["description"],
            "rows": len(df),
            "columns": list(df.columns),
            "target_column": meta["target_column"],
            "sensitive_attribute": meta["sensitive_attribute"],
            "quasi_identifiers": meta.get("quasi_identifiers", []),
            "numeric_columns": meta.get("numeric_columns", []),
            "positive_label_rate": meta.get("positive_label_rate", 0.0)
        })
    return res


@app.get("/api/datasets/{dataset_id}")
def get_dataset_details(dataset_id: str, limit: int = 50):
    """Retrieve sample rows and column profiles for a dataset."""
    if dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[dataset_id]
    sample_rows = df.head(limit).to_dict(orient="records")

    # Column statistics
    stats = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            stats[col] = {
                "type": "numeric",
                "mean": round(float(df[col].mean()), 2),
                "std": round(float(df[col].std()), 2),
                "min": round(float(df[col].min()), 2),
                "max": round(float(df[col].max()), 2)
            }
        else:
            stats[col] = {
                "type": "categorical",
                "unique_count": int(df[col].nunique()),
                "top_values": list(df[col].value_counts().head(3).index)
            }

    return {
        "metadata": meta,
        "total_records": len(df),
        "columns": list(df.columns),
        "statistics": stats,
        "sample": sample_rows
    }


@app.post("/api/privacy/mechanisms/simulate")
def simulate_mechanism(req: SimulateMechanismRequest):
    """
    Simulates noise distribution (PDF) and sample perturbation for interactive visualization.
    """
    x_range = np.linspace(-5.0 * (req.sensitivity / req.epsilon), 5.0 * (req.sensitivity / req.epsilon), 100)
    
    if req.mechanism.lower() == "gaussian":
        mech = GaussianMechanism(epsilon=req.epsilon, delta=req.delta, sensitivity=req.sensitivity)
        pdf_vals = mech.pdf(x_range)
        scale_param = mech.sigma
    else:
        mech = LaplaceMechanism(epsilon=req.epsilon, sensitivity=req.sensitivity)
        pdf_vals = mech.pdf(x_range)
        scale_param = mech.scale

    samples = mech.sample_noise(size=1000).tolist()

    points = [{"x": round(float(x), 3), "density": round(float(y), 5)} for x, y in zip(x_range, pdf_vals)]

    return {
        "mechanism": req.mechanism,
        "epsilon": req.epsilon,
        "delta": req.delta,
        "sensitivity": req.sensitivity,
        "scale_parameter": round(float(scale_param), 4),
        "pdf_curve": points,
        "sample_quantiles": {
            "p5": round(float(np.percentile(samples, 5)), 3),
            "p25": round(float(np.percentile(samples, 25)), 3),
            "median": round(float(np.median(samples)), 3),
            "p75": round(float(np.percentile(samples, 75)), 3),
            "p95": round(float(np.percentile(samples, 95)), 3)
        }
    }


@app.post("/api/privacy/perturb")
def perturb_dataset(req: PerturbRequest):
    """Applies Differential Privacy noise to the selected dataset."""
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    perturber = DifferentialPrivacyPerturber(
        epsilon=req.epsilon,
        delta=req.delta,
        mechanism=req.mechanism
    )
    noisy_df, p_meta = perturber.perturb_dataframe(df, numeric_columns=meta.get("numeric_columns"))

    # Log budget
    try:
        spend_rec = budget_tracker.spend(req.epsilon, req.delta, tag=f"DP Perturb {req.dataset_id}")
    except ValueError as e:
        spend_rec = {"error": str(e)}

    # Comparison preview for first 10 rows
    preview = []
    num_cols = meta.get("numeric_columns", [])[:3]
    for i in range(min(10, len(df))):
        orig_row = {c: round(float(df[c].iloc[i]), 2) for c in num_cols}
        noisy_row = {c: round(float(noisy_df[c].iloc[i]), 2) for c in num_cols}
        preview.append({"index": i, "original": orig_row, "noisy": noisy_row})

    return {
        "perturbation_meta": p_meta,
        "budget_status": budget_tracker.get_status(),
        "preview_comparison": preview
    }


@app.post("/api/privacy/anonymize")
def run_anonymization(req: AnonymizeRequest):
    """Runs k-Anonymity and l-Diversity on dataset."""
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    qis = req.quasi_identifiers or meta.get("quasi_identifiers", ["age"])
    sensitive_col = meta.get("sensitive_attribute", list(df.columns)[0])

    before_stats = AnonymizationEngine.evaluate_k_anonymity(df, qis)
    anon_df, after_stats = AnonymizationEngine.apply_k_anonymity(df, qis, target_k=req.target_k)
    l_div = AnonymizationEngine.evaluate_l_diversity(df, qis, sensitive_col)

    sample_preview = anon_df.head(15).to_dict(orient="records")

    return {
        "before_anonymization": before_stats,
        "after_anonymization": after_stats,
        "l_diversity": l_div,
        "sample_preview": sample_preview
    }


@app.post("/api/privacy/budget/status")
def get_budget_status():
    return budget_tracker.get_status()


@app.post("/api/privacy/budget/reset")
def reset_budget():
    budget_tracker.reset()
    return budget_tracker.get_status()


@app.post("/api/mining/dp-clustering")
def run_dp_clustering(req: DPKMeansRequest):
    """Runs Differentially Private k-Means clustering."""
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    feature_cols = req.features or meta.get("numeric_columns", [])[:2]
    X = df[feature_cols].values

    # Train Standard baseline KMeans for comparison
    from sklearn.cluster import KMeans
    std_kmeans = KMeans(n_clusters=req.n_clusters, random_state=42, n_init=5).fit(X)

    # Train DP KMeans
    dp_kmeans = DPKMeans(n_clusters=req.n_clusters, epsilon=req.epsilon, max_iter=8)
    dp_kmeans.fit(X)

    # Cluster centers
    clusters_info = []
    for k in range(req.n_clusters):
        clusters_info.append({
            "cluster_id": k,
            "standard_center": [round(float(v), 2) for v in std_kmeans.cluster_centers_[k]],
            "dp_noisy_center": [round(float(v), 2) for v in dp_kmeans.cluster_centers_[k]],
            "sample_count": int(np.sum(dp_kmeans.labels_ == k))
        })

    return {
        "features": feature_cols,
        "n_clusters": req.n_clusters,
        "epsilon": req.epsilon,
        "standard_inertia": round(float(std_kmeans.inertia_), 2),
        "dp_inertia": round(float(dp_kmeans.inertia_), 2),
        "clusters": clusters_info
    }


@app.post("/api/mining/dp-rules")
def run_dp_rules(req: DPRulesRequest):
    """Mines Differentially Private Frequent Itemsets & Association Rules."""
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    miner = DPAssociationRuleMiner(
        epsilon=req.epsilon,
        min_support=req.min_support,
        min_confidence=req.min_confidence
    )
    # Discretize continuous columns for association mining
    df_disc = df.copy()
    for col in meta.get("numeric_columns", []):
        df_disc[col] = pd.cut(df_disc[col], bins=3, labels=["Low", "Medium", "High"]).astype(str)

    transactions = miner.extract_transactions(df_disc)
    results = miner.mine_rules(transactions)
    return results


@app.post("/api/train-models")
def train_model_arena(req: TrainArenaRequest):
    """
    Trains and compares 4 configurations side-by-side:
    1. Baseline (Unconstrained, No DP, No Fairness)
    2. DP-Only (Differentially Private, No Fairness)
    3. Fair-Only (Fair Reweighed, No DP)
    4. EthicPrivAI (Fair Reweighed + Differentially Private)
    """
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    target_col = meta["target_column"]
    sensitive_attr = meta["sensitive_attribute"]
    features = [c for c in df.columns if c != target_col]

    X = df[features].values
    y = df[target_col].values
    prot = df[sensitive_attr].values

    X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
        X, y, prot, test_size=req.test_size, random_state=req.seed
    )

    # Compute fair reweighing weights
    fair_weights = FairReweighing.compute_weights(
        p_train, y_train,
        privileged_val=meta["privileged_group"],
        unprivileged_val=meta["unprivileged_group"]
    )

    models_results = {}

    configs = [
        ("baseline", "Baseline AI", False, False),
        ("dp_only", f"DP Only (eps={req.epsilon})", True, False),
        ("fair_only", "Fair AI (Reweighed)", False, True),
        ("ethicprivai", f"EthicPrivAI (Fair + DP eps={req.epsilon})", True, True)
    ]

    for key, label, use_dp, use_fair in configs:
        if use_dp:
            clf = DPLogisticRegression(epsilon=req.epsilon, max_iter=200)
            clf.fit(X_train, y_train, sample_weight=fair_weights if use_fair else None)
        else:
            clf = LogisticRegression(max_iter=300, random_state=req.seed)
            clf.fit(X_train, y_train, sample_weight=fair_weights if use_fair else None)

        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        try:
            auc = float(roc_auc_score(y_test, y_proba))
        except Exception:
            auc = 0.5

        # Fairness Audit
        fairness = FairnessAudit.audit(
            y_true=y_test,
            y_pred=y_pred,
            protected_attr=p_test,
            privileged_val=meta["privileged_group"],
            unprivileged_val=meta["unprivileged_group"]
        )

        # Empirical Privacy (MIA)
        mia = MembershipInferenceAttack.evaluate(
            model=clf,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test
        )

        # Explainability
        if hasattr(clf, "weights") and clf.weights is not None:
            w = clf.weights
            b = clf.bias
        else:
            w = clf.coef_[0]
            b = clf.intercept_[0]
        expl = ModelExplainer.explain_global(features, w, b)

        # Compliance Certificate
        privacy_met = {"epsilon": req.epsilon if use_dp else 999.0, "privacy_leakage_pct": mia["privacy_leakage_pct"]}
        utility_met = {"accuracy": acc, "roc_auc": auc}
        cert = EthicalAICertifier.audit_system(privacy_met, fairness, utility_met, model_name=label)

        models_results[key] = {
            "name": label,
            "use_dp": use_dp,
            "use_fair": use_fair,
            "accuracy": round(acc, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "fairness": fairness,
            "privacy_mia": mia,
            "explainability": expl,
            "certification": cert
        }

    return {
        "dataset": meta["name"],
        "target": target_col,
        "sensitive_attribute": sensitive_attr,
        "models": models_results
    }


@app.post("/api/tradeoff-analysis")
def evaluate_tradeoff_frontier(req: TradeoffRequest):
    """
    Computes Pareto Frontier curve across varying epsilon values:
    Accuracy vs Membership Inference Leakage vs Disparate Impact.
    """
    if req.dataset_id not in datasets_cache:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    df, meta = datasets_cache[req.dataset_id]

    target_col = meta["target_column"]
    sensitive_attr = meta["sensitive_attribute"]
    features = [c for c in df.columns if c != target_col]

    X = df[features].values
    y = df[target_col].values
    prot = df[sensitive_attr].values

    X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
        X, y, prot, test_size=0.3, random_state=req.seed
    )

    weights = FairReweighing.compute_weights(
        p_train, y_train,
        privileged_val=meta["privileged_group"],
        unprivileged_val=meta["unprivileged_group"]
    )

    frontier_points = []

    for eps in req.epsilon_values:
        clf = DPLogisticRegression(epsilon=eps, max_iter=150)
        clf.fit(X_train, y_train, sample_weight=weights)

        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        try:
            auc = float(roc_auc_score(y_test, y_proba))
        except Exception:
            auc = 0.5

        fairness = FairnessAudit.audit(
            y_true=y_test,
            y_pred=y_pred,
            protected_attr=p_test,
            privileged_val=meta["privileged_group"],
            unprivileged_val=meta["unprivileged_group"]
        )

        mia = MembershipInferenceAttack.evaluate(clf, X_train, y_train, X_test, y_test)

        frontier_points.append({
            "epsilon": eps,
            "accuracy": round(acc * 100, 2),
            "roc_auc": round(auc, 4),
            "privacy_leakage_pct": mia["privacy_leakage_pct"],
            "attack_auc": mia["attack_auc"],
            "disparate_impact": fairness["disparate_impact_ratio"],
            "demographic_parity_diff": fairness["demographic_parity_diff"],
            "fairness_score": fairness["fairness_score_pct"]
        })

    return {
        "dataset_name": meta["name"],
        "frontier": frontier_points
    }


@app.post("/api/upload")
async def upload_custom_dataset(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    sensitive_attribute: str = Form(...),
    privileged_group: str = Form("1"),
    unprivileged_group: str = Form("0")
):
    """Allows uploading custom CSV datasets with user-specified target and sensitive attribute."""
    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{target_column}' not found.")
    if sensitive_attribute not in df.columns:
        raise HTTPException(status_code=400, detail=f"Sensitive attribute '{sensitive_attribute}' not found.")

    dataset_id = f"custom_{file.filename.split('.')[0]}"
    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    if target_column in numeric_cols:
        numeric_cols.remove(target_column)

    meta = {
        "name": f"Custom: {file.filename}",
        "description": "User-uploaded dataset for custom ethical AI and privacy audit.",
        "target_column": target_column,
        "sensitive_attribute": sensitive_attribute,
        "privileged_group": privileged_group,
        "unprivileged_group": unprivileged_group,
        "quasi_identifiers": numeric_cols[:3],
        "numeric_columns": numeric_cols,
        "sample_count": len(df),
        "positive_label_rate": round(float(df[target_column].mean()), 3) if pd.api.types.is_numeric_dtype(df[target_column]) else 0.5
    }

    datasets_cache[dataset_id] = (df, meta)

    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": list(df.columns)
    }
